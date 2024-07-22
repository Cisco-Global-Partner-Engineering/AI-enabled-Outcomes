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

from flask import Flask, jsonify, request
import alerts
import infra_health
import app_health
import top_threats

app = Flask(__name__)

@app.route('/data', methods=['GET'])
def get_data():
    """Return data about the devices. A sample return data for this function is provided in demodbdata.py
    parameters: None
    returns: JSON
    """
    data = { 
        "Alerts": alerts.create_alerts_data_model(),
        "Infra_Health": infra_health.create_infra_health_data_model(),
        "App_Health": app_health.create_app_health_data_model(),
        "Top_Threats": top_threats.create_top_threats_data_model()
        }
    
    return jsonify({'data': data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
