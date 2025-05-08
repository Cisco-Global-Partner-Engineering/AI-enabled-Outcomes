"""
Copyright (c) 2025 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

__author__ = "Joel Jose <joeljos@cisco.com>"
__copyright__ = "Copyright (c) 2025 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"
"""

import modules.credentials as credentials
import json
import modules.dochat as dochat
import modules.execute_cmd_ubuntu as execute_cmd_ubuntu
import modules.send_router as send_router
import logging
import modules.telemetry as telemetry
from rich import print as print_md
import concurrent.futures
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting the script...")

# Get the script's directory and use it to create absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
l3_topology_path = os.path.join(BASE_DIR, 'data', 'input', 'l3_topology.json')

# Load the network topology and summary
try:
    with open(l3_topology_path, 'r') as f:
        network_topology = json.load(f)
except FileNotFoundError:
    logging.error(f"Could not find topology file at: {l3_topology_path}")
    network_topology = {}
devices = credentials.devices


def generate_insight(device_name, command, result, device_info, dochat, ping_result, response_deviceconnect, network_topology, remediation_results):
    """Generate insights for a single command result from a specific device in a separate thread."""
    # Skip empty results
    if not result:
        return f"Device '{device_name}', Command '{command}' returned no result."
    
    # Skip processing errors or sleep commands
    if isinstance(result, str) and (result.startswith(("ERROR","ERROR:")) or command.startswith("sleep")):
        return f"Device '{device_name}', Command '{command}' resulted in: {result}"
    
    # Messages for insights generation with your detailed prompt
    messages = [
        {
            "role": "system",
            "content": f"""You are a highly experienced Network Insights Analyst. Your objective is to meticulously analyze network device command outputs to identify potential root causes or contributing factors for a specific network alarm.

            **ANALYSIS CONTEXT:**
            * **Alarm Trigger:** '{ping_result}' (Interpret this alarm: what kind of network problem does it usually signify?)
            * **Device Under Investigation:**
                * Name: {device_info.get('name', 'N/A') if isinstance(device_info, dict) else 'N/A'}
                * Type: {device_info.get('type', 'N/A') if isinstance(device_info, dict) else 'N/A'}
            * **Network Context:**
                * Relevant Traffic Path: {response_deviceconnect['traffic-path'] if response_deviceconnect else 'N/A'}
                * Network Topology Snippet: {network_topology if network_topology else 'N/A'}
            * **History:**
                * Previous Remediation Attempt Results: {remediation_results if remediation_results else 'None'}

            **INSTRUCTIONS:**

            Follow these steps to conduct your analysis:

            1.  **Understand the Core Problem:** Based on the 'Alarm Trigger', determine the likely network issue (e.g., connectivity loss, high latency, packet drops, specific service reachability). Keep this specific problem context in mind throughout your analysis.
            2.  **Analyze Command Outputs:** Carefully examine the provided command results for the specified device.
                * **Prioritize Valid Data:** Focus your primary analysis on outputs from commands that executed successfully. Note any commands that failed or were unresponsive, as this *could* be relevant, but don't base your main findings on missing data.
                * **Look for Indicators:** Search for concrete evidence related to the suspected problem (from Step 1). This includes:
                    * **Interface Status:** Up/down status, protocol status, error counters (CRC, input/output errors, drops), discards, duplex/speed mismatches.
                    * **Routing/Forwarding:** Relevant routing table entries (or lack thereof), ARP/MAC table entries, forwarding decisions.
                    * **Configuration:** Misconfigurations, inconsistencies compared to topology or expected state.
                **************** ACL Analysis for IOS START ***************
                * **ACLs Analysis (IOS-specific):**
                    * **ACL Types**: Identify both standard (numbered 1-99, 1300-1999) and extended ACLs (numbered 100-199, 2000-2699) or named ACLs.
                    * **ACL Application**: 
                        * Check which interfaces have ACLs applied and in which direction (in/out).
                        * Verify the ACL is applied to the CORRECT interface and direction based on traffic flow:
                        - "in" filters packets before they enter the interface
                        - "out" filters packets after routing but before they exit the interface
                    * **Rule Processing**: 
                        * All IOS ACLs end with an implicit "deny any" that blocks all traffic not explicitly permitted.
                        * ACLs process from top to bottom (first match wins).
                        * Standard ACLs filter by source IP only, while extended ACLs can filter by source/destination IP, port, and protocol.
                    * **Common Issues**:
                        * Missing or overly restrictive permits for required traffic.
                        * ACL applied to wrong interface or direction.
                        * Standard ACL applied too close to destination (should be close to source).
                        * Established/reflexive ACLs configured incorrectly for return traffic.
                **************** ACL Analysis for IOS END ***************
                **************** ACL Analysis for ASA START ***************
                * **ACLs/Firewall Rules (ASA-specific): **
                    * **Security Level Analysis**: Identify all interfaces with their security levels (0-100). Remember traffic flows freely from high to low security by default, but requires explicit permission from low to high.
                    * **Access Group Application**: 
                        * Check which access-lists are applied to which interfaces and in which direction (in/out).
                        * Verify if access groups are applied to the CORRECT interfaces based on the traffic path.
                        * For inbound traffic (entering an interface), the access-group must be applied with "in" direction.
                        * For outbound traffic (exiting an interface), the access-group must be applied with "out" direction.
                        * If the access-group is not applied explicitly, the default behavior is to deny all traffic from the lower security level to higher security level.
                        * Is there any traffic blocked by the presence or absence of an access-group, due to implicit or explicit denies?
                    * **Rule Analysis**: 
                        * Remember ALL traffic is subject to the implicit "deny any any" at the end of every access-list.
                        * Check for both explicit denies and the absence of necessary permits.
                        * Verify rule ordering - the first matching rule is applied.
                        * Check hit counts if available to see if rules are being triggered.
                    * **NAT Interaction**: 
                        * Verify if NAT rules might be affecting how access control rules are applied.
                        * Remember NAT is applied before access control for incoming traffic and after access control for outgoing traffic.
                    * **Same-Security Traffic**: Check if "same-security-traffic permit inter-interface" is enabled if traffic needs to flow between interfaces with the same security level.
                **************** ACL Analysis for ASA END ***************
                * **Device Health:** High CPU/memory utilization, logs indicating errors (if provided).
                * **Device-Type Specifics:**
                    * **If Layer 2 Switch:** Focus on interface status/errors, VLAN configurations (ensure necessary VLANs exist and are allowed on trunks), spanning-tree status (blocking ports?), MAC address tables. Ignore Layer 3 routing aspects unless it's an L3 switch acting in an L2 role for this path. Ignore management VLANs/interfaces unless directly implicated by the alarm type.
            3.  **Correlate Findings with Context:** How do the specific findings from the command outputs relate to:
                * The 'Alarm Trigger'? (Does an interface drop explain the ping failure?)
                * The device's role in the 'Traffic Path' and 'Network Topology'? (Is the issue on an interface connecting to the next hop or the source/destination segment?)
            4.  **Synthesize Key Issues:** Consolidate your observations. Identify the most significant anomalies, errors, or configuration issues found in the command outputs that have a *plausible link* to the specific 'Alarm Trigger'.

            **OUTPUT REQUIREMENTS:**

            * Provide a **concise summary** of your analysis.
            * Focus *exclusively* on reporting the **key findings, potential issues, and anomalies** identified in the command results that are relevant to the 'Alarm Trigger' and the provided network context.
            * **Do NOT** suggest remediation steps, further diagnostic commands, or speculate beyond the provided data.
            * Be factual and base your summary strictly on the provided command outputs and context.
            """
        },
        {
            "role": "user",
            "content": f"Analyze the following command results for Device '{device_info.get('name', 'N/A') if isinstance(device_info, dict) else 'N/A'}' ({device_info.get('type', 'N/A') if isinstance(device_info, dict) else 'N/A'}):\n\n```\n{command}\n{result}\n```"
        },
    ]
    
    # Insight generation
    #llm="azuregpt41"

    response = dochat.dochat(messages=messages, json=False)
    insights = response.strip()
    print(f"\nInsights for device {device_info['name']} command '{command}': \n\n {insights} \n\n")
    return insights

