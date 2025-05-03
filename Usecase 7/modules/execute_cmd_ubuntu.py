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


import paramiko
import logging
import json
import time
import modules.credentials as credentials
import os
from pathlib import Path

# Get the same logger
logger = logging.getLogger(__name__)

import select
import socket
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

def get_host_key(hostname, port=22):
    """
    Retrieves the SSH host key for a given server.
    
    Args:
        hostname (str): The hostname or IP address
        port (int, optional): The SSH port number. Defaults to 22.
        
    Returns:
        paramiko.PKey or None: The host key if found, None otherwise
    """
    try:
        transport = paramiko.Transport(f"{hostname}:{port}")
        transport.start_client()
        key = transport.get_remote_server_key()
        transport.close()
        return key
    except Exception as e:
        print(f"Error retrieving host key: {e}")
        return None

def execute_commands_ssh(hostname, username, password=None, key_filename=None, port=22, commands=[], command_timeout=10, connection_timeout=10, auto_add_key=True):
    """
    Executes a list of commands over SSH with a timeout for each command.
    Commands are executed in parallel using multiple threads.

    Args:
        hostname (str): The hostname or IP address of the remote server.
        username (str): The username for SSH authentication.
        password (str, optional): The password for SSH authentication. Defaults to None.
        key_filename (str, optional): Path to the private key file for SSH authentication. Defaults to None.
        port (int, optional): The SSH port number. Defaults to 22.
        commands (list, optional): A list of commands to execute. Defaults to [].
        command_timeout (int, optional): Timeout in seconds for each command execution loop. Defaults to 10.
        connection_timeout (int, optional): Timeout in seconds for establishing the SSH connection. Defaults to 10.
        auto_add_key (bool, optional): Whether to automatically add unknown host keys. Defaults to True.

    Returns:
        dict or str: A dictionary containing the results of each command execution or a JSON string with an error 
                    if connection fails. Each command's result includes output, errors, exit status, and timeout information.
    """
    ssh = paramiko.SSHClient()
    
    # Setup host key policy
    if auto_add_key:
        # First check if the host key is already in known_hosts
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        host_keys = paramiko.HostKeys()
        
        # Create .ssh directory if it doesn't exist
        ssh_dir = Path(os.path.expanduser('~/.ssh'))
        if not ssh_dir.exists():
            ssh_dir.mkdir(mode=0o700)
            
        # Load existing known hosts if the file exists
        if os.path.isfile(known_hosts_path):
            host_keys.load(known_hosts_path)
            
        # Check if host is already in known_hosts
        if host_keys.lookup(hostname) is None:
            print(f"Host {hostname} not found in known_hosts, retrieving key...")
            # Get the host key
            host_key = get_host_key(hostname, port)
            if host_key:
                # Add the key to known_hosts file
                line = f"{hostname} {host_key.get_name()} {host_key.get_base64()}"
                with open(known_hosts_path, 'a+') as known_hosts_file:
                    known_hosts_file.write(f"{line}\n")
                print(f"Added {hostname} to known_hosts file.")
                
                # Update host keys object with new entry
                host_keys.add(hostname, host_key.get_name(), host_key)
                ssh.set_missing_host_key_policy(paramiko.RejectPolicy())  # Safer policy after adding the key
                ssh._host_keys = host_keys  # Set the loaded host keys directly
            else:
                # Fall back to AutoAddPolicy if we can't get the key
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print(f"Could not retrieve host key for {hostname}, using AutoAddPolicy.")
        else:
            # Host is already known, use the strict policy
            ssh.load_host_keys(known_hosts_path)
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
            print(f"Host {hostname} found in known_hosts, using existing key.")
    else:
        # Use AutoAddPolicy if auto_add_key is False (legacy behavior)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    results = {}
    connect_kwargs = {
        "hostname": hostname,
        "port": port,
        "username": username,
        "timeout": connection_timeout,  # Timeout for the connection itself
        "allow_agent": False,  # Disable agent usage unless explicitly needed
        "look_for_keys": False  # Disable searching for keys in default locations unless key_filename is None
    }

    if key_filename:
        connect_kwargs["key_filename"] = key_filename
    elif password:
        connect_kwargs["password"] = password
    else:
        # If neither key nor password is provided, try looking for keys in default locations
        connect_kwargs["look_for_keys"] = True

    try:
        print(f"Connecting to {hostname}:{port} as {username}...")
        ssh.connect(**connect_kwargs)
        print("Connection successful.")

        # Define an inner function to execute a single command (to be used in parallel)
        def execute_single_command(command):
            print(f"Executing command: {command}")
            timeout_occurred = False
            stdout_output = []
            stderr_output = []
            exit_status = None
            channel = None  # Initialize channel

            try:
                # Use exec_command for better status handling
                transport = ssh.get_transport()
                if not transport or not transport.is_active():
                    raise paramiko.SSHException("SSH transport is not active")
                channel = transport.open_session()
                channel.settimeout(command_timeout)  # Set overall timeout for channel operations
                channel.exec_command(command)

                start_time = time.time()  # Start time for this command

                while True:
                    # Check if command has finished
                    if channel.exit_status_ready():
                        exit_status = channel.recv_exit_status()
                        # Read any remaining data after exit
                        while channel.recv_ready():
                            stdout_output.append(channel.recv(4096).decode('utf-8', errors='replace'))
                        while channel.recv_stderr_ready():
                            stderr_output.append(channel.recv_stderr(4096).decode('utf-8', errors='replace'))
                        break  # Exit inner loop once command finished

                    # Check for timeout
                    if time.time() - start_time > command_timeout:
                        print(f"Command '{command}' timed out after {command_timeout} seconds.")
                        timeout_occurred = True
                        # Try to get exit status even on timeout, might be available
                        if channel.exit_status_ready():
                            exit_status = channel.recv_exit_status()
                        break  # Exit inner loop on timeout

                    # Wait for data or timeout using select
                    read_ready, _, err_ready = select.select([channel], [], [channel], 0.5)

                    if not read_ready and not err_ready:
                        # select timed out, loop again to check exit_status or overall timeout
                        continue

                    # Read available data
                    if channel.recv_ready():
                        stdout_output.append(channel.recv(4096).decode('utf-8', errors='replace'))
                    if channel.recv_stderr_ready():
                        stderr_output.append(channel.recv_stderr(4096).decode('utf-8', errors='replace'))

                # Join output/error streams
                stdout = "".join(stdout_output).strip()
                stderr = "".join(stderr_output).strip()

                return command, {
                    "output": stdout,
                    "error": stderr,
                    "exit_status": exit_status,
                    "timeout": timeout_occurred,
                }

            except socket.timeout as e:
                # Correct exception type for timeout
                print(f"Timeout exception during command '{command}': {e}")
                timeout_occurred = True
                return command, {"output": "".join(stdout_output).strip(), "error": str(e), "exit_status": None, "timeout": True}
            except Exception as e:
                print(f"Error executing command '{command}': {e}")
                return command, {"output": "".join(stdout_output).strip(), "error": str(e), "exit_status": None, "timeout": False}
            finally:
                # Ensure channel is closed if it was opened
                if channel:
                    try:
                        channel.close()
                        print(f"Channel closed for command: {command}")
                    except Exception as close_e:
                        print(f"Error closing channel for command '{command}': {close_e}")

        # Execute commands in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(len(commands), 10)) as executor:  # Limit the number of parallel executions
            # Submit all commands to the executor
            future_to_command = {executor.submit(execute_single_command, cmd): cmd for cmd in commands}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_command):
                try:
                    command, result = future.result()
                    results[command] = result
                except Exception as exc:
                    command = future_to_command[future]
                    print(f"Command '{command}' generated an exception: {exc}")
                    results[command] = {"output": "", "error": str(exc), "exit_status": None, "timeout": False}

    except paramiko.AuthenticationException as e:
        print(f"Authentication failed: {e}")
        return json.dumps({"error": f"Authentication failed: {e}"}, indent=4)
    except paramiko.SSHException as e:
        # Includes various SSH errors like connection refused, no route, protocol errors
        print(f"SSH connection error: {e}")
        return json.dumps({"error": f"SSH connection error: {e}"}, indent=4)
    except socket.timeout as e:
        # Correct exception for socket timeout during connection phase
        print(f"Connection timed out: {e}")
        return json.dumps({"error": f"Connection timed out to {hostname}:{port} after {connection_timeout} seconds"}, indent=4)
    except Exception as e:
        # Catch other potential errors during setup or connection
        print(f"An unexpected error occurred: {e}")
        return json.dumps({"error": f"An unexpected error occurred: {e}"}, indent=4)
    finally:
        # Ensure the main SSH client connection is always closed
        if ssh:
            ssh.close()
            print("SSH client connection closed.")

    # Return results directly as a dictionary
    return results

