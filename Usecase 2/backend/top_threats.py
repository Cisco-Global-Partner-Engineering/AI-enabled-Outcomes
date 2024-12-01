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

console = Console()

load_dotenv()

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


# Meraki Credentials
meraki_base_url = os.getenv("MERAKI_BASE_URL")
meraki_api_key = os.getenv("MERAKI_API_KEY")
meraki_network_id = os.getenv("MERAKI_NETWORK_ID")
meraki_org_id = os.getenv("MERAKI_ORG_ID")

# TE Credentials
te_base_url = os.getenv("TE_BASE_URL")
te_user_name = os.getenv("TE_USER_NAME")
te_password = os.getenv("TE_PASSWORD")

# Umbrella Credentials
umbrella_base_url = os.getenv("UMBRELLA_BASE_URL")
umbrella_api_key = os.getenv("UMBRELLA_API_KEY")
umbrella_key_secret = os.getenv("UMBRELLA_KEY_SECRET")

#header
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

    response = requests.request("GET", url, auth=(umbrella_api_key, umbrella_key_secret), headers=headers, data=payload)
    res = response.json()
    token = res["access_token"]

    if response.status_code == 200:
        console.log("Umbrella Authentication Successful.")
        return token

"""
Top Threat Types
"""

def umbrella_get_top_threats():
    try:
        # Umbrella Authentication
        access_token = umbrella_auth()

        url = f"https://{umbrella_base_url}/reports/v2/top-threats?from=-1days&to=now&limit=15"
        payload = {}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.request("GET", url, headers=headers, data=payload)
        res = response.json()

        if response.status_code != 200:
            console.log(f"{logging.info('Error with API Request')}")
            console.log(f"Status Code: {response.status_code}")
            console.log(f"Pushing null values to database.")
            top_threats_data = {}
            top_threats_data["threats_count"] = None
            top_threats_data["threats_data"] = None
            
            return top_threats_data
        
        if response.status_code == 200:
            console.log("API Call Successful.")
            console.log(res["data"])
            
            top_threats_list = res["data"]
            top_threats_data = {}

            if len(top_threats_list) == 0:
                console.log("No Threats found.")
                top_threats_data["threats_count"] = 0
                top_threats_data["threats_data"] = 0
                return top_threats_data
            
            top_threats_data["threats_count"] = len(top_threats_list)
            top_threats_data["threats_data"] = top_threats_list
            
            console.log(top_threats_data)
            return top_threats_data        

        else:
            console.log("API call failure.")
            console.log(response.status_code)    

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


def create_top_threats_data_model():
    #umbrella_top_threat_types_data = umbrella_get_top_threats()
    #top_threats_data_model = []
    #top_threats_data_model["top_threats"] = umbrella_top_threat_types_data

    data = [
    {"Threat Name":"Count"},
    {"Ransomware":"311"},
    {"Malware": "100"},
    {"Phishing": "15"},
    {"Other": "4"}
    ]
    return data

if(__name__ == "__main__"):
    create_top_threats_data_model()