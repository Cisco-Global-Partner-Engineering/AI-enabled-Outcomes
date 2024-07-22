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
from pprint import pprint
import time
#import dbnotifications


def runme():
    response = requests.get("http://127.0.0.1:5555/data")
    if response.status_code ==200:
        data = response.json()["data"]
        #dbnotifications.runme(dataparam=data)
    else:
        return response
    return data



if __name__ == '__main__':
    count = 0
    while(True):
        try:
            pprint(runme())
        except Exception as e:
            print("Exception occured : ",e)
            print("Continuing..")
            continue
        count+=1
        print("dryrun count is : ",count,"\nSleeping for 60 seconds..")
        time.sleep(60)