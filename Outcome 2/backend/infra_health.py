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

import os
import requests
import logging
from dotenv import load_dotenv
from rich.console import Console
from urllib.error import HTTPError
from pprint import pprint

console = Console()
load_dotenv()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Meraki Credentials
meraki_base_url = os.getenv("MERAKI_BASE_URL")
meraki_api_key = os.getenv("MERAKI_API_KEY")
#meraki_network_id = os.getenv("MERAKI_NETWORK_ID")
meraki_org_id = os.getenv("MERAKI_ORG_ID")

# TE Credentials
te_base_url = os.getenv("TE_BASE_URL")
te_token = os.getenv("TE_TOKEN")

# Umbrella Credentials
umbrella_base_url = os.getenv("UMBRELLA_BASE_URL")
umbrella_api_key = os.getenv("UMBRELLA_API_KEY")
umbrella_key_secret = os.getenv("UMBRELLA_KEY_SECRET")

# header
headers = {
    'X-Cisco-Meraki-API-Key': meraki_api_key,
    'Content-Type': 'application/json'
}

"""
Helper Functions

- umbrella_auth() : Authenticate with umbrella.
- meraki_get_device_serials() : List Serial of all Meraki Devices in Org.
- 

"""
# Umbrella Authentication


def umbrella_auth():
    url = f"https://{umbrella_base_url}/auth/v2/token"

    payload = {}
    headers = {}

    response = requests.request("GET", url, auth=(
        umbrella_api_key, umbrella_key_secret), headers=headers, data=payload)
    res = response.json()
    token = res["access_token"]

    if response.status_code == 200:
        console.log("Umbrella Authentication Successful.")
        return token

# Get Organization ID


