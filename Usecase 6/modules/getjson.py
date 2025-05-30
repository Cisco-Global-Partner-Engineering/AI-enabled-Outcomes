"""
Copyright (c) 2024 Cisco and/or its affiliates.
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
"""

__author__ = "Joel Jose <joeljos@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import modules.dochat as dochat
import json
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
        }

    final_json_data = collect_responses(required_keys, alarm_data, model=model)
    return final_json_data

if __name__ == "__main__":
    for i in range(10):
        print(f"Iteration: {i}")
        pprint(final_assembly())
