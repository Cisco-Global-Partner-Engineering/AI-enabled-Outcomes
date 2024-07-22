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

from flask import Flask
from flask_cors import CORS  # import the CORS module
import mongodb_auth
import json

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

@app.route('/data', methods=['GET'])
def get_data():
    """Return data about the devices. A sample return data for this function is provided in demodbdata.py
    parameters: None
    returns: JSON
    """
    db = mongodb_auth.authenticatedb()
    collection = db['Alerts']
    response = mongodb_auth.get_data(collection)
    collection = db['Infra_Health']
    response2 = mongodb_auth.get_data(collection)
    collection = db['App_Health']
    response3 = mongodb_auth.get_data(collection)
    collection = db['Top_Threats']
    response4 = mongodb_auth.get_data(collection)
    data = {"data": {"alerts": response, "infra_health": response2, "app_health": response3, "top_threats": response4}}

    
    return json.dumps(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
