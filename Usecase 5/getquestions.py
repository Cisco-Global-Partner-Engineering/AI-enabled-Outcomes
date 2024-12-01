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

import json
from pprint import pprint

def getquestions(n=-1):
    with open("data/doc_qa.json","r") as f:
        data = json.load(f)

    result = []
    count = 0
    if n == -1:
        n = len(data)
    # Iterate through all data
    for item in data:
        result.append(item["question"])
        if count == n:
            break
    return result

if __name__=="__main__":
    pprint(getquestions())