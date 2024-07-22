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

console = Console()

load_dotenv()

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


# Meraki Credentials
meraki_base_url = os.getenv("MERAKI_BASE_URL")
meraki_api_key = os.getenv("MERAKI_API_KEY")
#meraki_network_id = os.getenv("MERAKI_NETWORK_ID")
#meraki_org_id = os.getenv("MERAKI_ORG_ID")

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

    

# Section 1: Alerts
# Meraki Webhook Alerts
# ThousandEyes Active Alerts
# Umbrella Intrusion Alerts 


"""
Alert Levels: 
"""
meraki_informational_alerts = ['sensor_magnetic_tampering_reset', 'sensor_probe_cable_reconnected', 'sensor_usb_power_cable_reconnected', 'sensor_water_cable_reconnected', 'settings_changed', 'started_reporting', 'usage_alert', 'port_speed_change', 'power_supply_up', 'rogue_ap_association', 'rps_base_supply_up', 'sensor_alert', 'sensor_alert_test', 'sensor_automation', 'sensor_automation_test', 'sensor_battery_cover_replaced', 'sensor_battery_improved', 'motion_alert', 'new_splash_signup', 'pcc_enrollment', 'pcc_expired_apns_cert', 'pcc_security_compliance', 'pcc_sw_found', 'port_connected', 'bluetooth_out', 'cellular_up', 'dhcp_no_leases', 'geofencing_in', 'bluetooth_in']
meraki_warning_alerts = ['sensor_probe_cable_disconnected', 'sensor_usb_power_cable_disconnected', 'sensor_water_cable_disconnected', 'udld_error', 'umbrella_expiring', 'unreachable_radius_server', 'uplink_ip6_conflict', 'vpn_connectivity_change', 'amp_malware_blocked', 'port_disconnected', 'prefix_starvation', 'rogue_dhcp', 'rps_backup', 'sensor_battery_cover_removed', 'sensor_battery_low', 'sensor_magnetic_tampering_detected', 'analyzed_app_network_insight_performance_alert', 'ip6_conflict', 'ip_conflict', 'mi_alert', 'pcc_outage_begin', 'pcc_outage_end', 'pcc_security_violation', 'pcc_unmanaged', 'port_cable_error', 'cellular_down', 'client_connectivity', 'cloud_archive_alert', 'dhcp6na_renumber', 'dhcp6pd_renumber', 'dhcp_alerts', 'failover_event', 'firewall_test_failed', 'gateway_to_repeater', 'geofencing_out', 'amp_malware_detected', 'foreign_ap', 'rogue_ap', 'Unreachable device']
meraki_critical_alerts = ['stopped_reporting', 'vrrp', 'power_supply_down', 'node_hardware_failure', 'critical_temperature']

def meraki_get_network_alerts(meraki_network_id):
    try:
        url = f"https://{meraki_base_url}/networks/{meraki_network_id}/health/alerts"
        #url = f"https://{meraki_base_url}/networks/{meraki_network_id}/alerts/history"

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
            meraki_alert_details = {}
            meraki_alert_details["informational"] = None
            meraki_alert_details["warning"] = None
            meraki_alert_details["critical"] = None

            return meraki_alert_details

        if response.status_code == 200:
            #console.log(res)
            meraki_alert_details = {}
            informational_count = 0
            warning_count = 0
            critical_count = 0 
            meraki_alert_details["alert_data"] = []
            #console.log("API call successful.")
            if len(res) == 0:
                meraki_alert_details["informational"] = 0
                meraki_alert_details["warning"] = 0
                meraki_alert_details["critical"] = 0

                return meraki_alert_details
            
            for alert in res:
                #console.log(alert)
                data = {}
                data["id"] = alert["id"]
                data["category"] = alert["category"]
                data["type"] = alert["type"]
                #data["device_name"] = alert["device"]["name"]
                #data["device_serial"] = alert["device"]["serial"]
                data["details"] = alert["scope"]["devices"]

                if(alert["type"] in meraki_informational_alerts):
                        alert_severity = "informational"
                        data["severity"] = alert_severity
                        informational_count += 1
                elif(alert["type"] in meraki_warning_alerts):
                        alert_severity = "warning"
                        data["severity"] = alert_severity
                        warning_count += 1
                elif(alert["type"] in meraki_critical_alerts):
                        alert_severity = "critical"
                        data["severity"] = alert_severity
                        critical_count += 1
                data["URL"] = "NA"
                meraki_alert_details["alert_data"].append(data)
            meraki_alert_details["informational"] = informational_count
            meraki_alert_details["warning"] = warning_count
            meraki_alert_details["critical"] = critical_count

            #console.log(meraki_alert_details)  
         
            return meraki_alert_details    

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)

