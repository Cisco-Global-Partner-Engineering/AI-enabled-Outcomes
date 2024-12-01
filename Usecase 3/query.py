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
import sample_bm25
from pprint import pprint
import credentials
from openai import AzureOpenAI


client = AzureOpenAI(
    azure_endpoint = "https://openaigpts.openai.azure.com/", 
    api_key=credentials.azure_openai_token,  
    api_version="2024-02-15-preview"
    )

file = "catalystcenter.json"
#file = "vmanageapi_2014.json"
#file = "meraki_dashboard_api_1_52_0.json"

with open(file, "r") as f:
    apidoc = json.load(f)

paths = []
for item in apidoc["paths"]:
    paths.append(item)

pathtext = {}
for item in paths:
    # get key from item
    #print(apidoc["paths"][item])
    for key in apidoc["paths"][item].keys():
        pathtext[item] = ""
        if ("summary" in apidoc["paths"][item][key]):
            pathtext[item] = apidoc["paths"][item][key]["summary"]
        if ("description" in apidoc["paths"][item][key]):
            pathtext[item] = pathtext[item] + "." + apidoc["paths"][item][key]["description"]

corpus = []
for value in pathtext.values():
    corpus.append(value)
corpus = set(corpus)
corpus = list(corpus)
print(len(corpus))

#pprint(corpus)

query = input("Enter your query: ")
results = sample_bm25.get_bm25_scores(corpus, query)

resultpaths = []
for key1,value in results.items():
    if value > 0:
        #print(key1, value)
        # find the key in pathtext that matches the value in results
        for key2 in pathtext.keys():
            #print("pathtext",pathtext[key2])
            #print("key1",key1)
            if pathtext[key2] == key1:
                resultpaths.append(key2)
                #break

#print(resultpaths)
resultpaths = resultpaths[:5]
print(resultpaths)
#exit()
replylist = []
for item in resultpaths:
    #print(item)
    #pprint(apidoc["paths"][item])
    messages=[
        {"role": "system", "content": f"Answer the query with the given REST API context. Make sure to include all information needed to write a code based on this. Try to answer, even if a partial answer is available. if context is totally not relevant, then reply with only 'NO'. Make sure to answer only using the provided REST API context. REST API context : {item} ; {apidoc["paths"][item]}"},
        {"role": "user", "content":"query:" + query}
    ]
    chat_completion = client.chat.completions.create(
        model="azuregpt-4o", messages = messages, temperature = 0.1, max_tokens = 500
    )
    reply = chat_completion.choices[0].message.content
    if reply.startswith("NO"):
        continue
    else:
        replylist.append(reply)
    

messages=[
        {"role": "system", "content": f"Answer the query with the given list of partial answers. Make sure to include all information needed to write a code based on this. Make sure to answer only using the provided partial answer list. Partial answers: {replylist}"},
        {"role": "user", "content":"query:" + query}
    ]
chat_completion = client.chat.completions.create(
        model="azuregpt-4o", messages = messages, temperature = 0.1, max_tokens = 1000
    )
reply = chat_completion.choices[0].message.content
print(reply)

