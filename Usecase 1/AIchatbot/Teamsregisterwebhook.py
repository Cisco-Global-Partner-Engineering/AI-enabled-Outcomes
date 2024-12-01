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


import requests
import credentials

# Replace <YOUR_ACCESS_TOKEN> with your bot's access token
ACCESS_TOKEN = credentials.webex_bot_token

# Function to retrieve a list of webhooks
def get_webhooks():
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.get('https://webexapis.com/v1/webhooks', headers=headers)
    return response.json().get('items', [])

# Function to delete a webhook by ID
def delete_webhook(webhook_id):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    response = requests.delete(f'https://webexapis.com/v1/webhooks/{webhook_id}', headers=headers)
    if response.status_code == 204:
        print(f"Webhook with ID '{webhook_id}' deleted successfully.")
    else:
        print(f"Failed to delete webhook with ID '{webhook_id}'.")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")

# Main entry point
if __name__ == '__main__':
    # Retrieve a list of webhooks
    webhooks = get_webhooks()
    
    # Delete each webhook
    for webhook in webhooks:
        webhook_id = webhook.get('id')
        delete_webhook(webhook_id)
    
    # Replace <YOUR_WEBHOOK_URL> with the URL that should receive the webhook events
    WEBHOOK_URL = 'https://mspwebexbot.azurewebsites.net/'

    # Define the webhook payload
    webhook_data = {
        'name': 'My Webhook',
        'targetUrl': WEBHOOK_URL,
        'resource': 'messages',
        'event': 'created'
        #'filter': 'roomId=Y2lzY29zcGFyazovL3VzL1JPT00vMDYyODQ1NjAtZDU3MC0xMWVlLTgxYjYtZjkzOTljN2FhZjE3'  # Replace with the roomId where your bot is listening
    }

    # Send the request to register the webhook
    headers = {'Authorization': 'Bearer ' + ACCESS_TOKEN, 'Content-Type': 'application/json'}
    response = requests.post('https://api.ciscospark.com/v1/webhooks', json=webhook_data, headers=headers)

    # Check the response status code
    if response.status_code == requests.codes.ok:
        print('Webhook registered successfully')
    else:
        print('Error registering webhook: ' + response.text)

