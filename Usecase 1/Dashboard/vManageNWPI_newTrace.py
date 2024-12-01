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
import time

#We are hardcoding the VLANID as we cannot have more than 2 vlanid per site for the nwpi trace
sitevlan = [{'300':['10']},{'300':['20']}]


def traceexists():
    data = vManage_auth.get_data("/dataservice/stream/device/nwpi/traceHistory")["data"]
    for items in data:  
        for item in items["data"]["devices"]:
            if(item["state"]=="running"):
                return True
            else:
                return False


def startnewtrace():
    milliseconds = str(int((time.time() % 1) * 10000))
    last_four_digits = milliseconds[-4:]

    for item in sitevlan:
        for key in item.keys():
            for vpnid in item[key]:
                postparam = {
                "source-site": key,
                "vpn-id": vpnid,
                "duration": "60",
                "trace-name": key + "-" + vpnid + "-" + last_four_digits 
                }
                data = vManage_auth.post_data("/dataservice/stream/device/nwpi/trace/start", param=postparam)
                print(postparam, data)

if __name__ == "__main__":
    while True:
        if(traceexists()):
            print("trace is running.. sleeping for 300 seconds before retrying..")
            time.sleep(300)
        else:
            startnewtrace()
            print("sleeping for 30 seconds before checking the tracehistory for confirmation of trace start..")
            time.sleep(30)