def process_device(label, device_info, ping_result, response_deviceconnect, remediation_results=None):
    """
    Process a single device: generate commands, execute them, and create insights.
    
    Args:
        label (str): Device label
        device_info (dict): Device information
        ping_result: Results of ping tests
        response_deviceconnect (dict): Traffic path information
        remediation_results: Any previous remediation efforts
        
    Returns:
        dict: Device insights and results
    """
    print(f"Recon module: {label}")
    if device_info is None:
        print(f"Device {label} not found in devices list.")
        return {"device": label, "device_type": "unknown", "insights": "Device not found"}
        
    print(f"Device info: {device_info}")
    
    # Messages for show command generation
    messages = [
    {
        "role": "system",
        "content": f"""You are a network diagnostics expert who generates precise troubleshooting commands based on alarm data and network context.

    Your task is to analyze an alarm on a network device and provide a prioritized, comma-separated list of diagnostic commands that will help identify the root cause.


    DEVICE INFORMATION:
    - Device Name: {device_info.get('name', 'Unknown') if isinstance(device_info, dict) else 'Unknown'}
    - Device Type: {device_info.get('type', 'Unknown') if isinstance(device_info, dict) else 'Unknown'}

    AVAILABLE CONTEXT:
    - Alarm Details: {ping_result if ping_result is not None else 'Not provided'}
    - Traffic Path Information: {response_deviceconnect.get('traffic-path', 'Not available') if isinstance(response_deviceconnect, dict) else 'Not available'}
    - Network Topology : {network_topology if network_topology else 'Not provided'}
    - Previous Remediation Attempt Results: {remediation_results if remediation_results else 'No previous remediation results provided'}

    OUTPUT REQUIREMENTS:
    - Provide ONLY the most critical executable commands as a comma-separated list
    - No explanations, comments, or preambles in your response
    - Commands must be appropriate for the specified device type
    - Focus on revealing current state and connectivity issues
    - Include safety parameters (timeouts, hop limits, etc.) for unbounded commands

   EXAMPLES OF DEVICE-TYPE SPECIFIC COMMANDS:
    For Cisco IOS virtual router devices:
    - Interface status: 'show ip interface brief', 'show interfaces status'
    - Routing: 'show ip route', 'show ip protocols'
    - ACLs: 'show access-lists', 'show ip access-lists', 'show run | include access-list'
    - Logs: 'show logging | last 50'
    - running config: 'show run | include <pattern>' (to filter running config for the items of interest, like access-list, route, etc.)
    For Cisco IOS Layer 2 virtual switches:
    - Interface status: 'show ip interface brief', 'show interfaces status', 'show vlan brief'
    - VLANs: 'show vlan', 'show mac address-table'
    - running config: 'show run | include <pattern>' (to filter running config for the items of interest, like access-list, route, etc.)
    For Cisco ASA virtual devices (highly recommended to run the packet-tracer command for both ingress and egress flows):
    - Interface status: 'show interface ip brief', 'show interface status'
    - Routing: 'show route', 'show route summary'
    - ACLs: 'show access-list', 'show run access-list', 'show run access-group'
    - Logs: 'show logging | grep <pattern>' (last 50 is not a valid option. Instead use grep to filter logs)
    - running config: 'show run | grep <pattern>'(to filter running config for the items of interest, like access-list, route, etc.)
    - traceroute: 'traceroute <dest> ttl <min-ttl> <max-ttl>'(to limit the number of hops)
    - ping: 'ping <dest> repeat <count>' (to limit the number of pings)
    - packet-tracer input {{ifc_name}} icmp  {{ src_ip }} {{icmp_value}} {{ icmp_code }} {{ dst_ip }} detailed (run the packet-tracer command for both ingress and egress interfaces. 'ifc_name' should be the 'nameif' of the respective interface from the 'Network Topology' data.)



    For Linux/Unix virtual hosts:
    - Interface status: 'sudo ip addr', 'sudo ip link'
    - Routing: 'sudo ip route', 'sudo netstat -rn'
    - Firewall: 'sudo iptables -L -n', 'sudo nft list ruleset'
    - Logs: 'tail -n 50 /var/log/syslog'

    For network routers and firewalls, always check:
    1. Interface status related to the alarm path
    2. Routing/forwarding information for affected destinations
    3. Access control lists and groups applied to relevant interfaces
    4. Error counters and traffic statistics
    5. Control plane protocol status
    6. Recent logs related to connectivity issues
    7. Do ping and traceroute tests to the destination IP address to check connectivity


    For Virtual IOS Switches:
    1. Do not include any routing elements as they are not applicable
    2. Focus on interface status, VLAN configurations, and any relevant issues
    3. Do not check any layer 3 elements as they are not applicable
    4. Ignore the management vlan and management interfaces as they are not relevant to the alarm

    COMMAND SAFETY REQUIREMENTS:
    - For traceroute: Include hop limits (e.g., 'traceroute -m 15 <dest>')
    - For ping: Include count limits (e.g., 'ping -c 5 <dest>')
    - For log commands: Include line limits to prevent overwhelming output
    - For all commands: Consider timeout options where available

    Remember: Include ONLY diagnostic commands. Do not generate any commands that would modify device configuration.
    """
        },
        {
            "role": "user", 
            "content": f"Generate critical diagnostic commands for {device_info.get('name', 'this device') if isinstance(device_info, dict) else 'this device'} ({device_info.get('type', 'unknown type') if isinstance(device_info, dict) else 'unknown type'}). Return only a comma-separated list with no other text."
        }
    ]
    
    # Command generation
    #llm="azuregpt41"

    response = dochat.dochat(messages=messages, json=False)
    # Strip the response and remove any unwanted characters
    response = response.split(",")
    response = [command.strip() for command in response if command.strip()]
    print(f"Command List for {label}: {response}")
    command_results = {}
    
    # Execute the correct command based on device type
    if device_info["type"] == "alpine virtual linux":
        command_results = execute_cmd_ubuntu.execute_commands_ssh(
            device_info["ip"],
            device_info["username"],
            device_info["password"],
            commands=response
        )
    else:
        # Use the updated send_router.py functions with the device name
        command_results = send_router.execute_commands_in_parallel(
            [device_info["name"]], response
        )
    
    # Error handling
    if isinstance(command_results, str) and command_results.startswith("ERROR"):
        error_msg = f"Error executing commands on {device_info['name']}: {command_results}"
        print(error_msg)
        return {"device": device_info["name"], "device_type": device_info["type"], "insights": error_msg, "error": True}
    
    if isinstance(command_results, dict) and "setup_error" in command_results:
        error_msg = f"Error executing commands on {device_info['name']}: {command_results['setup_error']}"
        print(error_msg)
        return {"device": device_info["name"], "device_type": device_info["type"], "insights": error_msg, "error": True}
    
    print(f"Command Results for device {device_info['name']} : \n\n {command_results} \n\n")
    
   # Process command results in parallel across all devices and commands
    insight_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(response)) as executor:
        # Create a dictionary of futures to track devices and commands
        future_to_info = {}
        
        # Submit all tasks for parallel execution
        for device_name, device_commands in command_results.items():
            for command, result in device_commands.items():
                future = executor.submit(
                    generate_insight, 
                    device_name, 
                    command, 
                    result,
                    {"name": device_name, "type": device_info["type"] if device_info else "unknown"},  # Enhancing device_info
                    dochat,
                    ping_result,               # Pass the ping result context
                    response_deviceconnect,    # Pass traffic path info
                    network_topology,          # Pass network topology
                    remediation_results        # Pass previous remediation results
                )
                future_to_info[future] = (device_name, command)
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_info):
            device_name, command = future_to_info[future]
            try:
                insight = future.result()
                insight_list.append(insight)
            except Exception as exc:
                print(f"Device '{device_name}', Command '{command}' generated an exception: {exc}")
                insight_list.append(f"Error processing device '{device_name}', command '{command}': {str(exc)}")
    
    messages = [
            {
            "role": "system",
            "content": "You are an expert Network Insight Analyzer. Given a list of insights, your task is to summarize the key findings and clearly highlight any potential issues identified. Make sure to give as much detailed information as possible for all the potential issues identified, so as to derive the remediation steps from the insights."
            },
            {"role": "user", "content": "Insight List: " + str(insight_list)}
        ]
    
    # Generate a summary of the insights
    #llm="azuregpt41"
    insight_summary = dochat.dochat(messages=messages, json=False)
    # Save the results to a file
    command_results_path = os.path.join(BASE_DIR, 'data', 'command_results', f'command_results_{device_info["name"]}.json')
    with open(command_results_path, 'w') as f:
        json.dump(command_results, f, indent=4)
    
    insights_detailed_path = os.path.join(BASE_DIR, 'data', 'insights', 'detailed', f'insights_detailed_{device_info["name"]}.json')
    with open(insights_detailed_path, 'w') as f:
        json.dump(insight_list, f, indent=4)
    
    insights_summary_path = os.path.join(BASE_DIR, 'data', 'insights', 'summary', f'insights_summary_{device_info["name"]}.json')
    with open(insights_summary_path, 'w') as f:
        json.dump(insight_summary, f, indent=4)
    
    return {
        "device": device_info["name"], 
        "device_type": device_info["type"], 
        "insights": insight_summary
    }

