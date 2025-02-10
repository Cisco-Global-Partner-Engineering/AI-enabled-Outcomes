import paramiko
import json

# Define remote Ubuntu machine connection details
ubuntu_device = {
    'host': '198.18.128.112',  # Replace with your remote Ubuntu machine's IP address
    'username': 'cisco',     # Replace with your remote Ubuntu machine's username
    'password': 'cisco',   # Replace with your remote Ubuntu machine's password
}
# Target IP address to ping
target_ip = '10.10.10.2'

def ping_from_remote_ubuntu(device=ubuntu_device, target_ip=target_ip):
    """
    Perform a ping from a remote Ubuntu machine.

    :param device: Dictionary containing device connection details.
    :param target_ip: IP address to ping.
    :return: Ping result as a string.
    """
    try:
        # Establish SSH connection to the remote Ubuntu machine
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device['host'], username=device['username'], password=device['password'])
        
        # Execute the ping command
        stdin, stdout, stderr = ssh.exec_command(f"ping -c 4 {target_ip}")
        output = stdout.read().decode()
        
        # Close the connection
        ssh.close()

        # Save the ping result to a JSON file
        alarm = {"alarm": "ping", "result": output, "topology": f"ubuntu1 (20.20.20.2) --> router-gw (198.18.128.111) --> ubuntu2 ({target_ip})"}
        with open("ping_result.json", "w") as file:
            json.dump(alarm, file)
        
        return alarm
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    
    # Perform ping from remote Ubuntu machine and print the result
    result_ubuntu = ping_from_remote_ubuntu(ubuntu_device, target_ip)
    print("Ping result from remote Ubuntu machine:")
    print(result_ubuntu)