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

 
def get_data():
    """
    Get application health from DNAC

    params: 
                none

    Returns:
                json: json response from Dnac

    example:
                [{'events': 'health: 5, packetLossPercent: 60, '
                              'networkLatency: 84, Jitter: None',
                    'health': 'critical',
                    'name': 'http',
                    'url': 'https://10.1.100.4/dna/assurance/application/details?id=http&siteId=4f885bef-c58b-4daf-8e1e-f71576b69721'},
                   {'events': 'health: 5, packetLossPercent: 58, '
                              'networkLatency: 3, Jitter: None',
                    'health': 'critical',
                    'name': 'ssl',
                    'url': 'https://10.1.100.4/dna/assurance/application/details?id=ssl&siteId=4f885bef-c58b-4daf-8e1e-f71576b69721'},
                   {'events': 'health: 1, packetLossPercent: 80, '
                              'networkLatency: 599, Jitter: None',
                    'health': 'critical',
                    'name': 'binary-over-http',
                    'url': 'https://10.1.100.4/dna/assurance/application/details?id=binary-over-http&siteId=4f885bef-c58b-4daf-8e1e-f71576b69721'},
                   {'events': 'health: 1, packetLossPercent: 50, '
                              'networkLatency: 2, Jitter: None',
                    'health': 'critical',
                    'name': 'google-play',
                    'url': 'https://10.1.100.4/dna/assurance/application/details?id=google-play&siteId=4f885bef-c58b-4daf-8e1e-f71576b69721'},
                   {'events': 'health: 5, packetLossPercent: 45, '
                              'networkLatency: 2, Jitter: None',
                    'health': 'critical',
                    'name': 'google-services',
                    'url': 'https://10.1.100.4/dna/assurance/application/details?id=google-services&siteId=4f885bef-c58b-4daf-8e1e-f71576b69721'},
                   {'events': 'health: 5, packetLossPercent: 76, '
                              'networkLatency: 5, Jitter: None',
                    'health': 'critical',
                    'name': 'ocsp',
                    'url': 'https://10.1.100.4/dna/assurance/application/details?id=ocsp&siteId=4f885bef-c58b-4daf-8e1e-f71576b69721'}]

    """
    result = []
    siteid=[]
    tmp = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/site")['response']
    for item in tmp:
        siteid.append(item["id"])
    for item in siteid:
        query = {
            "siteId": item
        }
        tmp = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/application-health", query=query)['response']
        for item2 in tmp:
            if(item2["health"]!=None):
                if(item2["health"]<8):
                    if(type(item2["networkLatency"])==float):
                        item2["networkLatency"] = round(item2["networkLatency"])
                    if(type(item2["packetLossPercent"])==float):
                        item2["packetLossPercent"] = round(item2["packetLossPercent"])
                    if(type(item2["jitter"])==float):
                        item2["jitter"] = round(item2["jitter"])


                    result.append({"name":item2["name"],"events": "health: " +str(item2["health"])+ ", packetLossPercent: "+str(item2["packetLossPercent"]) + ", networkLatency: "+str(item2["networkLatency"])+ ", Jitter: "+ str(item2["jitter"]) , "url": CatalystCenter_auth.BASE_URL + "/dna/assurance/application/details?id="+item2["name"]+"&siteId="+item, "health":"critical"})
    return result

if __name__ == "__main__":
    pprint(get_data())

