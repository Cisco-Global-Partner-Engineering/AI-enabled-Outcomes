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

import CatalystCenter_auth
from pprint import pprint



def get_networkhealth():
    """
    Get network health from DNAC

    params:  none

    Returns: json: json response from Dnac

    example:
            {'networkHealth': 1}    
        
    """
    returnData = {}
    data = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/network-health")['response'][0]
    if(data["healthScore"]>99):
        returnData['networkHealth'] = 1
    elif(data["healthScore"]>0 and data["healthScore"]<100 ):
        returnData['networkHealth'] = -1
    else:
        returnData['networkHealth'] = 0
    return returnData


def get_devicehealth():
    """
    Get device health from DNAC

    params:  none

    Returns: json: json response from Dnac

    example:
            [{'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.4',
                  'name': 'CPS-Edge1',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=d372d4cc-8a2a-4e2b-8829-90d490d608d5',
                  'uuid': 'd372d4cc-8a2a-4e2b-8829-90d490d608d5'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.7',
                  'name': 'DC-Switch.demo.local',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=5e06830b-bec7-4f9d-ba03-1f920ec8b0f4',
                  'uuid': '5e06830b-bec7-4f9d-ba03-1f920ec8b0f4'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.3',
                  'name': 'CPS-L2Border',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=ff8a6102-46d7-4d1d-8a13-ae60d6f29567',
                  'uuid': 'ff8a6102-46d7-4d1d-8a13-ae60d6f29567'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.5',
                  'name': 'CPS-Edge2',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=4c9a1371-86f1-4d6b-b9ba-3f7ea7f669f9',
                  'uuid': '4c9a1371-86f1-4d6b-b9ba-3f7ea7f669f9'},
                 {'deviceFamily': 'routers',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.19',
                  'name': 'Appx_CSR1Kv',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=77a3cf63-15c5-4d7f-ad3e-d68ee40660ed',
                  'uuid': '77a3cf63-15c5-4d7f-ad3e-d68ee40660ed'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.2',
                  'name': 'CPS-BDR',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=69e325d0-fc08-4e13-ab40-3aacb8ad915a',
                  'uuid': '69e325d0-fc08-4e13-ab40-3aacb8ad915a'}]]
    """
    itemData = {}
    returnData = []
    data = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/device-health")['response']
    for item in data:
        itemData["name"] = item["name"]
        itemData["deviceFamily"] = item["deviceFamily"].lower()
        itemData["reachabilityHealth"] = item["reachabilityHealth"].lower()
        itemData["ipAddress"] = item["ipAddress"]
        if(item["overallHealth"]>9):
            itemData['deviceHealth'] = "positive"
        elif(item["overallHealth"]>0 and item["overallHealth"]<10):
            itemData['deviceHealth'] = "moderate"
        else:
            itemData['deviceHealth'] = "critical"
        query = {
            "searchBy": item["macAddress"],
            "identifier": "macAddress"
        }
        detailData = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/device-detail", query=query)['response']
        itemData['url'] = CatalystCenter_auth.BASE_URL + "/dna/assurance/device/details?id=" + detailData["nwDeviceId"]
        itemData["uuid"] = detailData["nwDeviceId"]
        returnData.append(itemData.copy())
    return returnData

""" def get_platformhealth():
    data = Dnac_auth.get_data(uri="/dna/intent/api/v1/diagnostics/system/health")
    pprint(data) """

    


def get_data():
    """
    Combine all health data from DNAC

    params:  none

    Returns: list: list of json response from Dnac

    example: 
            [{'networkHealth': 1},
                [{'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.4',
                  'name': 'CPS-Edge1',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=d372d4cc-8a2a-4e2b-8829-90d490d608d5',
                  'uuid': 'd372d4cc-8a2a-4e2b-8829-90d490d608d5'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.7',
                  'name': 'DC-Switch.demo.local',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=5e06830b-bec7-4f9d-ba03-1f920ec8b0f4',
                  'uuid': '5e06830b-bec7-4f9d-ba03-1f920ec8b0f4'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.3',
                  'name': 'CPS-L2Border',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=ff8a6102-46d7-4d1d-8a13-ae60d6f29567',
                  'uuid': 'ff8a6102-46d7-4d1d-8a13-ae60d6f29567'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.5',
                  'name': 'CPS-Edge2',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=4c9a1371-86f1-4d6b-b9ba-3f7ea7f669f9',
                  'uuid': '4c9a1371-86f1-4d6b-b9ba-3f7ea7f669f9'},
                 {'deviceFamily': 'routers',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.19',
                  'name': 'Appx_CSR1Kv',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=77a3cf63-15c5-4d7f-ad3e-d68ee40660ed',
                  'uuid': '77a3cf63-15c5-4d7f-ad3e-d68ee40660ed'},
                 {'deviceFamily': 'switches_and_hubs',
                  'deviceHealth': 'positive',
                  'ipAddress': '192.168.1.2',
                  'name': 'CPS-BDR',
                  'reachabilityHealth': 'reachable',
                  'url': 'https://10.1.100.4/dna/assurance/device/details?id=69e325d0-fc08-4e13-ab40-3aacb8ad915a',
                  'uuid': '69e325d0-fc08-4e13-ab40-3aacb8ad915a'}]]

    """
    data = [get_networkhealth(), get_devicehealth()]
    return data    



if __name__ == "__main__":
    pprint(get_data())
