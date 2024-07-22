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

import mongodb_auth
import requests
from pprint import pprint

def runme():
    """This function is used to push data to the database
    parameters: None
    returns: None
    """

    db = mongodb_auth.authenticatedb()

    response = requests.get("http://127.0.0.1:5555/data")
    data = response.json()["data"]
    print("completed getting data from ControllerREST..")

    alerts = data["Alerts"]
    infra_health = data["Infra_Health"]
    app_health = data["App_Health"]
    top_threats = data["Top_Threats"]

    collection = db['Alerts']
    print("Alerts : ",mongodb_auth.purge_collection(collection))
    data = alerts
    if(len(data)==0):
        print("No data to push to the database.")
        return
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")

    
    collection = db['Infra_Health']
    print("Infra_Health : ",mongodb_auth.purge_collection(collection))
    data = infra_health
    if(len(data)==0):
        print("No data to push to the database.")
        return
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")

    
    print("len of data", len(data))
    collection = db['App_Health']
    print("App_Health : ",mongodb_auth.purge_collection(collection))
    data = app_health
    if(len(data)==0):
        print("No data to push to the database.")
        return
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")

    
    collection = db['Top_Threats']
    print("Top_Threats : ",mongodb_auth.purge_collection(collection))
    data = top_threats
    if(len(data)==0):
        print("No data to push to the database.")
        return
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")



if __name__ == "__main__":
    runme()

