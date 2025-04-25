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

import sys
import os
import json
import logging
import time

# Get the script's directory and use it to create absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent directory of main

# Add the parent directory of 'modules' to the Python path
sys.path.append(BASE_DIR)

# Now import the project modules
import modules.dochat as dochat
import modules.send_router as send_router
import modules.execute_cmd_ubuntu as execute_cmd_ubuntu
import modules.telemetry as telemetry
import modules.getjson as getjson
import parallel_rca_loop
import modules.credentials as credentials
from rich import print as print_markdown

devices = credentials.devices

# human in the loop, if True, the script will pause for user confirmation at certain points
human_in_the_loop = True 

# Ensure required directories exist
os.makedirs(os.path.join(BASE_DIR, 'data', 'reports'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data', 'input'), exist_ok=True)

# clear the remediation log file to start fresh
remediation_log_path = os.path.join(BASE_DIR, 'data', 'input', 'remediation_log.json')
with open(remediation_log_path, 'w') as f:
    f.write("")

# Clear existing handlers to avoid conflicts
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging
try:
    # Check if the file is writable
    debug_log_path = os.path.join(BASE_DIR, 'data', 'input', 'agentic_debug.log')
    with open(debug_log_path, 'a'):
        pass

    # Set up logging with both file and console handlers
    file_handler = logging.FileHandler(debug_log_path)
    console_handler = logging.StreamHandler()

    # Define the log format
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Apply the format to both handlers
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Add handlers to the root logger
    logging.getLogger().setLevel(logging.INFO)  # Set the logging level
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)

except IOError as e:
    print(f"Error: Unable to write to log file '{debug_log_path}'. {e}")
    # Fallback to console-only logging
    console_handler = logging.StreamHandler()
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_format)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)


