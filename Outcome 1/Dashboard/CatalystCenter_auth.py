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

import requests
from requests.auth import HTTPBasicAuth
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pprint import pprint
import credentials

BASE_URL = 'https://cisco.msp-dnac.dc-01.com'
AUTH_URL = '/dna/system/api/v1/auth/token'
USERNAME = credentials.DNAC_USERNAME
PASSWORD = credentials.DNAC_PASSWORD 


def get_data(uri,header=None, query=None):
    """
    Get data from Dnac using the uri and query provided
    
    params:   
            uri (str): uri to get data from
            header (dict): header to be passed to the uri (optional)
            query (dict): query to be passed to the uri (optional)
    
    Returns: 
            json: json response from Dnac
    """
    
    response = requests.post(BASE_URL + AUTH_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    token = response.json()['Token']
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    while True:
        url = BASE_URL + uri
        if(header):
            headers.update(header)
        response = requests.get(url, headers=headers, params=query, verify=False)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print("Exception raised : ",e)
                continue
        elif(response.status_code == 429):
            print("got response 429 from Dnac, retrying in 60 seconds..")
            time.sleep(60)
            continue
        else:
            print(response, response.text)
            continue

def post_data(uri, body=None):
    """
    Post data to Dnac using the uri and body provided

    params:
            uri (str): uri to post data to
            body (dict): body to be passed to the uri (optional)

    Returns:
            json: json response from Dnac
    """
    
    response = requests.post(BASE_URL + AUTH_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    token = response.json()['Token']
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    url = BASE_URL + uri
    response = requests.post(url,headers=headers,json=body,verify=False)
    if response.status_code == 202:
        return response.json()
    else:
        print("error while posting data : ", response, response.json())
        return False


if __name__ == "__main__":
    print("device-health : ")
    data = get_data(uri="/dna/intent/api/v1/device-health")['response']
    pprint(data)
    print("device-details : ")
    for item in data:
        query = {
            "searchBy": item["macAddress"],
            "identifier": "macAddress"
        }
        print(query)
        pprint(get_data(uri="/dna/intent/api/v1/device-detail", query=query))
