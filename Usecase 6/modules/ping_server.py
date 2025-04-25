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


import modules.execute_cmd_ubuntu as execute_cmd_ubuntu
import json
import time
import logging
import os
import paramiko  # Add missing import

# Get the base directory path (parent of the modules directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get the same logger
logger = logging.getLogger(__name__)

# Define remote linux machine connection details
linux_device = {
    'host': '198.18.1.113',  # Replace with your remote linux machine's IP address
    'username': 'cisco',     # Replace with your remote linux machine's username
    'password': 'cisco',   # Replace with your remote linux machine's password
}
# Target IPs addresses to ping
target_ips = ['10.1.0.2','10.0.2.10','10.0.3.10']

def ping_from_remote_linux(device=linux_device, target_ips=target_ips):
    
    """
    Perform a ping from a remote linux machine.

    :param device: Dictionary containing device connection details.
    :param target_ip: IP address to ping.
    :return: Ping result as a string.
    """
    try:
        outputs = []
        # Establish SSH connection to the remote linux machine
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device['host'], username=device['username'], password=device['password'])

        print(f"Connected to {device['host']} as {device['username']}")
        
        for target_ip in target_ips:
            # Execute the ping command
            stdin, stdout, stderr = ssh.exec_command(f"ping -c 4 {target_ip}")
            outputs.append(stdout.read().decode())
        
        # Close the connection
        ssh.close()

        # Save the ping result to a JSON file using absolute path
        alarm = {"alarm": "ping from server", "results": outputs}
        ping_result_path = os.path.join(BASE_DIR, 'data', 'input', 'ping_result.json')
        with open(ping_result_path, 'a') as file:
            json.dump(alarm, file)
        
        return alarm
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    
    # Perform ping from remote linux machine and print the result
    result_linux = ping_from_remote_linux(linux_device, target_ips)
    print("Ping result from remote linux machine:")
    print(result_linux)