def te_get_active_alerts():
    try:
        #url = f"https://{te_base_url}/v6/alerts.json"
        url = f"https://{te_base_url}/v7/alerts"
        headers = {}
        headers = {"Authorization": "Bearer " + te_token}
        response = requests.get(url, headers=headers, params={"format":"json"}, verify=False)
        res = response.json()

        if response.status_code != 200:
            console.log(f"{logging.info('Error with API Request')}")
            console.log(f"Status Code: {response.status_code}")
            console.log(f"Pushing null values to database.")
            te_alert_details = {}
            te_alert_details["informational"] = 0
            te_alert_details["warning"] = 0
            te_alert_details["critical"] = 0

            return te_alert_details

        if response.status_code == 200:
            #console.log("API Call Successful.")
            #console.log(res)
            informational_count = 0
            warning_count = 0
            critical_count = 0 
            te_alert_details = {}
            if len(res["alerts"]) == 0:
                te_alert_details["alert_data"] = [{"severity":"informational","type":"Agents UP","details":"NA"}]
                te_alert_details["informational"] = 1
                te_alert_details["warning"] = 0
                te_alert_details["critical"] = 0
                #console.log(te_alert_details)
                return te_alert_details
            te_alert_details["alert_data"] = []
            alert_array = res["alert"]
            for alert in alert_array:
                data = {}
                data["severity"] = alert["severity"]
                data["alertId"] = alert["alertId"]
                data["testName"] = alert["testName"]
                data["type"] = alert["type"]
                data["permalink"] = alert["permalink"]

                if alert["severity"] == "INFO":
                    informational_count+=1
                    te_alert_details["alert_data"].append(data) 
                elif alert["severity"] == "MINOR" or alert["severity"] == "MAJOR":
                    warning_count+=1
                    te_alert_details["alert_data"].append(data)
                elif alert["severity"] == "CRITICAL":
                    critical_count+=1
                    te_alert_details["alert_data"].append(data)

            te_alert_details["informational"] = informational_count
            te_alert_details["warning"] = warning_count
            te_alert_details["critical"] = critical_count

            #console.log(te_alert_details)        
            return te_alert_details

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


"""
def umbrella_get_intrusion_alerts():
    try:
        # Umbrella Authentication
        access_token = umbrella_auth()

        url = f"https://{umbrella_base_url}/reports/v2/activity/intrusion?from=1700548089&to=1700807289&limit=100"
        payload = {}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.request("GET", url, headers=headers, data=payload)
        res = response.json()

        if response.status_code == 200:
            console.log("API Call Successful.")
            console.log(res["data"])
            informational_count = 0
            warning_count = 0
            critical_count = 0 
            umbrella_alert_details = {}
            if len(res["data"]) == 0:
                umbrella_alert_details["informational"] = None
                umbrella_alert_details["warning"] = None
                umbrella_alert_details["critical"] = None
                #console.log(umbrella_alert_details)
                return umbrella_alert_details
            umbrella_alert_details["alert_data"] = []
            alert_array = res["data"]
            for alert in alert_array:
                data = {}
                data["severity"] = alert["severity"]
                data["classification"] = alert["classification"]
                data["timestamp"] = alert["timestamp"]
                data["sessionid"] = alert["sessionid"]

                if alert["severity"] == "Very Low" or alert["severity"] == "Low":
                    informational_count+=1
                    umbrella_alert_details["alert_data"].append(data) 
                elif alert["severity"] == "Medium":
                    warning_count+=1
                    umbrella_alert_details["alert_data"].append(data)
                elif alert["severity"] == "High":
                    critical_count+=1
                    umbrella_alert_details["alert_data"].append(data)

            umbrella_alert_details["informational"] = informational_count
            umbrella_alert_details["warning"] = warning_count
            umbrella_alert_details["critical"] = critical_count

            #console.log(umbrella_alert_details)        
            return umbrella_alert_details
            

    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)
"""

