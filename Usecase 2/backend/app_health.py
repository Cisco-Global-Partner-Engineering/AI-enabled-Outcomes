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
import re
import sys
import requests
import json
import logging
#import schedule
import time
from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from urllib.error import HTTPError
from pymongo.mongo_client import MongoClient
import thousandEyes_auth as te
from pprint import pprint

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
te_token = os.getenv("TE_TOKEN")

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

# List Meraki Devices
def meraki_get_device_serials():
    try:
        url = f"https://{meraki_base_url}/organizations/{meraki_org_id}/devices"

        payload = {}
        headers = {
        'X-Cisco-Meraki-API-Key': f'{meraki_api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        #console.log(response)
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
        #console.log(response)
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

def meraki_get_network_insight_applications(meraki_org_id):
    try:
        url = f"https://{meraki_base_url}/organizations/{meraki_org_id}/insight/applications"

        payload = {}
        headers = {
        'X-Cisco-Meraki-API-Key': f'{meraki_api_key}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        #console.log(response)
        res = response.json()
        #console.log(res)
        if response.status_code == 200:
            #console.log("API Call Successful.")
            #console.log(res)
            application_list = []
            for app in res:
                if app["thresholds"]["type"] == "smart":
                    application_list.append(app)
            return application_list
    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)
                

    

# Section 2: Application Health

"""
Application Health
"""

def meraki_get_application_health_metrics():
    try:
        application_list = []
        meraki_org_id = get_meraki_org_id()
        app_list = meraki_get_network_insight_applications(meraki_org_id)
        total_network_list = get_meraki_network_id(meraki_api_key, meraki_base_url, meraki_org_id)

        for app in app_list:
            app_id = app["applicationId"]
            app_name = app["name"]
            app_network_list = app["thresholds"]["byNetwork"]
            #console.log(app_network_list)
            network_list_len = len(app_network_list)
            if(network_list_len == 0):
                network_list_len = 1

            if len(app_network_list) == 0:
                total_wan_latency = 0
                total_lan_latency = 0
                total_wan_loss_percent = 0
                total_lan_loss_percent = 0
                app_performance_metrics = {}
                app_performance_metrics["application_id"] = app_id
                app_performance_metrics["application_name"] = app_name

            if len(app_network_list)!=0:
                total_wan_latency = 0
                total_lan_latency = 0
                total_wan_loss_percent = 0
                total_lan_loss_percent = 0
                app_performance_metrics = {}
                app_performance_metrics["application_id"] = app_id
                app_performance_metrics["application_name"] = app_name
                
        
            for network in total_network_list:
                net_id = network

                url = f"https://{meraki_base_url}/networks/{net_id}/insight/applications/{app_id}/healthByTime"

                payload = {}
                headers = {
                'X-Cisco-Meraki-API-Key': f'{meraki_api_key}'
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                #console.log(response)
                res = response.json()
                #console.log(res)
                if response.status_code == 200:
                    if len(res)!=0:
                        app_performance = res[0]
                        app_perf_wan_latency = app_performance["wanLatencyMs"]
                        app_perf_lan_latency = app_performance["lanLatencyMs"]
                        app_perf_wan_loss_percent = app_performance["wanLossPercent"]
                        app_perf_lan_loss_percent = app_performance["lanLossPercent"]

                        total_wan_latency = int(total_wan_latency) + int(float(app_perf_wan_latency))
                        total_lan_latency = total_lan_latency + int(float(app_perf_lan_latency))
                        total_wan_loss_percent = total_wan_loss_percent + int(float(app_perf_wan_loss_percent))
                        total_lan_loss_percent = total_lan_loss_percent + int(float(app_perf_lan_loss_percent))
        
            #console.log(total_wan_latency/network_list_len)
            app_performance_metrics["avg_wan_latency"] = total_wan_latency/network_list_len
            app_performance_metrics["avg_lan_latency"] = total_lan_latency/network_list_len
            app_performance_metrics["avg_wan_loss_percentage"] = total_wan_loss_percent/network_list_len
            app_performance_metrics["avg_lan_loss_percentage"] = total_lan_loss_percent/network_list_len
            if(app_performance_metrics["avg_wan_latency"] > 100) or (app_performance_metrics["avg_wan_loss_percentage"] > 0) or (app_performance_metrics["avg_lan_latency"] > 100) or (app_performance_metrics["avg_lan_loss_percentage"] > 0):
                app_performance_metrics["status"] = "Poor"
            else:
                app_performance_metrics["status"] = "Good"
            application_list.append(app_performance_metrics)
        #get average score for app performance with Good given a score of 1 and Poor given a score of 0
        total_score = 0
        for app in application_list:
            if app["status"] == "Good":
                total_score = total_score + 1
        avg_score = total_score/len(application_list)
        app_performance_metrics = {}
        app_performance_metrics["avg_score"] = avg_score
        app_performance_metrics["details"]  = application_list
        return app_performance_metrics


    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)
                

def create_app_health_data_model():
    meraki_app_health = meraki_get_application_health_metrics()
    app_health_data_model = [
        {"meraki_app_health":meraki_app_health},
        {"te_app_health":te.testresults()}
    ]
    return app_health_data_model

if __name__ == "__main__":
    pprint(create_app_health_data_model())