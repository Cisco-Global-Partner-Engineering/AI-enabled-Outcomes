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


import credentials
from openai import AzureOpenAI
from anthropic import Anthropic
import analyze
import json
from pprint import pprint

class ChatClient:
    def __init__(self, api_type="azure"):
        """Initialize chat client with specified API type ('azure' or 'claude')"""
        self.api_type = api_type    
        if api_type == "azure":
            self.azure_client = AzureOpenAI(
                azure_endpoint="https://openaigpts.openai.azure.com/",
                api_key=credentials.azure_openai_token,
                api_version="2024-02-15-preview"
            )
        elif api_type == "claude":
            self.claude_client = Anthropic(api_key=credentials.claude_token)
        else:
            raise ValueError("api_type must be either 'azure' or 'claude'")

    def chat(self, query, data, runbook):
        """Send prompt to selected API and get response"""
        if self.api_type == "azure":
            return self._azure_chat(query, data, runbook)
        else:
            return self._claude_chat(query, data, runbook)

    def _azure_chat(self, query, data, runbook):
        """Handle chat with Azure OpenAI API"""
        print("Sending the prompt to the azuregpt-4o model")
        messages = [
            {"role": "system", "content": f"""
Analyze the alarm information: {data} and the runbook: {runbook} while keeping the following in mind:

1. Think step by step: Begin by reviewing the alarm data. Identify any key issues, error codes, timestamps, or unusual metrics that stand out. Pay attention to critical patterns or anomalies that could indicate a problem.
   
2. Cross-reference the alarm data with the steps in the runbook. Focus on identifying any troubleshooting actions associated with the specific error codes or UUIDs mentioned in the alarm information.

3. Extract relevant insights from both the alarm data and the runbook. Focus on the most immediate and applicable details that could help guide the user in troubleshooting the issue.

4. Based on the analysis, provide concise and actionable troubleshooting steps or checks for the user. These steps should be derived solely from the alarm information and runbook, and must be directly applicable to the problem at hand.

5. Do not reference or explicitly mention the runbook in your response. Ensure the user receives a seamless set of insights without requiring additional external context.

6. Always include UUIDs or other unique identifiers from the alarm data as applicable, as these are critical for accurately addressing the issue.

Remember to approach this systematically, ensuring that each part of the process is carefully considered and applied. Reply as concisely as possible.
"""
},
            {"role": "user", "content": query}
        ]
        #print("Length of data:", len(data))
        chat_completion = self.azure_client.chat.completions.create(
            model="azuregpt-4o", 
            messages=messages, 
            temperature=0.7,
            max_tokens=4096
        )
        
        response = chat_completion.choices[0].message.content
        return response

    def _claude_chat(self, query, data, runbook):
        """Handle chat with Claude API"""
        print("Sending the prompt to Claude")
        
        # Construct the messages list format required by Claude
        messages = [
            {
                "role": "user",
                "content": f"""
Analyze the alarm information: {data} and the runbook: {runbook} while keeping the following in mind:

1. Think step by step: Begin by reviewing the alarm data. Identify any key issues, error codes, timestamps, or unusual metrics that stand out. Pay attention to critical patterns or anomalies that could indicate a problem.
   
2. Cross-reference the alarm data with the steps in the runbook. Focus on identifying any troubleshooting actions associated with the specific error codes or UUIDs mentioned in the alarm information.

3. Extract relevant insights from both the alarm data and the runbook. Focus on the most immediate and applicable details that could help guide the user in troubleshooting the issue.

4. Based on the analysis, provide concise and actionable troubleshooting steps or checks for the user. These steps should be derived solely from the alarm information and runbook, and must be directly applicable to the problem at hand.

5. Do not reference or explicitly mention the runbook in your response. Ensure the user receives a seamless set of insights without requiring additional external context.

6. Always include UUIDs or other unique identifiers from the alarm data as applicable, as these are critical for accurately addressing the issue.

Remember to approach this systematically, ensuring that each part of the process is carefully considered and applied. Reply as concisely as possible.
\n\nUser: {query}"""
            }
        ]
        #print("Length of data:", len(data))
        # Create the message with required parameters
        message = self.claude_client.messages.create(
            max_tokens=8192,  # Adjust this value based on your needs
            messages=messages,
            model="claude-3-5-sonnet-20240620",
            temperature=0.1
        )
        
        # Extract the response content
        if hasattr(message.content[0], 'text'):
            response = message.content[0].text
        else:
            response = message.content[0]
        
        return response

def main():
    if(analyze.analyze_alarms()):
        print("Alarm analysis completed successfully")
        # Read message data from file
        with open('alarm_analysis_results.json', 'r') as f:
            data = json.load(f)
        data = data["alarm_reduction"]["reduced_alarms"]
        print("Length of data:", len(data))
        #pprint(data)

        with open('runbook.txt', 'r') as f:
            runbook = f.read()

        while True:
            # Get user input
            query = input("Enter your Query ('exit' to quit): ")
            if query.lower() == "exit":
                break
            # Create chat client (default to Azure)
            chat_client = ChatClient(api_type="azure")  # or "claude"
            responselist = []
            # increment in terms of 25 till the length of data
            incr = 25
            for i in range(0, len(data), incr):
                print("i:", i)
                if i+incr > len(data):
                    chatdata = data[i:]
                else:
                    chatdata = data[i:i+incr]
                # Get response
                #print("Length of data:", len(chatdata))
                responselist.append(chat_client.chat(query, chatdata, runbook))
            chat_client = ChatClient(api_type="azure")  # or "claude"
            #pprint(responselist)
            response = chat_client.chat(query, responselist, runbook)
            print("Response:", response)
    else:
        print("Alarm analysis failed")

if __name__ == "__main__":
    main()

