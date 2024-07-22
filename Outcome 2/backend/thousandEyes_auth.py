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
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()
thousandEyes_token = os.getenv("TE_TOKEN")

def get_data(uri):
     while True:
        url = f"https://api.thousandeyes.com{uri}"
        headers = {"Authorization": "Bearer " + thousandEyes_token}
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

def testresults():
    data = get_data(uri="/v7/tests") 
    results = {}
    results["details"] = []
    results["avg_score"] = 0
    for test in data["tests"]:
        item = get_data(test["_links"]["testResults"][0]['href'].split(".com")[1])
        #pprint(item)
        testresult = 1
        testdetails = {}
        #pprint(item)
        testdetails["details"] = item["results"]
        for i in range(len(item["results"])):
            if(item["results"][i]["errorType"] == 'None'):
                testresult = testresult * 1
            else:
                print("errorType",type(item["results"][i]["errorType"]))
                #print(item["results"][i])
                testresult = testresult * 0
        if(testresult == 1):
            testdetails["status"] = "Test Passed"
        else:
            testdetails["status"] = "Test Failed"
        results["details"].append(testdetails)
    # get average score for test results with Test Passed given a score of 1 and Test Failed given a score of 0
    score = 0
    for i in range(len(results)):
        if(results["details"][i]["status"] == "Test Passed"):
            score = score + 1
    score = score/len(results)
    results["avg_score"]=score

    return results
    


if __name__ == "__main__":
    pprint(testresults())