# Recon module
def recon(response_deviceconnect, remediation_results=None):
    """
    Reconnaissance module for network devices with parallel processing.
    
    Args:
        response_deviceconnect (dict): Traffic path information
        remediation_results: Previous remediation efforts
        
    Returns:
        tuple: Ping results and list of device insights
    """
    print("Recon module initialized.")
    print("Traffic path:", response_deviceconnect['traffic-path'])
    
    # Get ping results first
    ping_result = telemetry.ping_all()
    #with open("ping_result.json", "r") as f:
    #    ping_result = f.read()
    
    # Process devices in parallel
    insights_list = []
    device_tasks = []
    
    # Prepare the device processing tasks
    for label in response_deviceconnect['traffic-path']:
        device_info = next((device for device in devices if device["name"] == label), None)
        if device_info:
            device_tasks.append((label, device_info))
    
    # Use ThreadPoolExecutor for network I/O bound operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(device_tasks)) as executor:
        # Start the tasks
        future_to_device = {
            executor.submit(
                process_device, 
                label, 
                device_info, 
                ping_result, 
                response_deviceconnect, 
                remediation_results
            ): (label, device_info) for label, device_info in device_tasks
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_device):
            label, device_info = future_to_device[future]
            try:
                result = future.result()
                insights_list.append(result)
                logging.info(f"Completed processing for device: {label}")
            except Exception as exc:
                logging.error(f"Device {label} generated an exception: {exc}")
                insights_list.append({
                    "device": label, 
                    "device_type": device_info["type"] if device_info else "unknown",
                    "insights": f"Error during processing: {str(exc)}",
                    "error": True
                })
    
    print("Recon module completed.")
    return ping_result, insights_list

