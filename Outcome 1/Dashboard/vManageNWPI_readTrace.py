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
import datetime
from pprint import pprint

def get_data():
    now = datetime.datetime.utcnow()
    date_string_now = now.strftime("%Y-%m-%dT%H:%M:%S UTC") # format the time string
    old = now - datetime.timedelta(minutes=90) # subtract 90 minutes  
    date_string_old= old.strftime("%Y-%m-%dT%H:%M:%S UTC") # format the time string
    getquery = {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": [
                        date_string_old,
                        date_string_now
                    ],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "between"
                }
            ]
        },
        "aggregation": {
            "metrics": [
                {
                    "property": "latency",
                    "type": "avg"
                }
            ]
        }
    }
    traceData = {}
    sloData=[]
    data = vManage_auth.get_data("/dataservice/stream/device/nwpi/traceHistory")["data"]
    for items in data:  
        for item in items["data"]["devices"]:
            if(item["state"]=="running"):
                traceData.update({item["trace-name"] : ["NA"]})
    data = vManage_auth.get_data("/dataservice/stream/device/nwpi", query2=getquery)["data"]
    seen = []
    seen2 = []
    for item in data:
        tracename=""
        tracestate=""
        if("devices" in item["data"].keys()):
            tracename = item["data"]["devices"][0]["trace-name"]
        else:
            tracename = item["trace-id"]

        if(tracename not in seen):
            seen.append(tracename)
            query = {
                "traceId" : item["trace-id"], 
                "timestamp": item["entry_time"],
                "state":"running"
            }
            data = vManage_auth.get_data("/dataservice/stream/device/nwpi/concurrentData",query=query)
            flag = False
            summary=[]
            seen3 = []
            for entry in data:
                entry = entry["data"]
                if(entry["big_drop"]==True):
                    flag = True
                    if("big_drop" not in seen3):
                        seen3.append("big_drop")
                        summary.append({"big_drop":entry["big_drop"]})
                elif(entry["big_wan_drop"]==True):
                    flag = True
                    if("big_wan_drop" not in seen3):
                        seen3.append("big_wan_drop")
                        summary.append({"big_wan_drop":entry["big_wan_drop"]})
                elif(entry["qos_congested"]==True):
                    flag = True
                    if("qos_congested" not in seen3):
                        seen3.append("qos_congested")
                        summary.append({"qos_congested":entry["qos_congested"]})
                elif(entry["server_no_response"]==True):
                    flag = True
                    if("server_no_response" not in seen3):
                        seen3.append("server_no_response")
                        summary.append({"server_no_response":entry["server_no_response"]})
                elif(entry["sla_violated"]==True):
                    flag = True
                    if("sla_violated" not in seen3):
                        seen3.append("sla_violated")
                        summary.append({"sla_violated":entry["sla_violated"]})
                elif(entry["sla_violated_bfd"]==True):
                    flag = True
                    if("sla_violated_bfd" not in seen3):
                        seen3.append("sla_violated_bfd")
                        summary.append({"sla_violated_bfd":entry["sla_violated_bfd"]})
                for i in entry["upstream_hop_list"]:
                    if(int(i["jitter"])>20):
                        flag = True
                        if("jitter" not in seen3):
                            seen3.append("jitter")
                            summary.append({"jitter":round(int(i["jitter"]))})
                    elif(int(i["latency"])>20):
                        flag = True
                        if("latency" not in seen3):
                            seen3.append("latency")
                            summary.append({"latency":round(int(i["latency"]))})
                    elif(int(i["local_drop_rate"])>20):
                        flag = True
                        if("local_drop_rate" not in seen3):
                            seen3.append("local_drop_rate")
                            summary.append({"local_drop_rate":round(int(i["local_drop_rate"]))})
                    elif(i["qos_congested"]==True):
                        flag = True
                        if("qos_congested" not in seen3):
                            seen3.append("qos_congested")
                            summary.append({"qos_congested":i["qos_congested"]})
                    elif(int(i["remote_drop_rate"])>20):
                        flag = True
                        if("remote_drop_rate" not in seen3):
                            seen3.append("remote_drop_rate")
                            summary.append({"remote_drop_rate":round(int(i["remote_drop_rate"]))})
                    elif(i["server_no_response"]==True):
                        flag = True
                        if("server_no_response" not in seen3):
                            seen3.append("server_no_response")
                            summary.append({"server_no_response":i["server_no_response"]})
                    elif(i["sla_violated"]==True):
                        flag = True
                        if("sla_violated" not in seen3):
                            seen3.append("sla_violated")
                            summary.append({"sla_violated":i["sla_violated"]})
                    elif(i["sla_violated_bfd"]==True):
                        flag = True
                        if("sla_violated_bfd" not in seen3):
                            seen3.append("sla_violated_bfd")
                            summary.append({"sla_violated_bfd":i["sla_violated_bfd"]})
                for i in entry["downstream_hop_list"]:
                    if(int(i["jitter"])>20):
                        flag = True
                        if("jitter" not in seen3):
                            seen3.append("jitter")
                            summary.append({"jitter":round(int(i["jitter"]))})
                    elif(int(i["latency"])>20):
                        flag = True
                        if("latency" not in seen3):
                            seen3.append("latency")
                            summary.append({"latency":round(int(i["latency"]))})
                    elif(int(i["local_drop_rate"])>20):
                        flag = True
                        if("local_drop_rate" not in seen3):
                            seen3.append("local_drop_rate")
                            summary.append({"local_drop_rate":round(int(i["local_drop_rate"]))})
                    elif(i["qos_congested"]==True):
                        flag = True
                        if("qos_congested" not in seen3):
                            seen3.append("qos_congested")
                            summary.append({"qos_congested":i["qos_congested"]})
                    elif(int(i["remote_drop_rate"])>20):
                        flag = True
                        if("remote_drop_rate" not in seen3):
                            seen3.append("remote_drop_rate")
                            summary.append({"remote_drop_rate":round(int(i["remote_drop_rate"]))})
                    elif(i["server_no_response"]==True):
                        flag = True
                        if("server_no_response" not in seen3):
                            seen3.append("server_no_response")
                            summary.append({"server_no_response":i["server_no_response"]})
                    elif(i["sla_violated"]==True):
                        flag = True
                        if("sla_violated" not in seen3):
                            seen3.append("sla_violated")
                            summary.append({"sla_violated":i["sla_violated"]})
                    elif(i["sla_violated_bfd"]==True):
                        flag = True
                        if("sla_violated_bfd" not in seen3):
                            seen3.append("sla_violated_bfd")
                            summary.append({"sla_violated_bfd":i["sla_violated_bfd"]})
                if(flag and (tracename not in seen2)):
                    sloData.append({"health":"critical", "name": "traceid: "+ str(tracename),"events":str(summary), "url":"https://"+ vManage_auth.vmanage_ip + "/#/app/monitor/nwpi"})
                    flag = False
                    seen2.append(tracename)
            data = vManage_auth.get_data("/dataservice/stream/device/nwpi/eventReadout", query=query)
            eventlist = []
            for i in data:
                for event in i["eventList"]:
                    eventlist.append(event)
            traceData[tracename] = eventlist
    traceDetails = []
    for key,value in traceData.items():
        if(value!=['NA'] and value!=[]):
            traceDetails.append({"name":"traceid: "+str(key),"events":value, "url": "https://"+ vManage_auth.vmanage_ip + "/#/app/monitor/nwpi", "health":"critical"})
    return [sloData,traceDetails]


if __name__ == "__main__":   
    data = get_data() 
    pprint(data)
