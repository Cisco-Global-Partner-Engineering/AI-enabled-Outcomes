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
import thousandEyesAppHealth
#import dbnotifications


def runme():
    """This function is used to push data to the database
    parameters: None
    returns: None
    """
    db = mongodb_auth.authenticatedb()

    response = requests.get("http://127.0.0.1:5555/data")
    data = response.json()["data"]
    print("completed getting data from ControllerREST..")

    #dbnotifications.runme(dataparam=data)

    vManageHealth_data = data["vManageHealth"]


    DnacHealth_data = data["DnacHealth"]
    vManageNWPI_readTrace_sloDetails = data["vManageNWPI_readTrace"][0]
    vManageNWPIAppHealth_data = data["vManageNWPI_readTrace"][1]
    DnacAppHealth_data = data["DnacAppHealth"]
    thousandEyesAppHealth_data = thousandEyesAppHealth.get_data()
    AppHealth_data = vManageNWPIAppHealth_data
    if(vManageNWPIAppHealth_data==[] and DnacAppHealth_data==[] and vManageNWPI_readTrace_sloDetails==[]):
        AppHealth_data = [{"health":"green","name":"all","events":["positive"]}]
    tmp = {}
    result = int(vManageHealth_data[0]["networkHealth"]) * int(DnacHealth_data[0]["networkHealth"])
    if(result == 0):
        tmp["NetworkHealth"] = "critical"
    elif(result == -1):
        tmp["NetworkHealth"] = "moderate"
    else:
        tmp["NetworkHealth"] = "positive"    
    vManageAlarms_data = data["vManageAlarms"]
    DnacAlarms_data = data["DnacAlarms"]
   
    
    collection = db['NetworkHealth']
    print("NetworkHealth : ",mongodb_auth.purge_collection(collection))
    data = [tmp]
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")

    collection = db['DeviceHealth']
    print("DeviceHealth : ",mongodb_auth.purge_collection(collection))
    data = vManageHealth_data[1]
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")
    data = DnacHealth_data[1]
    print("Added",mongodb_auth.addData(data,collection),"documents to collection.")

    collection = db['ApplicationHealth']
    print("ApplicationHealth : ", mongodb_auth.purge_collection(collection))
    data = AppHealth_data
    if(data!=[]):
        print("Added",mongodb_auth.addData(data,collection),"documents to collection.")
    data = vManageNWPI_readTrace_sloDetails
    if(data!=[]):
        print("Added",mongodb_auth.addData(data,collection),"documents to collection.")
    data = DnacAppHealth_data
    if(data!=[]):
        print("Added",mongodb_auth.addData(data,collection),"documents to collection.")
    data = thousandEyesAppHealth_data
    if(data!=[]):
        print(mongodb_auth.addData(data,collection))
    
    if(vManageAlarms_data==[] and  DnacAlarms_data==[]):
        DnacAlarms_data = {"severity":"positive"}
    collection = db['Alarms']
    print("Alarms : ", mongodb_auth.purge_collection(collection))
    data = DnacAlarms_data
    if(data!=[]):
        print("Added",mongodb_auth.addData(data,collection),"documents to collection.")
    data = vManageAlarms_data
    if(data!=[]):
        print("Added",mongodb_auth.addData(data,collection),"documents to collection.")
        

if __name__ == "__main__":
    runme()

