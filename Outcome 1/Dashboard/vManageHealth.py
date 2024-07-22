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
    """
    Returns a list of dictionaries containing the health of the network and the devices in the network.
    The first dictionary contains the health of the network and the second dictionary contains the health of the devices.
    The health of the network is determined by the health of the devices in the network.
    The health of the devices is determined by the reachability of the devices.
    
    param:      None
    
    Returns:    [dict, list]
                [networkHealth, deviceHealth]

    Example:
                [{'networkHealth': 0},
                   [{'deviceFamily': 'vedge',
                     'deviceHealth': 'positive',
                     'ipAddress': '1.2.3.4',
                     'name': 'DC-8kv',
                     'reachabilityHealth': 'reachable',
                     'url': 'https://10.1.100.11/?_open=ext#/app/monitor/devices/dashboard/health?systemIp=1.2.3.4&localSystemIp=1.2.3.4&device-model=vedge&uuid=C8K-PAYG-ece-0a57-46cd-bb14-d39a30cae7cd',
                     'uuid': 'C8K-PAYG-ece-0a57-46cd-bb14-d39a30cae7cd'},
                    {'deviceFamily': 'vedge',
                     'deviceHealth': 'critical',
                     'ipAddress': '100.100.100.100',
                     'name': 'CPS-WANEgde1',
                     'reachabilityHealth': 'reachable',
                     'url': 'https://10.1.100.11/?_open=ext#/app/monitor/devices/dashboard/health?systemIp=100.100.100.100&localSystemIp=100.100.100.100&device-model=vedge&uuid=CSR-337C2D1B-3F54-F921-BCD6-043219E2FC9B',
                     'uuid': 'CSR-337C2D1B-3F54-F921-BCD6-043219E2FC9B'},
                    {'deviceFamily': 'vedge',
                     'deviceHealth': 'moderate',
                     'ipAddress': '100.0.0.10',
                     'name': 'RS1001-BR-WAN1',
                     'reachabilityHealth': 'reachable',
                     'url': 'https://10.1.100.11/?_open=ext#/app/monitor/devices/dashboard/health?systemIp=100.0.0.10&localSystemIp=100.0.0.10&device-model=vedge&uuid=ISR4331/K9-FDO2116130M',
                     'uuid': 'ISR4331/K9-FDO2116130M'},
                    {'deviceFamily': 'vmanage',
                     'deviceHealth': 'positive',
                     'ipAddress': '11.11.11.11',
                     'name': 'vmanage',
                     'reachabilityHealth': 'reachable',
                     'url': 'https://10.1.100.11/?_open=ext#/app/monitor/devices/dashboard/health?systemIp=11.11.11.11&localSystemIp=11.11.11.11&device-model=vmanage&uuid=a12b3fd2-e367-4ed1-960a-6a56fbb19635',
                     'uuid': 'a12b3fd2-e367-4ed1-960a-6a56fbb19635'},
                    {'deviceFamily': 'vbond',
                     'deviceHealth': 'positive',
                     'ipAddress': '11.11.11.12',
                     'name': 'vBond',
                     'reachabilityHealth': 'reachable',
                     'url': 'https://10.1.100.11/?_open=ext#/app/monitor/devices/dashboard/health?systemIp=11.11.11.12&localSystemIp=11.11.11.12&device-model=vbond&uuid=44a23240-3c4b-49de-8d9b-cd4ba9a4470a',
                     'uuid': '44a23240-3c4b-49de-8d9b-cd4ba9a4470a'},
                    {'deviceFamily': 'vsmart',
                     'deviceHealth': 'positive',
                     'ipAddress': '11.11.11.13',
                     'name': 'vSmart',
                     'reachabilityHealth': 'reachable',
                     'url': 'https://10.1.100.11/?_open=ext#/app/monitor/devices/dashboard/health?systemIp=11.11.11.13&localSystemIp=11.11.11.13&device-model=vsmart&uuid=8e96b807-86cb-4e3c-961b-95a9b5a4d98c',
                     'uuid': '8e96b807-86cb-4e3c-961b-95a9b5a4d98c'}]]

                """
    
    returnData = {}
    deviceData = []
    seen = []
    data = vManage_auth.get_data("/dataservice/device/bfd/sites/detail?state=siteup")["data"]
    for item in data:
        returnData['networkHealth'] = 1
        tmp={}
        tmp["name"] = item["host-name"]
        seen.append(item["host-name"])
        tmp["deviceFamily"] = item["device-type"].lower()
        tmp["reachabilityHealth"] = item["reachability"].lower()
        tmp["ipAddress"] = item["system-ip"]
        tmp["uuid"] = item["uuid"]
        tmp["deviceHealth"] = "positive"
        tmp['url'] = "https://"+vManage_auth.vmanage_ip+"/?_open=ext#/app/monitor/devices/dashboard/health?systemIp="+item["system-ip"]+"&"+ "localSystemIp="+item["local-system-ip"]+"&"+"device-model="+item["device-type"]+"&"+"uuid="+item["uuid"]
        deviceData.append(tmp.copy())
    data = vManage_auth.get_data("/dataservice/device/bfd/sites/detail?state=sitepartial")["data"]
    for item in data:
        returnData['networkHealth'] = -1
        tmp={}
        tmp["name"] = item["host-name"]
        seen.append(item["host-name"])
        tmp["deviceFamily"] = item["device-type"].lower()
        tmp["reachabilityHealth"] = item["reachability"].lower()
        tmp["ipAddress"] = item["system-ip"]
        tmp["uuid"] = item["uuid"]
        tmp["deviceHealth"] = "moderate"
        tmp['url'] = "https://"+vManage_auth.vmanage_ip+"/?_open=ext#/app/monitor/devices/dashboard/health?systemIp="+item["system-ip"]+"&"+ "localSystemIp="+item["local-system-ip"]+"&"+"device-model="+item["device-type"]+"&"+"uuid="+item["uuid"]
        deviceData.append(tmp.copy())
    data = vManage_auth.get_data("/dataservice/device/bfd/sites/detail?state=sitedown")["data"]
    for item in data:
        returnData['networkHealth'] = 0
        tmp={}
        tmp["name"] = item["host-name"]
        seen.append(item["host-name"])
        tmp["deviceFamily"] = item["device-type"].lower()
        tmp["reachabilityHealth"] = item["reachability"].lower()
        tmp["ipAddress"] = item["system-ip"]
        tmp["uuid"] = item["uuid"]
        tmp["deviceHealth"] = "critical"
        tmp['url'] = "https://"+vManage_auth.vmanage_ip+"/?_open=ext#/app/monitor/devices/dashboard/health?systemIp="+item["system-ip"]+"&"+ "localSystemIp="+item["local-system-ip"]+"&"+"device-model="+item["device-type"]+"&"+"uuid="+item["uuid"]
        deviceData.append(tmp.copy())
    data = vManage_auth.get_data("/dataservice/health/devices")["devices"]
    for item in data:
        if(item["name"] not in seen):
            tmp={}
            tmp["name"] = item["name"]
            seen.append(item["name"])
            tmp["deviceFamily"] = item["device_type"].lower()
            tmp["reachabilityHealth"] = item["reachability"].lower()
            tmp["ipAddress"] = item["system_ip"]
            tmp["uuid"] = item["uuid"]
            if(item["health"] == "green"):
                tmp["deviceHealth"] = "positive"
            elif(item["health"] == "yellow"):
                tmp["deviceHealth"] = "moderate"
            elif(item["health"] == "red"):
                tmp["deviceHealth"] = "critical"
            tmp['url'] = "https://"+vManage_auth.vmanage_ip+"/?_open=ext#/app/monitor/devices/dashboard/health?systemIp="+item["system_ip"]+"&"+ "localSystemIp="+item["local_system_ip"]+"&"+"device-model="+item["device_type"]+"&"+"uuid="+item["uuid"]
            deviceData.append(tmp.copy())
    return [returnData, deviceData]



if __name__ == "__main__":
    pprint(get_data())