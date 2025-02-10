from netmiko import ConnectHandler
import json
import time

def execute_commands(device, commands):
    """
    Connect to a router and execute show commands.

    :param device: Dictionary containing device connection details.
    :param commands: List of show commands to execute.
    :return: Dictionary with command results.
    """
    try:
        # Establish SSH connection to the device
        connection = ConnectHandler(**device)
        
        # Execute each command and store the output
        results = {}
        for command in commands:
            if command.startswith("sleep"):
                print("Sleeping for", int(command.split(" ")[1]), "seconds")
                time.sleep(int(command.split(" ")[1]))
                continue
            # Check current mode and elevate to privileged EXEC mode (enable mode)
            if not connection.check_enable_mode():  # Check if already in enable mode
                connection.enable()  # Enter enable mode
            # Confirm we're in enable mode
            #print("Current prompt:", connection.find_prompt())  # Should show something ending in '#'

            output = connection.send_command(command, read_timeout=10, expect_string=r'#')
            results[command] = output
        
        # Close the connection
        connection.disconnect()
        
        return results
    except Exception as e:
        return {"error": str(e)}

def router_send_command(routerip,send_commands):
    router_device = {
        'device_type': 'cisco_ios',
        'host': routerip,  # Replace with your device's IP address
        'username': 'cisco',       # Replace with your device's username
        'password': 'cisco',       # Replace with your device's password
        'secret': 'cisco',        # Replace with your device's enable secret if needed
        'session_log': 'debug_log.txt',
    }
    
    # Execute show commands and print the results
    results = execute_commands(router_device, send_commands)
    return results

if __name__ == "__main__":
    # Define the router IP address and show command
    router_ip = '198.18.128.111'
    show_commands = ['show access-lists',
                   'show ip interface brief',
                   'show running-config | include access-list',
                   'show ip route']
    router_send_command(router_ip, show_commands)
    results = {}
    with open("debug_log.txt") as file:
        results["results"] = file.read()
    results["topology"] = "Ubuntu1 -> Router -> Ubuntu0"
    print(json.dumps(results, indent=4))
    
    # Save the results to a file
    with open("show_command_results.json", "w") as file:
        json.dump(results, file, indent=4)