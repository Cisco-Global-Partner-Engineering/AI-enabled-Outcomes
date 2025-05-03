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


#!/usr/bin/env python3
"""
Network Device Command Execution Tool

This script provides functionality to connect to various network devices 
(Cisco routers, ASA firewalls, and switches) and execute commands or configurations.
It supports parallel execution, robust error handling, and proper session management.

Dependencies:
    - netmiko: For SSH connections to network devices
    - concurrent.futures: For parallel command execution
"""

from netmiko import ConnectHandler
import json
import time
import logging
import concurrent.futures
from functools import partial
import modules.credentials as credentials  # Module containing device credential information

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("network_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_device_connection_params(device_name):
    """
    Retrieve connection parameters for a specific device by name.
    
    Args:
        device_name (str): The name of the device as defined in credentials.
        
    Returns:
        dict: Connection parameters for the device.
        
    Raises:
        ValueError: If the device name isn't found in credentials.
    """
    for device in credentials.devices:
        if device["name"] == device_name:
            conn_params = {
                'host': device['ip'],
                'username': device['username'],
                'password': device['password'],
                'port': device['port']
            }
            
            # Add enable password if device is not a Linux host
            if 'linux' not in device['type'].lower():
                conn_params['secret'] = device.get('enable_password', device['password'])
                
                # Set device_type based on the device type
                if 'asa' in device['type'].lower():
                    conn_params['device_type'] = 'cisco_asa'
                elif 'ios' in device['type'].lower():
                    conn_params['device_type'] = 'cisco_ios'
            else:
                conn_params['device_type'] = 'linux'
                
            return conn_params
            
    raise ValueError(f"Device '{device_name}' not found in credentials")


def send_config_commands(device_name, config_commands, timeout=60):
    """
    Connect to a device and send configuration commands.

    Args:
        device_name (str): Name of the device as defined in credentials.
        config_commands (list): List of configuration commands to execute.
        timeout (int, optional): Command timeout in seconds. Defaults to 120.

    Returns:
        str: Output from the configuration commands or error message.
    """
    connection = None
    try:
        # Get device parameters from credentials
        device_params = get_device_connection_params(device_name)
        
        logger.info(f"Connecting to {device_name} ({device_params['host']}) for configuration...")
        connection = ConnectHandler(**device_params)
        
        # Enter enable mode if needed
        if device_params['device_type'] in ['cisco_ios', 'cisco_asa']:
            connection.enable()
            
            # Disable paging based on device type
            if device_params['device_type'] == 'cisco_asa':
                connection.send_command('terminal pager 0')
            else:
                connection.send_command('terminal length 0')
        
        logger.info(f"Sending {len(config_commands)} configuration commands to {device_name}...")
        output = connection.send_config_set(config_commands, read_timeout=timeout)
        logger.info(f"Configuration successfully applied to {device_name}")
        
        return output
        
    except Exception as e:
        error_msg = f"Error configuring {device_name}: {str(e)}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
        
    finally:
        if connection and connection.is_alive():
            logger.debug(f"Disconnecting from {device_name}...")
            connection.disconnect()


def execute_commands(device_name, commands, timeout=60):
    """
    Connect to a device and execute a list of show or operational commands.
    
    The function handles special commands like 'sleep' and tries to maintain
    a clean state for each command execution.

    Args:
        device_name (str): Name of the device as defined in credentials.
        commands (list): List of commands to execute.
        timeout (int, optional): Command timeout in seconds. Defaults to 60.
    
    Returns:
        dict: Dictionary with command results. Failed commands will have error messages as values.
    """
    results = {}
    connection = None
    
    try:
        # Get device parameters
        device_params = get_device_connection_params(device_name)
        device_type = device_params['device_type']
        
        for command in commands:
            try:
                # Handle sleep command without requiring a connection
                if command.startswith("sleep"):
                    duration = int(command.split(" ")[1])
                    logger.info(f"Sleeping for {duration} seconds")
                    time.sleep(duration)
                    results[command] = f"Slept for {duration} seconds"
                    continue
                
                # Establish or re-establish connection for each command
                if connection is None or not connection.is_alive():
                    logger.info(f"Connecting to {device_name} ({device_params['host']})...")
                    connection = ConnectHandler(**device_params)
                
                # Check current mode and elevate to privileged EXEC mode for network devices
                if device_type in ['cisco_ios', 'cisco_asa']:
                    if not connection.check_enable_mode():
                        connection.enable()
                    
                    # Disable terminal paging based on device type
                    if device_type == 'cisco_asa':
                        connection.send_command('terminal pager 0')
                    else:
                        connection.send_command('terminal length 0')

                logger.info(f"Executing command on {device_name}: {command}")
                expect_string = r"#" if device_type in ['cisco_ios', 'cisco_asa'] else r"$"
                output = connection.send_command(command, read_timeout=timeout, expect_string=expect_string)
                results[command] = output
                
            except Exception as error:
                # Log the error but continue with next command
                error_msg = f"Error executing '{command}' on {device_name}: {str(error)}"
                logger.error(error_msg)
                results[command] = f"ERROR: {error_msg}"
                
                # Close the faulty connection to ensure a clean reconnect
                if connection and hasattr(connection, 'disconnect'):
                    try:
                        connection.disconnect()
                    except Exception as disconnect_error:
                        logger.error(f"Error disconnecting: {str(disconnect_error)}")
                    connection = None
    
    except Exception as e:
        logger.error(f"Error setting up device parameters for {device_name}: {str(e)}")
        results["setup_error"] = f"ERROR: {str(e)}"
        
    finally:
        # Final cleanup
        if connection and hasattr(connection, 'disconnect'):
            try:
                connection.disconnect()
                logger.debug(f"Disconnected from {device_name}")
            except Exception as disconnect_error:
                logger.error(f"Error during final disconnect from {device_name}: {str(disconnect_error)}")
    
    return results


def execute_commands_in_parallel(device_names, commands, max_workers=5):
    """
    Execute the same commands on multiple devices in parallel.
    
    Args:
        device_names (list): List of device names to connect to.
        commands (list): List of commands to execute on each device.
        max_workers (int, optional): Maximum number of parallel workers. Defaults to 5.
        
    Returns:
        dict: Dictionary with device names as keys and command results as values.
    """
    results = {}
    max_workers = len(commands) # Ensure we don't exceed the number of commands
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Create a dictionary of futures
        future_to_device = {
            executor.submit(execute_commands, device, commands): device
            for device in device_names
        }
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_device):
            device = future_to_device[future]
            try:
                results[device] = future.result()
                logger.info(f"Completed execution on {device}")
            except Exception as e:
                logger.error(f"Exception occurred while processing {device}: {str(e)}")
                results[device] = f"ERROR: {str(e)}"
    
    return results


if __name__ == "__main__":
    # Example usage
    device_list = ['branch-fw', 'dmz-fw']
    show_commands = [
        "show interface ip brief",
        "show route"
    ]
    
    parallel_results = execute_commands_in_parallel(device_list, show_commands)
    
    # Print results to console for verification
    print("\nResults by device:")
    for device, commands_output in parallel_results.items():
        print(f"\n=== Device: {device} ===")
        for command, output in commands_output.items():
            print(f"\nCommand: {command}")
            print("-" * 50)
            print(output)
            print("-" * 50)
    
    # Ensure the JSON is properly structured with device names as the top level keys
    with open("parallel_execution_results.json", "w") as file:
        json.dump(parallel_results, file, indent=4)
