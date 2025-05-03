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


from openai import AzureOpenAI
from openai import OpenAI
import modules.credentials as credentials
import json
import re
import ollama
import time
import logging
# Get the same logger
logger = logging.getLogger(__name__)


def extract_json_from_output(output_str):
    """
    Extracts a JSON substring from the LLM output.
    
    The function searches for code blocks delimited by triple backticks, 
    optionally labeled as 'json'. This is based on the observation that many
    LLMs output JSON within such fenced blocks (Brown et al., 2020).
    """
    # Regular expression to capture code blocks with or without 'json' specifier.
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", output_str, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        # Fallback: assume the whole output is intended as JSON.
        json_str = output_str.strip()
    return json_str

def fix_common_json_errors(json_str):
    """
    Applies simple fixes to common JSON formatting errors.
    
    For example, trailing commas in objects or arrays are common mistakes
    that break strict JSON parsing (Holtzman et al., 2020).
    """
    # Remove trailing commas before a closing bracket or brace.
    # This regex finds a comma followed by optional whitespace and a closing } or ]
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    return json_str

def robust_json_load(json_str):
    """
    Attempts to load a JSON string, applying cleaning techniques if needed.
    
    This function first tries to parse the JSON string directly. If it fails,
    it applies simple cleaning routines and retries. This approach is inspired by
    prompt engineering techniques (Liu et al., 2021) and error handling in text generation.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try cleaning the string for common errors.
        cleaned_str = fix_common_json_errors(json_str)
        try:
            return json.loads(cleaned_str)
        except json.JSONDecodeError as e2:
            # If still failing, raise an error with details.
            raise ValueError(f"Failed to parse JSON.\nOriginal error: {e}\nAfter cleaning: {e2}\nCleaned JSON:\n{cleaned_str}")

def process_llm_output(output_str):
    """
    Processes LLM output that is supposed to be JSON and returns the parsed data.
    
    This function ties together extraction, error correction, and robust JSON parsing,
    enabling the script to work across different LLMs even if their output JSON isn't perfect.
    """
    extracted_json = extract_json_from_output(output_str)
    return robust_json_load(extracted_json)

def dochat_openrouter(prompt=None, messages=[],json=False, model = None, temperature=0.1): 
    if not model:
        #model = "meta-llama/llama-3.3-70b-instruct"
        #model = "meta-llama/llama-4-maverick"
        #model = "microsoft/phi-4-multimodal-instruct"
        model  = "google/gemma-3-27b-it"
    logging.info(f"Sending the prompt to {model}")
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=credentials.openrouter_key,
    )

    if prompt:
        prompt = str(prompt)

    if json and prompt:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature=temperature, response_format={"type": "json_object"}
        )

        return process_llm_output(completion.choices[0].message.content)
    
    elif prompt:
        completion = client.chat.completions.create(

        model=model,
        messages=[
            {
            "role": "user",
            "content": prompt
            }
        ],
        temperature=temperature
        )

        return completion.choices[0].message.content
    
    elif json and messages:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature, response_format={"type": "json_object"}
        )
        return process_llm_output(completion.choices[0].message.content)
    
    elif messages:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return completion.choices[0].message.content


def dochat_gpto4mini(prompt="",messages=[],json=False, temperature=1):
    temperature = 1 # supports only 1
    max_completion_tokens=50000
    logging.info("Sending the prompt to the azure gpt-o4_mini model")
    client = AzureOpenAI(
        azure_endpoint=credentials.azure_endpoint, 
        api_key=credentials.azure_openai_gpto4mini_token,  
        api_version="2024-12-01-preview",
        timeout=900.0, max_retries=4
    )
    if not messages:
        messages = [
            {
            "role": "system",
            "content": "You are an helpful AI. Your role is to listen to the user and provide the best answer you can."
            },
            {"role": "user", "content": prompt}
        ]
    if json:
        chat_completion = client.chat.completions.create(
            model="o4-mini", response_format={"type": "json_object"}, messages=messages, temperature=temperature, max_completion_tokens=max_completion_tokens
        )
        return process_llm_output(chat_completion.choices[0].message.content)
    else:
        chat_completion = client.chat.completions.create(
            model="o4-mini", messages=messages, temperature=temperature, max_completion_tokens=max_completion_tokens
        )
    return chat_completion.choices[0].message.content


def dochat_gpt41(prompt="",messages=[],json=False, temperature=0.1):
    logging.info("Sending the prompt to the azuregpt-4.1 model")
    client = AzureOpenAI(
        azure_endpoint=credentials.azure_endpoint,  
        api_version="2024-12-01-preview",
        timeout=120.0, max_retries=4,
        api_key=credentials.azure_openai_gpt41_token
    )
    if not messages:
        messages = [
            {
            "role": "system",
            "content": "You are an helpful AI. Your role is to listen to the user and provide the best answer you can."
            },
            {"role": "user", "content": prompt}
        ]
    if json:
        chat_completion = client.chat.completions.create(
            model="gpt-4.1", response_format={"type": "json_object"}, messages=messages, temperature=temperature
        )
        return process_llm_output(chat_completion.choices[0].message.content)
    else:
        chat_completion = client.chat.completions.create(
            model="gpt-4.1", messages=messages, temperature=temperature
        )
    return chat_completion.choices[0].message.content


#implement for ollama
def dochat_ollama(prompt="",messages=[],json=False):

    #model = "mistral-nemo:12b-instruct-2407-q6_K"
    model = "hermes3:latest"
    #model = "hf.co/bartowski/Ministral-8B-Instruct-2410-GGUF:Q8_0"

    logging.info(f"Sending the prompt to the ollama model : {model}")
    if not messages:
        messages = [
            {"role": "system", "content": "You are a cisco network administration expert."},
            {"role": "user", "content": prompt}
        ]

    logging.info(time.localtime())

    if json:
        chat_completion = ollama.chat(model=model,messages=messages,stream = False, format='json')
        logging.info(time.localtime())
        return chat_completion["message"]["content"]
    else:
        chat_completion = ollama.chat(model=model,messages=messages,stream = False)
        logging.info(time.localtime())
        return process_llm_output(chat_completion["message"]["content"])


def dochat(prompt="",messages=[],json=False, model = None, temperature=0.1, llm="azuregpt41"):
    if llm == "openrouter":
        try:
            result = dochat_openrouter(prompt, messages, json, model, temperature)
            if result:
                return result
            else:
                raise ValueError("No response from the model")
        except Exception as e:
            logging.info(f"Error: {e}, retrying")
            return dochat_openrouter(prompt, messages, json, model, temperature)
    elif llm == "azuregpto4mini":
        try:
            result = dochat_gpto4mini(prompt, messages, json, temperature)
            if result:
                return result
            else:
                raise ValueError("No response from the model")
        except Exception as e:
            logging.info(f"Error: {e}, retrying")
            logging.info("Retrying after 30 seconds")
            time.sleep(30)
            # Retry after 30 seconds
            return dochat_gpto4mini(prompt, messages, json, temperature)
    elif llm == "azuregpt41":
        try:
            result = dochat_gpt41(prompt, messages, json, temperature)
            if result:
                return result
            else:
                raise ValueError("No response from the model")
        except Exception as e:
            logging.info(f"Error: {e}, retrying")
            return dochat_gpt41(prompt, messages, json, temperature)
    elif llm == "ollama":
        try:
            return dochat_ollama(prompt, messages, json)
        except Exception as e:
            logging.info(f"Error: {e}, retrying")
            return dochat_ollama(prompt, messages, json)
    else:
        logging.error("Invalid LLM model")
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    #prompt = "answer 4+2, in json format"
    #response = dochat(prompt,json=True)
    #prompt = "Calculate 4+2 and give me the answer. Do not output anything else."
    #prompt = "Who is the GOAT in Tennis?"
    #prompt = input("Enter your question: ")
    messages = [    
        {
            "role": "system",
            "content": "You are an helpful AI. Your role is to listen to the user and provide the best answer you can. reply strictly in this json schema : {'Goat':'Answer'}. Do not output anything else."
        },
        {"role": "user", "content": "Who is the GOAT in Tennis?"}
    ]
    response = dochat(messages=messages,json=True, llm="azuregpto4mini")
    print("Response: ")
    print(response)