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

import vManage_auth
from pprint import pprint

def get_data():
    result = []
    query = {"query":{
        "field": "active",
        "type": "boolean",
        "value": ["true"],
        "operator": "equal"
    }}
    data = vManage_auth.get_data("/dataservice/alarms",query2=query)["data"]
    for item in data:
        if(item["acknowledged"]==False and item["active"]==True):
            item["severity"] = item["severity"].lower()
            if('host-name' not in item['values'][0].keys()):
                item['values'][0]['host-name'] = "NA"
            if(item["severity"]=="medium"):
                item["severity"] = "moderate"
            if(item["severity"]=="minor"):
                item["severity"] = "warning"
            result.append({"summary": item["eventname"], "name": item['values'][0]['host-name'], "severity": item["severity"] , "url" : "https://"+vManage_auth.vmanage_ip + "/#/app/monitor/alarms/details/" + str(item["uuid"])})
    return result

if __name__ == "__main__":
    pprint(get_data())