def get_meraki_org_id():
    url = f"https://{meraki_base_url}/organizations"
    headers = {'X-Cisco-Meraki-API-Key': meraki_api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        orgs = response.json()
        # Assuming the first organization is the one you want
        if orgs:
            return orgs[0]['id']
        else:
            print("No organizations found.")
            return None
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


# List Meraki Devices
def meraki_get_device_serials():
    try:
        url = f"https://{meraki_base_url}/organizations/{meraki_org_id}/devices"

        payload = {}
        headers = {
            'X-Cisco-Meraki-API-Key': f'{meraki_api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        # console.log(response)
        res = response.json()

        if response.status_code == 200:
            serial_list = []
            for device in res:
                serial_list.append(device["serial"])

        return serial_list

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


# List Meraki Appliances
def meraki_get_appliance_serials():
    try:
        url = f"https://{meraki_base_url}/organizations/{meraki_org_id}/devices?deviceTypes[]=appliance"

        payload = {}
        headers = {
            'X-Cisco-Meraki-API-Key': f'{meraki_api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        # console.log(response)
        res = response.json()

        if response.status_code == 200:
            serial_list = []
            for device in res:
                serial_list.append(device["serial"])

        return serial_list

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


# Section 2: Infrastructure Health
# Meraki Device Statuses
# Umbrella Tunnel Error Events
# ThousandEyes Agent Error Details
"""
Infrastructure Health
"""


def meraki_get_organization_device_status(meraki_org_id):
    try:
        url = f"https://{meraki_base_url}/organizations/{meraki_org_id}/devices/statuses"

        payload = {}
        headers = {
            'X-Cisco-Meraki-API-Key': f'{meraki_api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        res = response.json()

        if response.status_code != 200:
            console.log(f"{logging.info('Error with API Request')}")
            console.log(f"Status Code: {response.status_code}")
            console.log(f"Pushing null values to database.")
            org_device_status_details = {}
            org_device_status_details["informational"] = None
            org_device_status_details["warning"] = None
            org_device_status_details["critical"] = None

            return org_device_status_details

        if response.status_code == 200:
            if len(res) == 0:
                console.log(f"No devices found in Org ID: {meraki_org_id}")
                org_device_status_details["total_count"] = total_count
                org_device_status_details["offline_count"] = offline_count
                return org_device_status_details
            
            #print("API Call Successful.")
            #pprint(res)
            org_device_status_details = {}
            org_device_status_details["offline_details"] = []
            org_device_status_details["online_details"] = []
            total_count = 0
            offline_count = 0
            for status in res:
                total_count = total_count + 1
                if status["status"] == "offline" or status["status"] == "dormant":
                    offline_count = offline_count + 1
                    org_device_status_details["offline_details"].append(status)
                else:
                    org_device_status_details["online_details"].append(status)
            
            org_device_status_details["details"] = res
            org_device_status_details["total_count"] = total_count
            org_device_status_details["offline_count"] = offline_count

            # Infrastructure percentage
            # (online devices/total devices)*100
            org_device_status_details["infratructure_percentage"] = (
                (total_count-offline_count)/total_count)*100

            #console.log(org_device_status_details)
            return org_device_status_details
    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


def umbrella_get_tunnel_state_information():
    try:
        # Umbrella Authentication
        access_token = umbrella_auth()

        url = f"https://{umbrella_base_url}/deployments/v2/tunnelsState"
        payload = None
        headers = {"Accept": "application/json",
                   'Authorization': f'Bearer {access_token}'}

        response = requests.request("GET", url, headers=headers, data=payload)
        res = response.json()
        if response.status_code != 200:
            console.log(f"{logging.info('Error with API Request')}")
            console.log(
                f"Status : {response.text.encode('utf8')} {response.status_code}")
            console.log(f"Pushing null values to database.")
            tunnel_state_data = {}
            tunnel_state_data["status_up"] = None
            tunnel_state_data["status_down"] = None
            tunnel_state_data["health_percentage"] = None

            return tunnel_state_data

        if response.status_code == 200:
            #console.log("API Call Successful.")
            #console.log(res)

            tunnel_state_data = {}
            tunnel_state_details = []
            count_statusUp = 0
            count_statusDown = 0

            for tunnel in res:
                if tunnel["status"] == "UP":
                    count_statusUp += 1
                elif tunnel["status"] == "DOWN" or tunnel["status"] == "FAILED STATE" or tunnel["status"] == "UNKNOWN":
                    count_statusDown += 1

                data = {}
                data["tunnel_id"] = tunnel["tunnelId"]
                data["status"] = tunnel["status"]
                data["name"] = tunnel["dcName"]
                data["details"] = tunnel

                tunnel_state_details.append(data)

            tunnel_state_data["status_up"] = count_statusUp
            tunnel_state_data["status_down"] = count_statusDown
            tunnel_state_data["details"] = res

            # infra health percentage
            for tunnel in tunnel_state_details:
                tunnel["health_percentage"] = (
                    count_statusUp/len(tunnel_state_details))*100

            #console.log("tunnel_state_details:", tunnel_state_details)

            return tunnel_state_data

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


def te_get_agent_health():
    try:
        url = f"https://{te_base_url}/v7/agents"
        headers = {}

        headers = {"Authorization": "Bearer " + te_token}
        response = requests.get(url, headers=headers, params={"format":"json"}, verify=False)
        res = response.json()

        if response.status_code != 200:
            console.log(f"{logging.info('Error with API Request')}")
            console.log(f"Status Code: {response.status_code}")
            console.log(f"Pushing null values to database.")
            te_agent_details = {}
            return te_agent_details

        if response.status_code == 200:
            #console.log("API Call Successful.")
            #console.log(res)
            agent_down_count = 0
            agent_up_count = 0
            te_agent_details = {}
            if len(res["agents"]) == 0:
                te_agent_details = {}
                return te_agent_details
            te_agent_details["agent_data"] = []
            agent_array = res["agents"]
            for agent in agent_array:
                if "agentState" not in agent:
                    continue
                data = {}
                data['agentId'] = agent["agentId"]
                data['agentName'] = agent["agentName"]
                data['agentState'] = agent["agentState"]
                data['agentType'] = agent["agentType"]
                data["details"] = agent

                if agent["agentState"] == "online":
                    agent_up_count += 1
                    te_agent_details["agent_data"].append(data)
                    print("agent is online ",data)
                elif agent["agentState"] == "offline":
                    agent_down_count += 1
                    te_agent_details["agent_data"].append(data)

            total_agents = agent_up_count + agent_down_count
            #pprint("te_agent_details")
            te_agent_details["health_percentage"] = (agent_up_count/total_agents)*100
            

            return te_agent_details

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print("Error:",ex)
def get_meraki_network_id(api_key, base_url, org_id):
    url = f"https://{base_url}/organizations/{org_id}/networks"
    headers = {'X-Cisco-Meraki-API-Key': api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        networks = response.json()
        # Assuming the first network is the one you want
        if networks:
            networkids = []
            for net in networks:
                networkids.append(net["id"])
            return networkids
        else:
            print("No networks found.")
            return None
    else:
        print(f"Request failed with status code {response.status_code}")
        return None


def get_meraki_health():
    meraki_health = []
    meraki_org_id = get_meraki_org_id()
    result = meraki_get_organization_device_status(meraki_org_id)
    if(result):
        meraki_health = result
    return meraki_health

def create_infra_health_data_model():
    meraki_infra_health = get_meraki_health()
    umbrella_infra_health = umbrella_get_tunnel_state_information()
    te_infra_health = te_get_agent_health()

    infra_alert_data_model = []

    infra_alert_data_model.append({"meraki_health": meraki_infra_health})
    infra_alert_data_model.append({"umbrella_health": umbrella_infra_health})
    infra_alert_data_model.append({"te_health": te_infra_health})

    return infra_alert_data_model


if __name__ == "__main__":
    data = create_infra_health_data_model()
    console.log(data)
