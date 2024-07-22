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

import thousandEyes_auth
from pprint import pprint

testids=['3732333']

def get_data():
    apphealth=[]
    for item in testids:
        data = thousandEyes_auth.get_data(uri="/v6/web/http-server/"+item)['web']['httpServer'][0]
        if(data["errorType"]!="None"):
            apphealth.append({"health":"critical","name":"TE agent: "+data["agentName"],"events":data["errorDetails"],"url":data["permalink"]})
        data = thousandEyes_auth.get_data(uri="/v6/net/metrics/"+item)['net']['metrics'][0]
        if(data["loss"]>=5):
            apphealth.append({"health":"critical","name":"TE agent: "+data["agentName"],"events":"packetLoss% "+str(round(data["loss"])),"url":data["permalink"]})
    return apphealth

if __name__ == "__main__":
    pprint(get_data())
