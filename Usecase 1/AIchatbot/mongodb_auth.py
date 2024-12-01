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

# Import the necessary libraries
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import credentials
import certifi


uri = credentials.mongodb_uri

# Function to purge the collection
def purge_collection(collection):
    result = collection.delete_many({})
    return('Deleted {} documents from collection.'.format(result.deleted_count))

def addData(data,collection):
    # Insert all documents
    result = collection.insert_many(data)
    return(len(result.inserted_ids))

def authenticatedb(dbname='maindb'):
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'),tlsCAFile=certifi.where())
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        import sys
        #print (sys._getframe(1).f_code.co_name)
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    # Get the database
    return client[dbname]

if __name__ == '__main__':
    authenticatedb()