# Example usage:
if __name__ == "__main__":
    # --- Configuration ---
    target_host = "198.18.1.113"  # <-- Replace with actual target
    ssh_user = "cisco"          # <-- Replace with actual username
    # Provide EITHER password OR key_filename
    ssh_password = "cisco"          # <-- Replace with actual password (or set to None)
    ssh_key_file = None                         # <-- Or replace with path to your private key file (e.g., "/path/to/id_rsa")

    # List of commands to execute in parallel
    commands_to_execute = [
        "ls -l /tmp",
        "whoami",
        "cat /etc/os-release",
        "sleep 10", # Example command that might time out
        "echo 'Error output' >&2", # Example command producing stderr
        "command_that_does_not_exist" # Example command with non-zero exit status
        ]

    # Timeouts
    connect_timeout_seconds = 15 # Timeout for establishing the connection
    cmd_timeout_seconds = 7      # Timeout for each individual command

    # --- Execution ---
    print("Starting parallel SSH command execution...")
    results = execute_commands_ssh(
        hostname=target_host,
        username=ssh_user,
        password=ssh_password,          # Pass password if using password auth
        key_filename=ssh_key_file,      # Pass key filename if using key auth
        # port=2222,                    # Optional: Specify non-standard port if needed
        commands=commands_to_execute,
        command_timeout=cmd_timeout_seconds,
        connection_timeout=connect_timeout_seconds
    )

    # --- Output ---
    print("\n--- Execution Results ---")
    if isinstance(results, dict) and "error" not in results:
        for cmd, result in results.items():
            print(f"\nCommand: {cmd}")
            print(f"  Timeout: {result.get('timeout')}")
            print(f"  Exit Status: {result.get('exit_status')}")
            print(f"  Output: {result.get('output', '')[:100]}...") # Print first 100 chars
            print(f"  Error: {result.get('error', '')[:100]}...")   # Print first 100 chars
    else:
        # Results is either a string or contains an error key
        print(json.dumps(results, indent=4) if isinstance(results, dict) else results)
    print("---------------------------------")