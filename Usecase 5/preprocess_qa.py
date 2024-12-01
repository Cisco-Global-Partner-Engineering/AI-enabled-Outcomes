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

import os
import json
from dochat import dochat

# Function to process data from JSON content
def read_json_content(json_data):
    data = []
    for item in json_data:
        content = item.get("content")
        uuid = item.get("uuid")
        if content and uuid:
            data.append((content, uuid))
    return data

# Function to initialize the output JSON file
def initialize_output_json(filename="indexchunks_questions.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return []

# Function to save the new data with question field to JSON file
def save_qa_to_json(output_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(output_data, file, indent=4)
    print(f"Data saved to {output_file}")

# Function to check if the content already exists in the saved output
def content_exists(content, output_data):
    for item in output_data:
        if item.get("content") == content:
            return True
    return False

# Function to synthesize questions and update the JSON data
def synthesize_questions_from_json(json_data, output_file):
    json_content = read_json_content(json_data)
    output_data = initialize_output_json(output_file)
    base_prompt = "Generate a comprehensive question that fully captures all key details of the provided answer. Ensure the question reflects technical and contextual specifics. Output only the question. Answer : "
    
    for index, (content, uuid) in enumerate(json_content, start=1):
        # Skip if this content is already processed and saved
        if content_exists(content, output_data):
            print(f"Skipping already processed content: {content[:50]}...")  # Show first 50 chars of content
            continue

        prompt = f"{base_prompt}\n{content}"
        question = dochat(prompt).strip()  # Assuming dochat generates the question
        qa_entry = {
            "uuid": uuid,
            "content": content,
            "question": question
        }

        # Add to output data and save it immediately after processing each item
        output_data.append(qa_entry)
        save_qa_to_json(output_data, output_file)
        print(f"Processed and saved Q&A pair {index}/{len(json_content)}")
        print(f"Question: {question}\n")
        print(f"Answer: {content}\n")
        print("-------------------------------------------------")

# Main function to run the process
def main():
    with open("data/indexchunks.json", 'r') as file:
        input_json = json.load(file)
    output_file = 'output/indexchunks_questions.json'
    synthesize_questions_from_json(input_json, output_file)

if __name__ == "__main__":
    main()
