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

from flask import Flask, jsonify
import vManageAlarms
import vManageHealth
import CatalystCenterHealth
import CatalystCenterAppHealth
import vManageNWPI_readTrace
import CatalystCenterAlarms

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_data():
    """Return data about the devices. A sample return data for this function is provided in demodbdata.py
    parameters: None
    returns: JSON
    """
    data = { 
        "vManageHealth": vManageHealth.get_data(),
        "DnacHealth" : CatalystCenterHealth.get_data(),
        "vManageNWPI_readTrace" : vManageNWPI_readTrace.get_data(),
        "DnacAppHealth": CatalystCenterAppHealth.get_data(),
        "vManageAlarms": vManageAlarms.get_data(),
        "DnacAlarms": CatalystCenterAlarms.get_data()
        }
    
    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5556, debug=True)