def find_rca(response_deviceconnect, remediation_results=None):
    """
    Find the root cause of the network issue.
    
    Args:
        response_deviceconnect (dict): Traffic path information
        remediation_results: Previous remediation efforts
        
    Returns:
        str: RCA analysis results
    """
    print("RCA module initialized.")
    print(f"Previous remediation results : \n\n{remediation_results}\n\n")
    
    # Get insights from parallel recon
    ping_result, insights_list = recon(response_deviceconnect, remediation_results)
    
    
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert Network Root Cause Analysis (RCA) Engineer. Your primary goal is to analyze the provided network information, determine the most probable root cause for the given alarm, and generate specific, actionable commands to confirm the diagnosis and/or implement a resolution.

            **INPUT CONTEXT:**
            * **Initial Reconnaissance Insights:** '{insights_list}'
            * **Alarm Trigger:** '{ping_result}' (Analyze this: what failure does it indicate?)
            * **Network Topology Snippet:** {network_topology if network_topology else 'N/A'}
            * **Relevant Traffic Path:** {response_deviceconnect.get('traffic-path', 'N/A') if isinstance(response_deviceconnect, dict) else 'N/A'}
            * **History:**
                * Previous Remediation Attempts: {remediation_results if remediation_results else 'None'}

            **RCA METHODOLOGY (Think Step-by-Step):**

            1.  **Synthesize Initial Data:** Correlate the 'Initial Reconnaissance Insights' with the specific 'Alarm Trigger'. Identify any immediate patterns or connections.
            2.  **Analyze Topology & Path:** Evaluate how the 'Network Topology' and 'Traffic Path' might contribute to the issue. Pinpoint critical devices or links along the path that are likely suspects based on the alarm type and insights.
            3.  **Formulate Hypotheses:** Based on steps 1 & 2, generate a short list of plausible root cause hypotheses (e.g., "Interface X down on Router Y", "ACL blocking traffic on Firewall Z", "Incorrect static route on Host A", "Incorrect application of access-groups and access-lists").
            4.  **Determine Most Probable Cause:** Evaluate the hypotheses against *all* available context (insights, alarm, topology, path, history). Select the *single most likely* root cause. Clearly state your reasoning, referencing specific pieces of evidence from the input context. If confidence is low, state that and explain why.

            **NEXT STEPS - COMMAND GENERATION:**

            Based on your *most probable root cause*, define the specific actions needed for verification and/or resolution.

            * **Purpose:** The goal is to provide commands that will either definitively confirm your hypothesis or directly implement the necessary fix. Prioritize configuration/action commands.
            * **No Show Commands:** Do NOT generate `show` or verification commands; assume a separate process handles status verification after changes. Focus on commands that *change* the state (configurations, service restarts etc.).
            * **Command Requirements:** For *each* command generated:
                * Target Device: Specify the exact device name.
                * Execution Context: Assume the command prompt is already in 'enable' (privileged EXEC) mode on network devices.
                * Configuration Mode: Ensure commands requiring configuration mode (e.g., Cisco `configure terminal` or `conf t`, Juniper `configure`) include the entry into that mode *before* the specific configuration lines, and exit appropriately if needed for subsequent commands on the same device.
                * Exact Syntax: Provide the full, precise command string, including necessary parameters, interface names, IP addresses, ACL names, etc., inferred from the context or your hypothesis. Use the examples below as a guide for syntax.
                * Parameterization: Use specific values derived from the context or hypothesis. If a value isn't available but is required (e.g., a specific IP), use a clear placeholder like `<REQUIRED_IP_ADDRESS>`.
            * ** Static Routes: ** Do not add any static routes. Always prefer ospf for dynamic routing. If routes are missing it could be due to interface down or other issues.
            * **Management Network Constraint:** CRITICAL - Do **not** generate commands that modify the default route or interfaces primarily used for device management, unless the analysis *specifically* identifies the management network itself as the root cause. Data plane routes are the target. Instead of changing the default route that is pointing to the management subnet, focus on adding specific routes to the data plane.
            * **Device Command Examples (Use as Syntax Guide):**
                * *Cisco IOS Router:*
                    ```bash
                    configure terminal
                    interface <type><number>
                    ip address <ip> <subnet_mask>
                    no shutdown
                    exit
                    router ospf <process_id>
                    network <ip> <wildcard_mask> area <area_id>
                    passive-interface <interface_name>
                    exit
                    access-list <num> <permit/deny> ...
                    ip access-list extended <name>
                    <sequence> <permit/deny> ...
                    exit
                    interface <type><number>
                    ip access-group <name> <in|out>
                    exit
                    end
                    ```
                * *Cisco ASA:*
                    ```bash
                    configure terminal
                    interface <name>
                    ip address <ip> <subnet_mask>
                    security-level <level>
                    nameif <name_string>
                    no shutdown
                    exit
                    router ospf <process_id>
                    network <ip> <subnet_mask> area <area_id> # Note: uses standard mask
                    passive-interface <name>
                    router-id <ip>
                    exit
                    access-list <name> extended <permit/deny> ...
                    access-group <name> <in|out> interface <nameif> (make sure to use the actual nameif name of the interface. Do not assume the nameif to be 'outside' or 'inside'..etc)
                    end
                    ```
                * *Cisco L2 Switch:* (Focus on interface/VLAN config)
                    ```bash
                    configure terminal
                    interface <type><number>
                    switchport mode <access|trunk>
                    switchport access vlan <vlan_id>
                    switchport trunk allowed vlan <vlan_list>
                    spanning-tree portfast # Example
                    no shutdown
                    exit
                    vlan <vlan_id>
                    name <vlan_name>
                    exit
                    end
                    ```
                * *Linux Host:*
                    ```bash
                    sudo ip addr add <ip>/<prefix> dev <interface>
                    sudo ip link set dev <interface> up
                    sudo ip route add <network>/<prefix> via <gateway_ip>
                    sudo ip route add default via <gateway_ip> # Use with caution per management route constraint
                    # sudo systemctl restart networking # Example service restart
                    ```
            * **JSON Output Format:** Structure the commands in a JSON object where each key is the target device name (string) and the value is an array of command strings (string[]) to be executed sequentially on that device.

                ```json
                {{
                "DeviceName1": [
                    "configure terminal",
                    "interface GigabitEthernet0/1",
                    " no shutdown",
                    " exit",
                    "end"
                ],
                "DeviceName2": [
                    "sudo ip route add 192.168.1.0/24 via 10.0.0.1",
                    "sudo ip link set dev eth1 up"
                ]
                }}
                ```

            **OUTPUT REQUIREMENTS:**

            1.  **Concise RCA Summary:** Provide a brief text summary explaining your analysis:
                * How the insights, alarm, and topology connect.
                * The most probable root cause identified.
                * Clear justification for why this cause is most likely.
            2.  **Actionable Commands JSON:** Immediately following the text summary, provide the structured JSON object containing the precise commands for the 'Next Steps', formatted exactly as specified above.
            3. **Management Network Constraint:** CRITICAL - Do **not** generate commands that modify the default route or interfaces primarily used for device management. Instead of changing the default route that is pointing to the management subnet, focus on adding specific routes to the data plane, if needed.
            """
        },
        {
            "role": "user",
            "content": "Analyze the provided context and generate a concise RCA summary and the corresponding 'Next Steps' command JSON, following the methodology and output requirements precisely."
        },
    ]
    
    # RCA analysis
    #llm="azuregpt41"
    response = dochat.dochat(messages=messages, json=False)
    print(f"RCA : \n\n")
    print_md(response)
    print(f"\n\n")

    # Save the RCA to a file
    rca_path =  os.path.join(BASE_DIR, 'data', 'reports', 'RCA.md')
    with open(rca_path, "w") as f:
        f.write(response)
        
    return response

if __name__ == "__main__":
    # For standalone testing, create a sample response_deviceconnect
    sample_response = {
        "traffic-path": ["dmz-fw"]
    }
    find_rca(sample_response)