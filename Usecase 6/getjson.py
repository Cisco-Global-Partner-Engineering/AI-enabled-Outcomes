import json
import dochat
from pprint import pprint
import logging

# Get the same logger
logger = logging.getLogger(__name__)

def request_specific_key(key, alarm_data):
    """
    Request specific key from the given alarm data.

    Args:
        key (str): The key to request.
        alarm_data (dict): The alarm data.

    Returns:
        str: A prompt to request the specific key.
    """
    description = key.split(":")[1].strip()
    key = key.split(":")[0].strip()

    return (f"Analyze the given Alarm data carefully and derive the value for the key : '{key}' based on what is mentioned in the description: '{description}' to determine the appropriate method."
    f"Alarm data: {alarm_data}. Output only the extracted value — no additional information.")


def collect_responses(keys, alarm_data, model=None):
    """
    Collect responses for each specific key.

    Args:
        keys (list): A list of keys to request.
        alarm_data (dict): The alarm data.

    Returns:
        dict: A dictionary with the collected responses.
    """
    gathered_data = {}
    for key in keys:
        #print(f"Key: {key}")
        logging.info(f"Processing Key: {key}")
        prompt = request_specific_key(key, alarm_data)
        response = dochat.dochat(prompt=prompt, json=False, model=model)
        key = key.split(":")[0].strip()
        gathered_data[key] = response.strip()
    return gathered_data

def final_assembly(required_keys=None, alarm_data=None, model=None):
    """
    Perform final assembly of the alarm data.

    Args:
        required_keys (list): A list of required keys. Defaults to None.
        alarm_data (dict): The alarm data. Defaults to None.

    Returns:
        dict: The final assembled alarm data.
    """
    if required_keys is None:
        required_keys = [
            "Alarm Source: The origin of the alarm",
            "Alarm Summary: A concise description of the alarm summarizing the issue",
            "Device Family: The category or type of device impacted (e.g., Switches, Routers)",
            "Classification: Whether the issue is either of resolved, urgent or normal",
            "Recommended Actions: A list of actionable steps to resolve or mitigate the issue. Each action should be clear, specific, and actionable, such as relevant Cisco CLI commands, configuration steps, or administrative tasks",
            "Tracking Next Steps: Instructions on how to monitor the issue after performing the recommended actions and what steps to take if the problem persists, including escalation guidance if necessary",
            "Alarm Details: All other details as available in the alarm data",
            "Insights: Any insights you have about the alarm"
        ]

    if alarm_data is None:
        alarm_data = {
            "alarm": "ping",
            "result": "PING 10.10.10.2 (10.10.10.2) 56(84) bytes of data.\n64 bytes from 10.10.10.2: icmp_seq=1 ttl=61 time=2.11 ms\n64 bytes from 10.10.10.2: icmp_seq=2 ttl=61 time=2.31 ms\n64 bytes from 10.10.10.2: icmp_seq=3 ttl=61 time=2.28 ms\n64 bytes from 10.10.10.2: icmp_seq=4 ttl=61 time=1.85 ms\n\n--- 10.10.10.2 ping statistics ---\n4 packets transmitted, 4 received, 0% packet loss, time 3004ms\nrtt min/avg/max/mdev = 1.849/2.134/2.305/0.180 ms\n",
            "topology": "ubuntu1 (20.20.20.2) --> router-gw (198.18.128.111) --> ubuntu2 (10.10.10.2)"
        }

    final_json_data = collect_responses(required_keys, alarm_data, model=model)
    return final_json_data

if __name__ == "__main__":
    for i in range(10):
        print(f"Iteration: {i}")
        pprint(final_assembly())
