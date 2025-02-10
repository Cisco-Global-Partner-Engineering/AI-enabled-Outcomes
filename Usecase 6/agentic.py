import json
import logging
#from pprint import pformat
#import time
from datetime import datetime
import CatalystCenter_auth
import sdwan_alarm_reduce
import vManageAlarms
import dochat
#import webex_notification
#import websearch
import send_router
import ping_ubuntu
import getjson

with open("agentic_debug.log", "w") as f:
    f.write("")
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agentic_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def new_alarm_intake():
    alarms_catalystcenter = CatalystCenter_auth.get_health()
    vManage_alarms = vManageAlarms.get_data()
    alarms_sdwan = sdwan_alarm_reduce.analyze_alarms(alarms=vManage_alarms)
    alarms_sdwan = alarms_sdwan["alarm_reduction"]["reduced_alarms"]

    """ # Load alarms from Cisco Catalyst Center
    with open('alarms_catalystcenter.json') as f:
        alarms_catalystcenter = json.load(f)
    # Load alarms from Cisco SD-WAN Manager
    with open('sdwan_alarm_reduction_results.json') as f:
        alarms_sdwan = json.load(f)
        alarms_sdwan = alarms_sdwan["alarm_reduction"]["reduced_alarms"]
    """
    
    alarms_catalystcenter = {"Cisco Catalyst Center": alarms_catalystcenter}
    alarms_sdwan = {"Cisco SD-WAN Manager": alarms_sdwan}
    #Load ping results
    telemetry_result = ping_ubuntu.ping_from_remote_ubuntu()
    """
    telemetry_result = '''
    PING 10.10.10.2 (10.10.10.2) 56(84) bytes of data.\nFrom 20.20.20.1 icmp_seq=1 Destination Host Unreachable\nFrom 20.20.20.1 icmp_seq=2 Destination Host Unreachable\nFrom 20.20.20.1 icmp_seq=3 Destination Host Unreachable\nFrom 20.20.20.1 icmp_seq=4 Destination Host Unreachable\n\n--- 10.10.10.2 ping statistics ---\n4 packets transmitted, 0 received, +4 errors, 100% packet loss, time 3015ms\n\n
    '''
    """

    ping_result = {"Ping Result": [telemetry_result]}

    # Combine alarms into a single dictionary
    alarms = {**alarms_catalystcenter, **alarms_sdwan, **ping_result}
    #alarms = {**ping_result}

    with open('combined_alarms.json', 'w') as f:
        json.dump(alarms, f, indent=4)

    return alarms


