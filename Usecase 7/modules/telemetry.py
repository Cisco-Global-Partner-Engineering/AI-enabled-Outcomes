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


import modules.ping_server as ping_server
import modules.ping_remoteworker as ping_remoteworker
import logging
import concurrent.futures
import os

# Get the base directory path (parent of the modules directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ping_all():
    """
    This function pings all devices in the network in parallel and returns the results.
    It uses the ping_client1, ping_client2, ping_server, and ping_remoteworker modules 
    to perform the pings concurrently using ThreadPoolExecutor.
    
    Returns:
        list: A list of ping results from all devices
    """
    logger = logging.getLogger(__name__)

    logger.info("Starting telemetry.py")
    
    # Reset the ping result file using absolute path
    ping_result_path = os.path.join(BASE_DIR, 'data', 'input', 'ping_result.json')
    with open(ping_result_path, 'w') as f:
        f.write("")

    # List of ping functions to execute
    ping_functions = [
        ping_server.ping_from_remote_linux,
        ping_remoteworker.ping_from_remote_linux
    ]

    results = []
    
    # Execute ping functions in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all ping functions to the executor
        future_to_ping = {executor.submit(func): func for func in ping_functions}
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_ping):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                func_name = future_to_ping[future].__module__
                logger.error(f"Ping function {func_name} generated an exception: {exc}")
                results.append(None)  # Add None for failed pings

    logger.info("Completed telemetry.py")

    return results

if __name__ == "__main__":
    # Configure logging if needed
    logging.basicConfig(level=logging.INFO)
    
    # Execute the parallel ping function
    results = ping_all()
    print(f"Ping results: {results}")