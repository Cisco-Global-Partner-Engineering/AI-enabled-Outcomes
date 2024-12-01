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


fiveTuple = [ 
    {"sourceIP":"172.16.1.200",
     "sourcePort":"9999",
     "destIP":"121.10.10.2",
     "destPort":"8888",
     "protocol":"tcp"
     }

    ]


def do_pathtrace():
   for item in fiveTuple:
      data=CatalystCenter_auth.post_data(uri="/dna/intent/api/v1/flow-analysis",body=item)
      pprint(data)

def get_pathtracehistory():
   data = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/flow-analysis")["response"]
   for item in data:
      if(item["status"]=="COMPLETED"):
        return(item["id"])

def get_pathtracedetails():
   uri = "/dna/intent/api/v1/flow-analysis/" + get_pathtracehistory()
   data = CatalystCenter_auth.get_data(uri=uri)["response"]
   pprint(data)


if __name__ == "__main__":
    pprint(get_pathtracedetails())