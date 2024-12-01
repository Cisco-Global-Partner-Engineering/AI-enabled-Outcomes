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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
from pprint import pprint
import credentials

def get_data(uri):
     while True:
        url = f"https://api.thousandeyes.com{uri}"
        headers = {"Authorization": "Bearer " + credentials.thousandEyes_token}
        response = requests.get(url, headers=headers, params={"format":"json"}, verify=False)
        if response.status_code == 200:
            return response.json()
        elif(response.status_code == 429):
            print("got response 429 from ThousandEyes, retrying in 60 seconds..")
            time.sleep(60)
            continue
        else:
            print(response, response.text)
            raise Exception("Failed to get data")


if __name__ == "__main__":
    #pprint(get_data(uri="/v6/web/http-server/3732333"))
    pprint(get_data(uri="/v6/net/metrics/3732333"))

    