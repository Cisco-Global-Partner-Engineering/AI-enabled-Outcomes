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


azure_endpoint=""
azure_openai_gpt41_token = ""
azure_openai_gpto4mini_token = ""
webex_access_token = ""
openrouter_key = ""


#################################

# Device credentials structure
devices = [
    {
        "name": "branch-router",
        "type": " IOS virtual Router",
        "ip": "198.18.1.100",
        "username": "",
        "password": "",
        "enable_password": "",
        "port": 22,
    },
    {
        "name": "branch-fw",
        "type": " virtual ASA Firewall",
        "ip": "198.18.1.109",
        "username": "",    
        "password": "",
        "enable_password": "",
        "port": 22,
    },
    {
        "name": "branch-switch",
        "type": " IOS Layer 2 virtual Switch", 
        "ip": "198.18.1.104",
        "username": "",
        "password": "",
        "enable_password": "", 
        "port": 22,
    },
     {
        "name": "client-switch",
        "type": " IOS Layer 2 virtual Switch",  
        "ip": "198.18.1.107",
        "username": "",
        "password": "",
        "enable_password": "", 
        "port": 22,
    },
    {
        "name": "client1",
        "type": "alpine virtual linux",
        "ip": "198.18.1.111",
        "username": "",
        "password": "",
        "port": 22,
    },
    {
        "name": "client2",
        "type": "alpine virtual linux",
        "ip": "198.18.1.112",
        "username": "",
        "password": "",
        "port": 22,
    },
    {
        "name": "client1-switch",
        "type": " IOS Layer 2 virtual Switch", 
        "ip": "198.18.1.105",
        "username": "",
        "password": "",
        "enable_password": "", 
        "port": 22,
    },
    {
        "name": "client2-switch",
        "type": " IOS Layer 2 virtual Switch",
        "ip": "198.18.1.106",
        "username": "",
        "password": "",
        "enable_password": "", 
        "port": 22,
    },
    {
        "name": "client1-router",
        "type": " IOS virtual Router", 
        "ip": "198.18.1.101",
        "username": "",
        "password": "",
        "enable_password": "", 
        "port": 22,
    },
    {
        "name": "client2-router",
        "type": " IOS virtual Router", 
        "ip": "198.18.1.114",
        "username": "",
        "password": "",
        "enable_password": "",
        "port": 22,
    },
    {
        "name": "dmz-router",
        "type": " IOS virtual Router",
        "ip": "198.18.1.103",
        "username": "",
        "password": "",
        "enable_password": "",
        "port": 22,
    },
    {
        "name": "dmz-fw",
        "type": " virtual ASA Firewall",
        "ip": "198.18.1.110",
        "username": "",
        "password": "",
        "enable_password": "",
        "port": 22,
    },
    {
        "name": "server-switch",
        "type": " IOS Layer 2 virtual Switch",
        "ip": "198.18.1.108",
        "username": "",
        "password": "",
        "enable_password": "",
        "port": 22,
    },
    {
        "name": "server",
        "type": "alpine virtual linux",
        "ip": "198.18.1.113",
        "username": "",
        "password": "",
        "port": 22,
    },
    {
        "name": "remote-worker",
        "type": "alpine virtual linux",
        "ip": "198.18.1.115",
        "username": "",
        "password": "",
        "port": 22,
    }

]