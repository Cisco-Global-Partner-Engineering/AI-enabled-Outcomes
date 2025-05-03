#!/usr/bin/env python3
"""
labcheck.py - Connectivity Test Script for Agentic AI Operations Lab

This script tests SSH connectivity to all network devices in the lab environment.
It uses the device credentials defined in modules/credentials.py and the
connection methods from send_router.py and execute_cmd_ubuntu.py.

The script attempts to connect to each device and run a simple command to verify
connectivity, printing the results in a user-friendly format.
"""

import os
import sys
import time
import json
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("labcheck.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PARENT_DIR)

# Import project modules - adjust imports for new location
import modules.send_router as send_router
import modules.execute_cmd_ubuntu as execute_cmd_ubuntu
import modules.credentials as credentials

def check_router_connectivity(device_name):
    """Test connectivity to a Cisco router, switch, or firewall device"""
    try:
        # Use a simple, non-disruptive command to test connectivity
        test_command = "show version | include uptime"
        if "fw" in device_name:  # Special handling for ASA firewalls
            test_command = "show version | include up"
            
        result = send_router.execute_commands(device_name, [test_command], timeout=30)
        
        if result and isinstance(result, dict) and test_command in result:
            cmd_output = result[test_command]
            if "ERROR:" in cmd_output:
                return False, cmd_output
            return True, "Connection successful"
        else:
            return False, "Failed to retrieve command output"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_linux_connectivity(device_info):
    """Test connectivity to a Linux device"""
    try:
        # Use a simple command to test connectivity
        test_command = "uname -a"
        result = execute_cmd_ubuntu.execute_commands_ssh(
            hostname=device_info["ip"],
            username=device_info["username"],
            password=device_info["password"],
            port=device_info["port"],
            commands=[test_command],
            command_timeout=30,
            connection_timeout=30
        )
        
        if result and isinstance(result, dict) and test_command in result:
            cmd_result = result[test_command]
            if cmd_result.get("exit_status") == 0:
                return True, "Connection successful"
            else:
                return False, f"Command failed: {cmd_result.get('error', 'Unknown error')}"
        elif isinstance(result, str) and "error" in result.lower():
            return False, result
        else:
            return False, "Failed to retrieve command output"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_device(device):
    """Check connectivity to a specific device based on its type"""
    device_name = device["name"]
    device_type = device["type"]
    
    logger.info(f"Testing connectivity to {device_name} ({device_type})...")
    
    start_time = time.time()
    
    if "linux" in device_type.lower():
        success, message = check_linux_connectivity(device)
    else:
        success, message = check_router_connectivity(device_name)
    
    elapsed_time = time.time() - start_time
    
    return {
        "name": device_name,
        "type": device_type,
        "ip": device["ip"],
        "success": success,
        "message": message,
        "elapsed_time": elapsed_time
    }

def print_results(results):
    """Print connectivity test results in a formatted table"""
    print("\n" + "="*80)
    print(f"{'DEVICE NAME':<20} {'DEVICE TYPE':<30} {'IP ADDRESS':<15} {'STATUS':<15}")
    print("="*80)
    
    success_count = 0
    failure_count = 0
    
    # Sort results by device name for consistent output
    sorted_results = sorted(results, key=lambda x: x["name"])
    
    for result in sorted_results:
        status = "✅ CONNECTED" if result["success"] else "❌ FAILED"
        print(f"{result['name']:<20} {result['type']:<30} {result['ip']:<15} {status:<15}")
        
        if result["success"]:
            success_count += 1
        else:
            failure_count += 1
            # Print failure details
            print(f"  Error: {result['message']}")
    
    print("-"*80)
    print(f"Summary: {success_count} devices connected, {failure_count} failed")
    print("="*80)
    
    return success_count, failure_count

def main():
    """Main function to test connectivity to all lab devices"""
    print("\nAgentic AI for Network Operations - Lab Connectivity Check")
    print("----------------------------------------------------------")
    print(f"Testing connectivity to {len(credentials.devices)} devices...\n")
    
    # Test connectivity to all devices in parallel
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_device = {executor.submit(check_device, device): device for device in credentials.devices}
        
        for future in concurrent.futures.as_completed(future_to_device):
            try:
                result = future.result()
                results.append(result)
                
                # Print immediate feedback
                status = "CONNECTED" if result["success"] else "FAILED"
                logger.info(f"Device {result['name']}: {status} ({result['elapsed_time']:.2f}s)")
                
            except Exception as e:
                device = future_to_device[future]
                logger.error(f"Error checking {device['name']}: {str(e)}")
                results.append({
                    "name": device["name"],
                    "type": device["type"],
                    "ip": device["ip"],
                    "success": False,
                    "message": f"Unexpected error: {str(e)}",
                    "elapsed_time": 0
                })
    
    # Print final results
    success_count, failure_count = print_results(results)
    
    # Provide overall status
    if failure_count == 0:
        print("\n✅ All devices are reachable and ready for the lab.")
        return 0
    else:
        print(f"\n❌ {failure_count} device(s) are not reachable. Please check the VPN connection and CML environment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())