
azure_openai_gpt41_token = ""
azure_openai_gpto4mini_token = ""
webex_access_token = ""
websearchkey=""
openrouter_key = ""
azure_endpoint=""


#################################

# Device credentials structure
devices = [
    {
        "name": "branch-router",
        "type": "Cisco IOS virtual Router",
        "ip": "198.18.1.100",
        "username": "cisco",
        "password": "cisco",
        "enable_password": "cisco",
        "port": 22,
    },
    {
        "name": "branch-fw",
        "type": "Cisco virtual ASA Firewall",
        "ip": "198.18.1.109",
        "username": "cisco",    
        "password": "cisco124",
        "enable_password": "cisco124",
        "port": 22,
    },
    {
        "name": "server",
        "type": "alpine virtual linux",
        "ip": "198.18.1.113",
        "username": "cisco",
        "password": "cisco",
        "port": 22,
    },
    {
        "name": "remote-worker",
        "type": "alpine virtual linux",
        "ip": "198.18.1.115",
        "username": "cisco",
        "password": "cisco",
        "port": 22,
    }

]