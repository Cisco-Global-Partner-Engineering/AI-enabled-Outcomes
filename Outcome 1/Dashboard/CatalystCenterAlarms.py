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

import CatalystCenter_auth
from pprint import pprint


def get_data():
    """ Get all alarms from catalyst center

    params:   None
    
    Returns:   List of dictionaries containing the following keys:
                severity (str): severity of the alarm
                summary (str): summary of the alarm
                name (str): name of the device
                url (str): url to the alarm in DNAC

    example:
                [{'name': 'CPS-BDR',
                 'severity': 'major',
                 'summary': 'device_time_drift',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'Appx_CSR1Kv',
                 'severity': 'moderate',
                 'summary': 'router_interface_excess_rx_tx_util',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'Appx_CSR1Kv',
                 'severity': 'moderate',
                 'summary': 'router_interface_input_output_discards',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'Appx_CSR1Kv',
                 'severity': 'major',
                 'summary': 'device_time_drift',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'DC-Switch.demo.local',
                 'severity': 'major',
                 'summary': 'device_time_drift',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'CPS-Edge2',
                 'severity': 'major',
                 'summary': 'device_time_drift',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'CPS-Edge1',
                 'severity': 'major',
                 'summary': 'device_time_drift',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'},
                {'name': 'CPS-L2Border',
                 'severity': 'major',
                 'summary': 'device_time_drift',
                 'url': 'https://10.1.100.4/dna/assurance/dashboards/issues-events/issues/open'}]

    """
    result = []
    data = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/issues")["response"]
    for item in data:
        if(item["status"]!="active"):
            continue
        query = {
        "entity_type": "issue_id",
        "entity_value": item["issueId"]
        }
        tmp = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/issue-enrichment-details", header=query)
        for i in tmp['issueDetails']['issue']:
            query = {
                "searchBy": i["deviceId"],
                "identifier": "uuid"
            }
            detailData = CatalystCenter_auth.get_data(uri="/dna/intent/api/v1/device-detail", query=query)['response']
            i["issueSeverity"] = i["issueSeverity"].lower()
            if(i["issueSeverity"]=='high'):
                i["issueSeverity"] = "major"
            elif(i["issueSeverity"]=='medium'):
                i["issueSeverity"] = "moderate"
            elif(i["issueSeverity"]=='minor'):
                i["issueSeverity"] = "warning"
            result.append({"severity":i["issueSeverity"], "summary": i["issueName"], "name": detailData["nwDeviceName"], "url": CatalystCenter_auth.BASE_URL + "/dna/assurance/dashboards/issues-events/issues/open" })
    return result

if __name__ == "__main__":
    pprint(get_data())