def agentic():
    # Load the combined alarms data
    alarms = new_alarm_intake()
    logging.info("Length of Alarms : ")
    logging.info(len(alarms))
    #logging.info("Alarms : ")
    #logging.info(alarms)

    alarmlist = {"Alarms":[]}
    for key,value in alarms.items():
        count = 0
        for initalarm in value:
            count += 1
            required_keys = [
                "Alarm Summary: A concise description of the alarm summarizing the issue",
                "Device Family: The category or type of device impacted (e.g., Switches, Routers)",
                "Classification: Whether the issue is either of Resolved, Urgent or Normal",
                "Recommended Actions: A list of actionable steps to resolve or mitigate the issue. Each action should be clear, specific, and actionable, such as relevant Cisco CLI commands, configuration steps, or administrative tasks",
                "Tracking Next Steps: Instructions on how to monitor the issue after performing the recommended actions and what steps to take if the problem persists, including escalation guidance if necessary",
                "Alarm Details: All other details as available in the alarm data. If none, state 'none'",
                "Insights: Any insights you have about the alarm. If none, state 'none'",
                "Priority: The priority level of the alarm, either of 'Urgent', 'Normal' or 'Low'. Alarm should be marked as 'Urgent' if it requires immediate attention and 'Low' if it is informational or non-critical",
                "Status: The current state of the alarm, either of 'Resolved' or 'Active'"
            ]
            logging.info("Step 1 : Generating initial Agentic response for current alarms..")
            response = getjson.final_assembly(required_keys=required_keys,alarm_data=initalarm)
            response["Alarm Source"] = key
            response["Alarm ID"] = f"{key} {count}"
            logging.info("Initial Alarm data :")
            logging.info(response)
            alarmlist["Alarms"].append(response)
        
        """ alarmlist = {
        "Alarms": [
            {
                "Alarm Source": "Ping Result",
                "Alarm Summary": "Destination Host Unreachable, 100% packet loss",
                "Device Family": "Routers",
                "Classification": "Urgent",
                "Recommended Actions": "1. Verify network connectivity and configuration between the source (20.20.20.1) and destination (10.10.10.2) IP addresses.\n2. Check the routing table for any issues or misconfigurations that might be causing the \"Destination Host Unreachable\" error.\n3. Use the Cisco CLI command \"show ip route\" to display the routing table and verify the path to the destination IP address.\n4. Run the command \"ping 10.10.10.2 source 20.20.20.1\" to isolate if the issue is specific to the source IP address.\n5. Execute the command \"traceroute 10.10.10.2\" to identify where the packets are being dropped or lost.\n6. Check for any firewall or access control list (ACL) rules that might be blocking ICMP packets between the source and destination IP addresses.\n7. Verify the IP address configuration on both the source and destination devices to ensure they are correctly set and match the expected settings.",
                "Tracking Next Steps": "To monitor the issue after performing the recommended actions, continue to ping the destination IP address (10.10.10.2) at regular intervals to check for any changes in connectivity. If the problem persists, check the network configuration and ensure that there are no firewall rules or network access control lists (ACLs) blocking the ICMP packets. Additionally, verify that the destination host is powered on and configured correctly. If the issue still persists, escalate the problem to the network administration team for further investigation and resolution.",
                "Alarm Details": "Ping Result \nPING 10.10.10.2 (10.10.10.2) 56(84) bytes of data.\nFrom 20.20.20.1 icmp_seq=1 Destination Host Unreachable\nFrom 20.20.20.1 icmp_seq=2 Destination Host Unreachable\nFrom 20.20.20.1 icmp_seq=3 Destination Host Unreachable\nFrom 20.20.20.1 icmp_seq=4 Destination Host Unreachable\n\n--- 10.10.10.2 ping statistics ---\n4 packets transmitted, 0 received, +4 errors, 100% packet loss, time 3015ms",
                "Insights": "The alarm indicates a network connectivity issue, with 100% packet loss and \"Destination Host Unreachable\" errors, suggesting that the host 10.10.10.2 is not reachable from the source 20.20.20.1."
            }
        ]
    } """
        
    # Save current response
    with open('agentic_response.json', 'w') as f:
        json.dump(alarmlist, f, indent=4)

    logging.info("Step 2. Starting workflow invocation based on Agentic insights..")
    rca_alarms = []
    workflows = ["webex_notification"]
    logging.info("Alarms : ")
    logging.info(alarmlist)
    i = -1
    for alarm in alarmlist["Alarms"]:
        i += 1
        if alarm["Classification"].lower() == "resolved" or alarm["Alarm Source"].lower() != "ping result":
            logging.info("Skipping workflow invocation..")
            logging.info(alarmlist)
            continue
        else:
            logging.info("Unresolved Ping alarm detected.")
            # Device connect attempt for new alarms and detailed root cause analysis
            routerip_mapping = ["198.18.128.111"]
            with open("network_topology.json") as f:
                topology = json.load(f)
            with open("runbook.txt") as f:
                runbook = f.read()
            
            alarm_data = {
                "alarm": alarm,
                "topology": topology,
                "available_management_ips": routerip_mapping
            }

            required_keys = [
            "deviceip-to-connect: From the available_management_ips in alarm_data, select the Management IP of the device most relevant to the alarm based on its relationship in the alarm and topology. **Output only Management IPs or 'none' without any additional text or explanations**"
        ]

            
            print("Alarm Data and Required Keys : ")
            print(alarm_data, required_keys)

            #print("Generating RCA check for Agentic auto-remediation..")
            logging.info("Step 3. Finding the device to connect based on the alarm and topology..")
            show_results =[]
            rca_history = []
            model = "meta-llama/llama-3.3-70b-instruct"
            response_deviceconnect = getjson.final_assembly(required_keys=required_keys,alarm_data=alarm_data,model=model)
            logging.info("Response Device Connect : ")
            logging.info(response_deviceconnect)

            if(response_deviceconnect["deviceip-to-connect"] in routerip_mapping):
                alarm_data = {
                "alarm": alarm,
                "topology": topology,
                "runbook": runbook,
                "available_commands" : """
                General System Information:
                - show version                : Displays system hardware, software version, and uptime.
                - show running-config         : Shows the current configuration in RAM.
                - show startup-config         : Displays the configuration stored in NVRAM.
                - show history                : Shows command history.
                - show users                  : Lists users currently connected to the device.
                - show processes cpu          : Displays CPU utilization statistics.
                - show memory                 : Displays memory usage details.
                - show clock                  : Displays the current date and time.

                Interface and IP Information:
                - show interfaces             : Displays details about all interfaces.
                - show interfaces [interface] : Displays detailed info for a specific interface.
                - show ip interface brief     : Shows a summary of IP interfaces and their status.
                - show ip route               : Displays the routing table.
                - show arp                    : Shows the ARP table.
                - show mac address-table      : Displays the MAC address table.

                Routing and Protocols:
                - show ip protocols           : Displays routing protocol settings.
                - show ip ospf neighbor       : Lists OSPF neighbors.
                - show ip bgp summary         : Displays BGP summary information.
                - show cdp neighbors          : Shows directly connected Cisco devices.
                - show lldp neighbors         : Displays LLDP neighbor information.

                Security and Access:
                - show access-lists           : Displays all configured ACLs.
                - show logging                : Displays system logs.
                - show aaa                    : Shows authentication, authorization, and accounting settings.
                - show ip nat translations    : Displays active NAT translations.

                Switching and VLANs:
                - show vlan brief             : Shows VLANs and their status.
                - show spanning-tree          : Displays spanning-tree information.
                - show etherchannel summary   : Displays EtherChannel details.

                Device Performance:
                - show processes memory       : Displays memory usage per process.
                - show environment            : Displays hardware environment status.
                - show power inline           : Shows PoE (Power over Ethernet) usage.
                """

                }
                required_keys = [
                f"show commands: A list of the most appropriate show commands (upto max 5) from among the 'available_commands', seperated by ',', to run on '{response_deviceconnect["deviceip-to-connect"]}' and try finding the root cause of the alarm. If none, state 'none'. Do not output any other information."
                ]
                response_deviceconnect_showcommands = getjson.final_assembly(required_keys=required_keys,alarm_data=alarm_data)
                logging.info("Response Device Connect Show Commands : ")
                logging.info(response_deviceconnect_showcommands)

                logging.info("Step 4. Starting RCA loop for Agentic insights..")
                for routerip in [response_deviceconnect["deviceip-to-connect"]]:
                    show_commands = response_deviceconnect_showcommands["show commands"].split(",")
                    logging.info("Router IP : ")
                    logging.info(routerip)
                    logging.info("Show Commands : ")
                    logging.info(show_commands)
                    logging.info("Sending show commands to router..")
                    results = send_router.router_send_command(routerip, show_commands)
                    results = {}
                    with open("debug_log.txt","r") as file:
                        results["results"] = file.read()
                    show_results.append({"results":results["results"]})
                #print("show_results : ")
                logging.info("show_results : ")
                #pprint(show_results)
                logging.info(show_results)
                with open("network_topology.json") as f:
                    topology = json.load(f)
            else:
                logging.info("No device to connect. Skipping RCA loop..")
                logging.info("Alarm Data : ")
                logging.info(alarm_data)
                logging.info("Response Device Connect : ")
                logging.info(response_deviceconnect)
                logging.info("Skipping RCA loop..")
                return False
            while(True):
                #print("Running latest telemetry tests..")
                logging.info("Running latest telemetry tests..")
                telemetry_result = ping_ubuntu.ping_from_remote_ubuntu()
                #print("Telemetry results : ")
                logging.info("Telemetry results : ")
                #pprint(telemetry_result)
                logging.info(telemetry_result)
                messages = [
                    {
                        "role": "system",
                        "content": f"""
                        Analyze the alarm : '{alarm}' and user provided telemetry and show results. Based on the alarm, telemetry and show results, determine if the alarm is resolved or not. Give the most preference to the telemetry result, for the analysis. If resolved, respond with Resolved. If not resolved, respond with not-Resolved. Do not output anything else.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Router Results: {show_results}, Latest Telemetry: {telemetry_result}"
                    }
                ]

                model = "meta-llama/llama-3.3-70b-instruct"
                breakornot = dochat.dochat(messages=messages,model=model)
                logging.info("Response Break or Not : ")
                logging.info(breakornot)
                if breakornot.lower() == "resolved":
                    #print("Alarm resolved. Breaking the RCA loop..")
                    logging.info("Alarm resolved. Breaking the RCA loop..")
                    break

                messages = [
                    {
                        "role": "system",
                        "content": f"""
                        Given the runbook: '{runbook}' and the network topology: '{topology}', analyze the provided alarm: '{alarm}' 
                        based on:
                        - The results of recent show commands from the router.
                        - The latest end-to-end telemetry test results. 
                        - **Make sure to prioritize the instructions mentioned in the runbook : '{runbook}'**.

                        **Objectives**:  
                        - Identify the **single most probable root cause** of the alarm. 
                        - **Do not repeat any previous RCA** 

                        **Atomic RCA Requirement**:  
                        - The root cause must be **atomic**, meaning it should result in exactly **one network change**.  
                        - If multiple changes are needed to resolve the issue, **select only the most impactful single change** that is likely to resolve or contribute to resolving the issue.  

                        **Response Format (JSON only)**:  
                        - If a probable root cause is found: `{{"rca": "<single identified root cause>"}}`  
                        - If no RCA can be determined: `{{"rca": "none"}}`  
                        - If the issue appears resolved: `{{"rca": "resolved"}}`  

                        **Strict Requirements**:  
                        - Return **only** a valid JSON object.  
                        - Do **not** include explanations, comments, or any additional text.  
                        - The RCA must be **a single actionable change** (e.g., "Bring up interface X", **not** "Bring up interface X and Y").  
                        - If multiple issues are detected, **select the most probable single root cause** based on available data.
                        - To ensure a logical and effective Root Cause Analysis (RCA) in network troubleshooting, it's essential to address foundational issues before delving into higher-level problems. For instance, if certain network interfaces are down, this could lead to missing routes. Therefore, it's prudent to first bring up the necessary interfaces and then verify if the routes are still missing.

                        """
                    },
                    {
                        "role": "user",
                        "content": f"Router Results: {show_results}, Latest Telemetry: {telemetry_result}, Previous RCA: {rca_history}"
                    }
                ]

                #print("Generating root cause analysis for Agentic insights..")
                logging.info("Step 5. Generating root cause analysis for Agentic insights..")
                response_rca = dochat.dochat(messages=messages,json=True)
                #print("Response RCA : ")
                logging.info("Response RCA : ")
                #pprint(response_rca)
                logging.info(response_rca)

                rca_history.append(response_rca)
                if(response_rca["rca"]=="none" or response_rca["rca"]=="resolved"):
                    break
                messages = [
                {
                "role": "system",
                "content": f"""You are a Cisco network troubleshooting assistant, specializing in interpreting detailed Root Cause Analysis (RCA) reports and converting them into actionable CLI commands for Cisco IOS devices. Given the runbook : '{runbook}' and topology : '{topology}' and Based on the RCA provided, you will:
                Analyze the potential root cause, alarm summary, and recommended actions. **Make sure to prioritize the instructions mentioned in the runbook : '{runbook}'.**
                Generate commands for transitioning between appropriate modes (enable, config, interface) on the device. 
                
                **Always assume that the device connection starts initially in enable mode. Always consider the current prompt at each command, before crafting your command lists.**

                Format your response in JSON to maintain clarity and allow direct usage of the commands.
                Based on the user provided RCA, you need to generate a step-by-step sequence of CLI commands to:
                Follow the main resolution mentioned in the RCA.
                Provide only the most relevant commands to resolve the issue. Try to make only one feature change.
                Validate the solution using diagnostic commands.
                If the RCA does not have associated CLI commands, respond with an empty list for "commands".
                Output Requirements:
                Provide the output in the following JSON format, where the key 'connection' has the value of the IP address of the device to connect to, out of these available list : {response_deviceconnect["deviceip-to-connect"]}:
                {{
                "connection": "",
                "commands": [
                    "command1", 
                    "command2",
                    "command3"
                ]
                }}
                Include special command (only if needed) : 'sleep <seconds>' at the appropriate places in the list to implement wait before running the next command if required (eg for route convergence..etc).
                """
                },

                {"role": "user", "content": f"RCA : {response_rca}"}
                ]
                #print("Generating CLI commands for Agentic insights..")
                logging.info("Generating CLI commands for Agentic insights..")
                response_cli = dochat.dochat(messages=messages,json=True)
                #response_cli = json.loads(response_cli)
                #pprint(response_cli)
                logging.info(response_cli)
                if response_cli["commands"] == []:
                    break
                logging.info("Sending commands to router..")
                response_remediation = send_router.router_send_command(response_cli["connection"],response_cli["commands"])
                #print("Remediation commands executed successfully.")
                logging.info("Remediation commands executed successfully.")
                results = {}
                with open("debug_log.txt","r") as file:
                    response_remediation = file.read()
                #print(response_remediation)
                logging.info("Response Remediation : ")
                logging.info(response_remediation)
                show_results.append({"commands executed": response_cli["commands"], "results":response_remediation})

            #print("Running latest telemetry tests..")
            logging.info("Running latest telemetry tests..")
            telemetry_result = ping_ubuntu.ping_from_remote_ubuntu()
            #print("Telemetry results : ")
            logging.info("Telemetry results : ")
            #pprint(telemetry_result)
            logging.info(telemetry_result)
            messages = [
            {
            "role": "system",
            "content": f"""You are a Cisco network troubleshooting assistant, you will analyse the original alarm : '{alarm}', complete RCA : '{rca_history}', the result of the remediation commands executed on the device and latest telemetry results given by the user. Based on all the data provided, generate a detailed description of the alarm, the RCA, the remediation steps taken, and the final outcome. Provide details of the entire process, including any additional insights or recommendations. Be comprehensive in your reply and not miss any details."""
            },

            {"role": "user", "content": f"Remediation : {show_results}, Latest Telemetry : {telemetry_result}"}
            ]
            #print("Generating summary for Agentic insights..")
            logging.info("Step 6. Generating summary for Agentic insights..")
            model = "meta-llama/llama-3.3-70b-instruct"
            response_summary = dochat.dochat(messages=messages,model=model)
            #print(response_summary)
            logging.info(response_summary)

            required_keys = [
                "Alarm Summary: A brief description of the alarm.",
                "Device Family: The category of the affected device (e.g., Routers, Switches).",
                "Classification: The urgency level of the alarm, either of 'Urgent', 'Normal' or'Low' ",
                "Reason: The underlying cause of the alarm.",
                "Recommended Actions: A list of suggested troubleshooting steps.",
                "Tracking Next Steps: The follow-up actions to monitor resolution progress.",
                "Alarm Details: Detailed information such as topology and logs.",
                "Status: The current state of the alarm - 'Resolved' or 'Active'. If the alarm is resolved or just informational in nature, mark it as 'Resolved'",
                "Priority: The priority level of the alarm either of 'Urgent', 'Normal' or 'Low'. Resolved alarms should be marked as 'Low'.",
                "Insights: Any additional findings or updated insights related to the alarm.",
                "Root Cause Analysis: A summary of the investigation findings in list format.",
                "Auto-Remediation Steps Taken: A list of steps performed to resolve the issue.",
                "Final Outcome: The result after applying the remediation steps.",
                "Additional Insights/Recommendations: Any best practices or preventative measures."
            ]

            response = getjson.final_assembly(required_keys=required_keys,alarm_data=response_summary)
            logging.info("Step 7. Updating alarmlist based on final response of RCA..")
            response["Alarm Source"] = alarm["Alarm Source"]
            response["Alarm ID"] = alarm["Alarm ID"]
            alarmlist["Alarms"][i] = response

        logging.info("Step 8. Invoking Webex Notification workflow..")
        logging.info("...NOTIFY...")
        #webex_notification.send_webex_notification(message=response['details'])

    # Save the updated insights back to the file to preserve the changes to Recommended Actions
    with open('agentic_response_insights.json', 'w') as f:
        json.dump(alarmlist, f, indent=4)
    return alarmlist

            
if __name__ == "__main__":
    agentic()
    #print("Agentic processing completed.")
    logging.info("Agentic processing completed.")