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

import dbimport
import doquery
import vectorquery

def semanticcheck(query,cachedquery):
    prompt = "Reply with only YES or NO. Given 2 queries asked by a customer, your task is to find out if they mean exactly the same. Following are the queries, seperated by semicolon :" + query + " ; " + cachedquery
    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
    try:
      response = doquery.dochat(prompt)
      if response.strip().upper() == 'YES':
          #print("Its True")
          return True
      else:
          #print("The query was semantically False")
          return False
    except Exception as e:
      print(f"Exception: {e}")
      return False

def getdbdata(db):
    all_data = []
    collection = db["ciscoupdate"+'-semantic']
    all_data = all_data + list(collection.find({}, {'_id': False}))
    return all_data

def dbcheck(query, db):
    #print("in dbcheck")
    collection = db["ciscoupdate"+'-semantic']
    all_data = getdbdata(db)
    #print("all_data :",all_data)
    if(all_data != []):
        #print("semantic:",all_data)
        #print("alldata: ",all_data)
        for d in all_data:
            if(query == d["query"]):
                if(d["result"]):
                    #print("exact match:",d["result"])
                    return d["result"]
        for d in all_data:
            if(semanticcheck(query,d["query"])):
                qoutput = [{"query":query,"result":d["result"]}]
                #print("similar:",qoutput)
                dbimport.addData(qoutput,collection)
                return d["result"]     
    return False

def queryme(query,type="blogs",history=[]):
    if(query == ""):
        return "Please enter a valid query"
    # else if query is only single word, then ask to enter longer query
    elif(len(query.split()) < 2):
        return "Please enter a longer query"
    else:
        query = query.strip()
    db = dbimport.authenticatedb()
    result = dbcheck(query,db)
    if(result is False):
        if(type == "docs"):
            result = vectorquery.dosearch(query)
        else:
            result = doquery.queryme(query)
        qoutput = [{"result":result,"query":query}]
        errorlist = ["Error in LLM inferencing..","Too many relevant indexes found. Please provide a more specific query / 'searchterms:'", "No relevant information found in the documents.","No relevant information found in the documents. Please rephrase the query and try again.","Please ask the query again with a valid platform name from the list : [IOS XE, Catalyst SD-WAN, Catalyst Center, Secure Firewall]","I am unable to provide an answer to your query, as I could not find any relevant data in the blogs or official documentation.","no result from blogs, now searching docs..","I am unable to provide an answer to your query, as I could not find any relevant data in the blogs or official documentation."]
        error_substrings = ["does not contain", "Answer is not available"]
        if(result != "" and result not in errorlist and not any(substring in result for substring in error_substrings)):
            collection = db["ciscoupdate"+'-semantic']
            dbimport.addData(qoutput,collection)
        print("gpt4-o:")
        return result
    else :
        result = "fromcache:" + result
        return result


def purgedb():
    db = dbimport.authenticatedb()
    collection = db["ciscoupdate"+'-semantic']
    print(dbimport.purge_collection(collection))


if(__name__ == '__main__'):

    #purgedb()

    while(True):
        #purgedb()
        query = input("enter query : ")
        if(query):
            result = queryme(query)
            print(result)