def new_alarm_intake():
    
    #Load ping results
    telemetry_result = telemetry.ping_all()

    ping_result = {"Ping Result": [telemetry_result]}

    # Combine alarms into a single dictionary
    alarms = {**ping_result}

    # Use absolute path for writing the combined alarms file
    combined_alarms_path = os.path.join(BASE_DIR, 'data', 'input', 'combined_alarms.json')
    with open(combined_alarms_path, 'w') as f:
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
                "Recommended Actions: A list of actionable steps to resolve or mitigate the issue. Each action should be clear, specific, and actionable, such as relevant Cisco CLI commands, configuration steps, or administrative tasks",
                "Tracking Next Steps: Instructions on how to monitor the issue after performing the recommended actions and what steps to take if the problem persists, including escalation guidance if necessary",
                "Alarm Details: All other details as available in the alarm data. If none, state 'none'",
                "Insights: Any insights you have about the alarm. If none, state 'none'",
                "Priority: The priority level of the alarm, either of 'Urgent', 'Normal' or 'Low'. Alarm should be marked as 'Urgent' if it requires immediate attention and 'Low' if it is informational or non-critical",
                "Status: The current state of the alarm, either of 'Resolved' or 'Active'"
            ]
            logging.info("Step 1 : Generating initial Agentic report for current alarms..")
            print_markdown(f"## [yellow] Step 1 : Generating initial Agentic report for current alarms..")
            response = getjson.final_assembly(required_keys=required_keys,alarm_data=initalarm)
            response["Alarm Source"] = key
            response["Alarm ID"] = f"{key} {count}"
            logging.info("Initial Alarm data :")
            logging.info(response)
            alarmlist["Alarms"].append(response)
        
        
    # Save current response
    initial_report_path = os.path.join(BASE_DIR, 'data', 'reports', 'agentic_initial_report.json')
    with open(initial_report_path, 'w') as f:
        json.dump(alarmlist, f, indent=4)

    logging.info("Step 2. Starting workflow invocation based on Agentic insights..")
    print_markdown(f"## [yellow] Step 2 : Starting workflow invocation based on Agentic insights..")
    logging.info(f"Total Alarms : {len(alarmlist['Alarms'])}")
    i = -1
    for alarm in alarmlist["Alarms"]:
        i += 1
        logging.info(f"Alarm #{i+1} : ")
        logging.info(json.dumps(alarm, indent=4))
        if alarm["Status"].lower() == "resolved":
            logging.info("!! Skipping workflow invocation as Alarm is already resolved !!")
            # print in color
            print_markdown(f"[green]!! Skipping workflow invocation as Alarm is already resolved !!")
            continue
        else:
            logging.info("Unresolved Ping alarm detected.")

            # Load the network topology from the JSON file using an absolute path
            l3_topology_path = os.path.join(BASE_DIR, 'data', 'input', 'l3_topology.json')
            with open(l3_topology_path) as f:
                topology = json.load(f)
            alarm_data = {
                "alarm": alarm,
                "topology": topology
            }

            messages = [
            {
                "role": "system",
                "content": "You are an AI that processes network data and outputs results as a pure JSON string. Your response must contain *only* the JSON object. Do NOT include any surrounding text, explanations, markdown code blocks (like ```json), or extra characters before or after the JSON. The JSON object must contain a single key, 'traffic-path', whose value is either a Python-compatible list of device labels or the string 'none'. Make use of the 'linux_to_linux_traffic_flows' key in the topology to help determine the traffic path."
            },
            {
                "role": "user",
                "content": f"Analyze the following `alarm_data` dictionary: '{alarm_data}'\n\nFrom the 'topology' within this `alarm_data`, identify all the devices in the traffic path related to the set of alarms. The path should include source and destination nodes for telemetry/traffic and encompass both L3 and L2 devices along that traffic path. The alarm may have multile traffic flows, select all the devices across all the flows. Provide the result as a JSON object with the key 'traffic-path'.\n\n**Expected Output Examples (raw JSON):**\n`{{\"traffic-path\": [\"device_A\", \"switch_B\", \"router_C\", \"server_D\"]}}`\n`{{\"traffic-path\": \"none\"}}`"
            }
            ]

            logging.info("Step 3. Finding the traffic path based on the alarm and topology..")
            print_markdown(f"## [yellow] Step 3 : Finding the traffic path based on the alarm and topology..")
            remediation_results=None
            rca_history = []

            #TODO: In future to derive the traffic path from the LLM by asking it to analyze the alarm and topology : #response_traffic_path = dochat.dochat(messages=messages,json=True,llm="azuregpto4mini")
            """ if type(response_traffic_path["traffic-path"]) == str:
                logging.info("traffic-path evals : ")
                logging.info(response_traffic_path["traffic-path"])
                response_traffic_path["traffic-path"] = eval(response_traffic_path["traffic-path"]) # convert string to list """
            
            response_traffic_path = {"traffic-path": ["branch-router", "branch-fw", "branch-switch", "client-switch", "client1", "client2", "client1-switch", "client2-switch", "client1-router", "client2-router", "dmz-router", "dmz-fw", "server-switch", "server", "remote-worker"]}
            
            logging.info("Traffic Path : ")
            logging.info(response_traffic_path)
            
            limit = 5 # maximum number of times to run the loop
            for loopcounter in range(limit):
                logging.info("Step 4. Confirming if the alarm is still active..")
                print_markdown(f"## [yellow] Step 4 : Confirming if the alarm is still active..")
                logging.info("Running latest telemetry tests..")
                latest_telemetry = telemetry.ping_all()
                messages = [
                    {
                        "role": "system",
                        "content": f"""
                        Review the current alarm conditions and utilize the latest telemetry data to ascertain the status of the alarm. If after the Root Cause Analysis (RCA) and considering the most recent telemetry, the alarm appears to be in a resolved state, please respond with 'Resolved'. If the alarm remains unresolved, even with the new telemetry insights, please reply with 'not-Resolved'. Do not output anything else.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Existing initial alarm : '{alarm}', Latest telemetry result : '{latest_telemetry}'"
                    }
                ]
                breakornot = dochat.dochat(messages=messages)
                logging.info("Alarm resolved or not : ")
                logging.info(breakornot)
                if breakornot.lower() == "resolved":
                    #print("Alarm resolved. Breaking the RCA loop..")
                    logging.info("Alarm resolved. Breaking the RCA loop..")
                    break

                logging.info("Step 5 Generating root cause analysis for Agentic insights..")
                print_markdown(f"## [yellow] Step 5 : Generating root cause analysis for Agentic insights..")
                rca = parallel_rca_loop.find_rca(response_traffic_path,remediation_results)
                logging.info("RCA : ")
                # print markdown in nice format using rich
                print_markdown(rca)

                latest_telemetry = telemetry.ping_all()
                messages = [
                    {
                        "role": "system",
                        "content": f"""
                        Review the current alarm conditions and utilize the latest telemetry data to ascertain the status of the alarm. If after the Root Cause Analysis (RCA) and considering the most recent telemetry, the alarm appears to be in a resolved state, please respond with 'Resolved'. If the alarm remains unresolved, even with the new telemetry insights, please reply with 'not-Resolved'. Do not output anything else.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Existing initial alarm : '{alarm}', Latest telemetry result : '{latest_telemetry}'"
                    }
                ]

                breakornot = dochat.dochat(messages=messages)
                logging.info("Alarm resolved or not : ")
                logging.info(breakornot)
                if breakornot.lower() == "resolved":
                    #print("Alarm resolved. Breaking the RCA loop..")
                    logging.info("Alarm resolved. Breaking the RCA loop..")
                    break

                rca_history.append(rca)
                remediation_attempt = 5
                attempt = 0
                for attempt in range(remediation_attempt):
                    if(human_in_the_loop):
                        logging.info("Pausing for human in the loop. Please confirm the RCA and the next steps and then press Enter to continue..")
                        confirm = input("Type 'confirm' to continue to the next step...")
                        while confirm.lower() != "confirm":
                            logging.info("Invalid input. Please type 'confirm' to continue.")
                            confirm = input("Type 'confirm' to continue to the next step...")

                    rca_log_path = os.path.join(BASE_DIR, 'data', 'reports', 'RCA.md')
                    with open(rca_log_path,"r") as file:
                        rca = file.read()
                    
                    messages = [
                        {
                            "role": "system",
                            "content": f"""
                            You are a network troubleshooting assistant that analyzes Root Cause Analysis documents 
                            and extracts actionable commands organized by device. Your task is to:
                            
                            1. Parse the "Next Steps" section of an RCA document
                            2. Identify each device mentioned
                            3. Extract the commands that need to be executed on each device
                            4. Organize these commands in the proper sequence
                            5. Return a structured JSON object where:
                            - Each key is a device name
                            - Each value is an array of commands to be executed on that device in order
                            - assume that all network device is by default entered in 'enable mode' and the commands have to account for that.
                            
                            If there are no commands for a particular device or no next steps at all, return a JSON 
                            with a single key "status" and value "Null".
                            
                            Format all commands exactly as they appear in the RCA without adding or removing syntax.
                            Maintain the proper sequence of commands for each device.
                            """
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Please analyze the following RCA document and provide the structured JSON output 
                            of commands by device:
                            
                            {rca}
                            """
                        }
                    ]
                    
                    #print("Generating CLI commands for Agentic insights..")
                    logging.info("Generating CLI commands for Agentic insights..")
                    cli = dochat.dochat(messages=messages,json=True)
                    logging.info("CLI Commands to be executed : ")
                    logging.info(json.dumps(cli, indent=4))

                    if(human_in_the_loop):
                        logging.info("Confirm to continue to ** Auto remediation ** step...")
                        confirm = input("Type 'confirm' to continue to the next step...")
                        while confirm.lower() != "confirm":
                            logging.info("Invalid input. Please type 'confirm' to continue.")
                            confirm = input("Type 'confirm' to continue to the next step...")
                    logging.info("Step 6. Executing auto-remediation commands on devices..")
                    print_markdown(f"## [yellow] Step 6 : Executing auto-remediation commands on devices..")
                    remediation_results = []
                    if "status" in cli.keys():
                        if cli["status"].lower() == "null":
                            #print("No commands found in RCA. Breaking the loop..")
                            logging.info("No commands found in RCA. Breaking the loop..")
                            break

                    # Use absolute path for remediation log file
                    remediation_log_path = os.path.join(BASE_DIR, 'data', 'reports', 'remediation_log.json')
                    with open(remediation_log_path, "w") as file:
                        file.write("")
                    for key in cli:
                        #clean the individual commands
                        cli[key] = [command.strip() for command in cli[key]]
                        #print(f"Device : {key}")
                        logging.info(f"Device : {key}")
                        #print("Commands : ")
                        logging.info("Commands : ")
                        #pprint(response_cli[key])
                        logging.info(cli[key])
                        # Finding the device IP address based on the device name
                        for device in devices:
                            if device["name"] == key:
                                if(device["type"] == "alpine virtual linux"):
                                    logging.info("Executing commands on Linux machine..")
                                    remediation_results.append({"device":device["name"],f"cli_cmd_{key}":
                                        execute_cmd_ubuntu.execute_commands_ssh(
                                        device["ip"],
                                        device["username"],
                                        device["password"],
                                        commands=cli[key]
                                        )})
                                elif(device["type"] == "Cisco IOS virtual Router"):
                                    remediation_results.append({"device":device["name"],f"cli_cmd_{key}":send_router.execute_commands_in_parallel([device["name"]],cli[key])})
                                elif(device["type"] == "Cisco IOS Layer 2 virtual Switch"):
                                    remediation_results.append({"device":device["name"],f"cli_cmd_{key}":send_router.execute_commands_in_parallel([device["name"]],cli[key])})
                                elif(device["type"] == "Cisco virtual ASA Firewall"):
                                    remediation_results.append({"device":device["name"],f"cli_cmd_{key}":send_router.send_config_commands(device["name"],cli[key])})

                    #print("Remediation commands executed successfully.")
                    logging.info("Remediation commands executed successfully.")
                    # Use absolute path for appending to remediation log
                    with open(remediation_log_path, "a") as file:
                        file.write(json.dumps(remediation_results, indent=4))
                    
                    messages = [
                        {
                            "role": "system",
                            "content": f"""
                            Analyze the following remediation results and if the remediation was successful, indicate that the issue has been resolved by replying with only 'remediated' and nothing else. Otherwise, if the remediation was not successful, provide details on what went wrong. Ask user to make the needed changed to the rca.md file and then press 'confirm' to continue and retry the remediation.
                            """
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Remediation Results : {remediation_results}
                            """
                        }
                    ]
                    remediation_status = dochat.dochat(messages=messages)
                    logging.info("Remediation status : ")
                    logging.info(remediation_status)
                    if 'remediated' in remediation_status.lower():
                        logging.info("Remediation successful. Breaking the loop..")
                        break
                    else:
                        logging.error("Remediation not successful. Please check the remediation log and make the needed changes to the rca.md file and then press 'confirm' to continue and retry the remediation.")
                        confirm = input("Type 'confirm' to continue to the next step...")
                        while confirm.lower() != "confirm":
                            logging.error("Invalid input. Please type 'confirm' to continue.")
                            confirm = input("Type 'confirm' to continue to the next step...")
                
                if attempt == remediation_attempt:
                    logging.error("Remediation failed after maximum attempts. Please check the remediation log")
                    break
                logging.info("Sleeping for 60 seconds to allow remediation to take effect..")
                time.sleep(60)

            logging.info("Running latest telemetry tests..")
            telemetry_result = telemetry.ping_all()
            logging.info("Telemetry results : ")
            logging.info(telemetry_result)
            messages = [
            {
            "role": "system",
            "content": f"""You are a Cisco network troubleshooting assistant, you will analyse the original alarm : '{alarm}', complete RCA : '{rca_history}', the result of the remediation commands executed on the device and latest telemetry results given by the user. Based on all the data provided, generate a detailed description of the alarm, the RCA, the remediation steps taken, and the final outcome. Provide details of the entire process, including any additional insights or recommendations. Be comprehensive in your reply and not miss any details."""
            },

            {"role": "user", "content": f"Remediation : {remediation_results}, Latest Telemetry : {telemetry_result}"}
            ]
            logging.info("Step 7. Generating summary for Agentic insights..")
            print_markdown(f"## [yellow] Step 7 : Generating summary for Agentic insights..")
            response_summary = dochat.dochat(messages=messages)
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
            logging.info("Step 8. Updating Final Report...")
            print_markdown(f"## [yellow] Step 8 : Updating Final Report...")
            response["Alarm Source"] = alarm["Alarm Source"]
            response["Alarm ID"] = alarm["Alarm ID"]
            alarmlist["Alarms"][i] = response


        # Save the updated insights back to the file to preserve the changes to Recommended Actions
        final_report_path = os.path.join(BASE_DIR, 'data', 'reports', 'agentic_final_report.json')
        with open(final_report_path, 'w') as f:
            json.dump(alarmlist, f, indent=4)

        logging.info("Step 9. Invoking Webex Notification workflow..")
        print_markdown(f"## [yellow] Step 9 : Invoking Webex Notification workflow..")
        #logging.info("...NOTIFY...")
        print_markdown("[green] ** Final Report Notification ** ")
        logging.info(json.dumps(alarmlist, indent=4))
        #webex_notification.send_webex_notification(message=response['details'])

    
    return alarmlist

            
if __name__ == "__main__":
    agentic()
    logging.info("Agentic processing completed.")