def umbrella_get_tunnel_state_information():
    try:
        # Umbrella Authentication
        access_token = umbrella_auth()

        url = f"https://{umbrella_base_url}/deployments/v2/tunnelsState"
        payload = {}
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.request("GET", url, headers=headers, data=payload)
        res = response.json()
        #console.log(res)
        #console.log(response.status_code)

        if response.status_code != 200:
            console.log(f"{logging.info('Error with API Request')}")
            console.log(f"Status Code: {response.status_code}")
            console.log(f"Pushing null values to database.")
            umbrella_tunnel_state_details = {}
            umbrella_tunnel_state_details["informational"] = None
            umbrella_tunnel_state_details["warning"] = None
            umbrella_tunnel_state_details["critical"] = None

            return umbrella_tunnel_state_details

        if response.status_code == 200:
            #console.log(res)
            #console.log("API Call Successful.")
            #console.log(res)
            informational_count = 0
            warning_count = 0
            critical_count = 0 
            umbrella_tunnel_state_details = {}
            if len(res) == 0:
                console.log("length of res is 0.")
                umbrella_tunnel_state_details["informational"] = 0
                umbrella_tunnel_state_details["warning"] = 0
                umbrella_tunnel_state_details["critical"] = 0
                return umbrella_tunnel_state_details

            umbrella_tunnel_state_details["alert_data"] = []
            alert_array = res
            for alert in alert_array:
                data = {}
                data["tunneId"] = alert["tunnelId"]
                data["status"] = alert["status"]
                data["modifiedAt"] = alert["modifiedAt"]
                
                if data["status"].lower() == "down" or data["status"].lower() == "unknown":
                    warning_count = warning_count + 1
                    umbrella_tunnel_state_details["alert_data"] = [{"severity":"warning","type":"Tunnel unkown","details":alert}]
                    #umbrella_tunnel_state_details["alert_data"].append(data)
                
                elif data["status"].lower() == "failed":
                    critical_count = critical_count + 1
                    umbrella_tunnel_state_details["alert_data"] = [{"severity":"critical","type":"Tunnel DOWN","details":alert}]
                    #umbrella_tunnel_state_details["alert_data"].append(data)
                elif data["status"].lower() == "up":
                    informational_count = informational_count + 1
                    umbrella_tunnel_state_details["alert_data"] = [{"severity":"informational","type":"Tunnel UP","details":alert}]
                    #umbrella_tunnel_state_details["alert_data"].append(data)

                umbrella_tunnel_state_details["informational"] = informational_count
                umbrella_tunnel_state_details["warning"] = warning_count
                umbrella_tunnel_state_details["critical"] = critical_count


            return umbrella_tunnel_state_details



    except HTTPError as http:
        print(http)
    except Exception as ex:
        print(ex)


"""
result1 = meraki_get_network_alerts()
result2 = te_get_active_alerts()
result3 = umbrella_get_tunnel_state_information()


console.log("Meraki")
console.log(result1)

console.log("ThousandEyes")
console.log(result2)

console.log("Umbrella")
console.log(result3)
"""

def get_meraki_alerts():
    meraki_alerts = []
    meraki_org_id = get_meraki_org_id()
    meraki_network_ids = get_meraki_network_id(meraki_api_key, meraki_base_url, meraki_org_id)
    for networkid in meraki_network_ids:
        #console.log(networkid)
        result = meraki_get_network_alerts(networkid)
        if(result):
            meraki_alerts.append(result)
    aggregated_alerts = {'alert_data': [], 'informational': 0, 'warning': 0, 'critical': 0}
    for alert in meraki_alerts:
        aggregated_alerts['alert_data'].extend(alert['alert_data'])
        aggregated_alerts['informational'] += alert['informational']
        aggregated_alerts['warning'] += alert['warning']
        aggregated_alerts['critical'] += alert['critical']

    return aggregated_alerts

def create_alerts_data_model():

    meraki_alerts = get_meraki_alerts()
    umbrella_alerts = umbrella_get_tunnel_state_information()
    te_alerts = te_get_active_alerts()

    alert_data_model = []

    alert_data_model.append({"meraki_alerts": meraki_alerts})
    alert_data_model.append({"umbrella_alerts": umbrella_alerts})
    alert_data_model.append({"te_alerts": te_alerts})
    alert_data_model.append({"timestamp": time.time()})

    #console.log(alert_data_model)
    return alert_data_model

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


if (__name__ == "__main__"):
    print(create_alerts_data_model())