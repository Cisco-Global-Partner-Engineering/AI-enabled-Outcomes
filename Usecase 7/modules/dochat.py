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


from google import genai
from google.genai import types, errors
from openai import OpenAI, RateLimitError, APIError
import modules.credentials as credentials
import json
import re
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


def dochat(prompt="", messages=[], json=False, model=None, temperature=0.1, llm="openai"):
    """
    Main chat interface supporting both OpenAI and Google's Gemini models.
    
    This function provides a unified interface for both OpenAI and Gemini APIs,
    allowing easy switching between providers via the llm parameter.
    
    Args:
        prompt (str): The user prompt/question
        messages (list): List of message dictionaries with 'role' and 'content' keys
        json (bool): Whether to expect JSON output
        model (str): Specific model to use (defaults based on llm parameter)
                    - OpenAI: 'gpt-5' (default)
                    - Gemini: 'gemini-2.0-flash-exp'
        temperature (float): Temperature for generation (0.0-2.0)
        llm (str): Model provider - 'openai' (default) or 'gemini'
    
    Returns:
        str or dict: Model response as string, or parsed JSON dict if json=True
    """
    
    # Normalize llm parameter
    llm = llm.lower()
    
    if llm == "openai":
        return _dochat_openai(prompt, messages, json, model, temperature)
    elif llm == "gemini":
        return _dochat_gemini(prompt, messages, json, model, temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm}. Supported values: 'openai', 'gemini'")


def _dochat_openai(prompt="", messages=[], json=False, model=None, temperature=0.1):
    """
    OpenAI implementation using the official OpenAI Python SDK with GPT-5 responses API.
    """
    # Use gpt-5 as default model
    if not model:
        model = "gpt-5"
    
    logger.info(f"Sending prompt to OpenAI model: {model}")
    
    # Retry configuration for rate limiting
    max_retries = 5
    initial_retry_delay = 10
    max_retry_delay = 320
    
    # Initialize the OpenAI client
    try:
        client = OpenAI(api_key=credentials.openai_api_key)
    except AttributeError:
        logger.error("OpenAI API key not found in credentials.py. Please add 'openai_api_key = \"YOUR_API_KEY\"'")
        raise ValueError("OpenAI API key not configured in credentials.py")
    
    # Build input list for OpenAI GPT-5 responses API
    api_input = []
    
    if messages:
        # Convert messages to GPT-5 format
        for msg in messages:
            role = msg.get("role", "user")
            content_text = msg.get("content", "")
            
            # Map roles: 'system' -> 'developer', 'model' -> 'assistant'
            if role == "system":
                role = "developer"
            elif role == "model":
                role = "assistant"
            
            # Build content array based on role
            if role == "assistant":
                # Assistant messages use output_text
                content_array = [{"type": "output_text", "text": content_text}]
            else:
                # User and developer messages use input_text
                content_array = [{"type": "input_text", "text": content_text}]
            
            # Add JSON instruction to last user message if needed
            if json and role == "user" and msg == messages[-1]:
                if "json" not in content_text.lower():
                    content_array[0]["text"] += "\nRespond in JSON format."
            
            api_input.append({
                "role": role,
                "content": content_array
            })
    elif prompt:
        # If only prompt provided, use it as user message
        prompt_text = prompt
        if json and "json" not in prompt_text.lower():
            prompt_text += "\nRespond in JSON format."
        
        api_input = [{
            "role": "user",
            "content": [{"type": "input_text", "text": prompt_text}]
        }]
    else:
        raise ValueError("Either 'prompt' or 'messages' must be provided")
    
    # Configure API parameters for GPT-5 responses.create()
    api_params = {
        "model": model,
        "input": api_input,
        "text": {
            "format": {"type": "json_object" if json else "text"},
            "verbosity": "medium"
        },
        "reasoning": {
            "effort": "medium"
        },
        "tools": [],
        "store": True,
        "include": [
            "reasoning.encrypted_content",
            "web_search_call.action.sources"
        ]
    }
    
    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            response = client.responses.create(**api_params)
            
            # Extract response text from GPT-5 response format
            # Response structure: response.output is a list containing reasoning items and messages
            # The actual text response is in the message output item's content
            response_text = None
            
            if hasattr(response, 'output') and response.output:
                # Iterate through output items to find the message with output_text
                for output_item in response.output:
                    # Check if this is a message type (not reasoning)
                    if hasattr(output_item, 'type') and output_item.type == 'message':
                        # Extract text from message content
                        if hasattr(output_item, 'content') and output_item.content:
                            for content_item in output_item.content:
                                if hasattr(content_item, 'type') and content_item.type == 'output_text':
                                    if hasattr(content_item, 'text'):
                                        response_text = content_item.text
                                        break
                        if response_text:
                            break
            
            # Final fallback: convert response to string if extraction failed
            if not response_text:
                logger.warning("Could not extract text from GPT-5 response, using fallback")
                response_text = str(response)
            
            # Process JSON if requested
            if json:
                return process_llm_output(response_text)
            else:
                return response_text
                
        except RateLimitError as e:
            retry_delay = min(initial_retry_delay * (2 ** attempt), max_retry_delay)
            logger.warning(
                f"OpenAI rate limit exceeded. "
                f"Attempt {attempt + 1}/{max_retries}. "
                f"Retrying in {retry_delay} seconds..."
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached. OpenAI API error: {e}")
                raise Exception(f"OpenAI API rate limit exceeded after {max_retries} retries: {e}")
                
        except APIError as e:
            # Handle API errors with retry
            retry_delay = min(initial_retry_delay * (2 ** attempt), max_retry_delay)
            logger.warning(
                f"OpenAI API error. Attempt {attempt + 1}/{max_retries}. "
                f"Retrying in {retry_delay} seconds..."
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached. OpenAI API error: {e}")
                raise Exception(f"OpenAI API error after {max_retries} retries: {e}")
                
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error during OpenAI API call: {e}")
            raise Exception(f"Unexpected OpenAI API error: {e}")
    
    return None


def _dochat_gemini(prompt="", messages=[], json=False, model=None, temperature=0.1):
    """
    Gemini implementation using Google's genai SDK.
    
    Args:
        prompt (str): The user prompt/question
        messages (list): List of message dictionaries with 'role' and 'content' keys
        json (bool): Whether to expect JSON output
        model (str): Specific Gemini model to use (defaults to 'gemini-2.0-flash-exp')
        temperature (float): Temperature for generation (0.0-2.0)
    
    Returns:
        str or dict: Model response as string, or parsed JSON dict if json=True
    """
    # Use gemini-2.0-flash-exp as default model
    if not model:
        model = "gemini-2.0-flash-exp"
    
    logger.info(f"Sending prompt to Gemini model: {model}")
    
    # Retry configuration for rate limiting (exponential backoff)
    max_retries = 5
    initial_retry_delay = 10  # Start with 10 seconds
    max_retry_delay = 320  # Cap at ~5 minutes
    
    # Initialize the client with API key
    try:
        client = genai.Client(api_key=credentials.google_api_key)
    except AttributeError:
        logger.error("Google API key not found in credentials.py. Please add 'google_api_key = \"YOUR_API_KEY\"'")
        raise ValueError("Google API key not configured in credentials.py")
    
    # Convert messages format to Gemini content format
    contents = []
    system_instruction = None
    
    if messages:
        # Extract system instruction if present
        for msg in messages:
            if msg.get("role") == "system":
                system_instruction = msg.get("content", "")
            elif msg.get("role") == "user":
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=msg.get("content", ""))]
                ))
            elif msg.get("role") == "model" or msg.get("role") == "assistant":
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=msg.get("content", ""))]
                ))
    
    # If no messages but prompt provided, use prompt directly
    if not contents and prompt:
        contents = prompt
    elif not contents:
        raise ValueError("Either 'prompt' or 'messages' must be provided")
    
    # Configure generation parameters
    config_params = {
        "temperature": temperature,
    }
    
    # Add system instruction if present
    if system_instruction:
        config_params["system_instruction"] = system_instruction
    
    # Add JSON response configuration if requested
    if json:
        config_params["response_mime_type"] = "application/json"
        # Enhance prompt to request JSON if not already mentioned
        if isinstance(contents, str) and "json" not in contents.lower():
            contents += "\nRespond in JSON format."
        elif isinstance(contents, list) and contents:
            last_user_content = None
            for content in reversed(contents):
                if content.role == "user":
                    last_user_content = content
                    break
            if last_user_content and last_user_content.parts:
                text = last_user_content.parts[0].text
                if "json" not in text.lower():
                    last_user_content.parts[0] = types.Part.from_text(
                        text=text + "\nRespond in JSON format."
                    )
    
    config = types.GenerateContentConfig(**config_params)
    
    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            
            # Extract response text
            response_text = response.text
            
            # Process JSON if requested
            if json:
                return process_llm_output(response_text)
            else:
                return response_text
                
        except errors.ClientError as e:
            # Handle rate limiting (429) and quota errors (403)
            if hasattr(e, 'code') and e.code in [429, 403]:
                retry_delay = min(initial_retry_delay * (2 ** attempt), max_retry_delay)
                logger.warning(
                    f"Rate limit/quota exceeded (HTTP {e.code}). "
                    f"Attempt {attempt + 1}/{max_retries}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Max retries reached. Gemini API error: {e}")
                    raise Exception(f"Gemini API rate limit exceeded after {max_retries} retries: {e}")
            else:
                # Other client errors
                logger.error(f"Gemini API client error: {e}")
                raise Exception(f"Gemini API error: {e}")
                
        except errors.ServerError as e:
            # Handle server errors with retry
            retry_delay = min(initial_retry_delay * (2 ** attempt), max_retry_delay)
            logger.warning(
                f"Gemini server error. Attempt {attempt + 1}/{max_retries}. "
                f"Retrying in {retry_delay} seconds..."
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Max retries reached. Gemini server error: {e}")
                raise Exception(f"Gemini API server error after {max_retries} retries: {e}")
                
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error during Gemini API call: {e}")
            raise Exception(f"Unexpected Gemini API error: {e}")
    
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    
    # Test 1: OpenAI JSON response (default)
    print("=" * 60)
    print("Test 1: OpenAI GPT-5 JSON response (default provider)")
    print("=" * 60)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI. Reply strictly in this JSON format: {'GOAT':<Answer>}."
        },
        {"role": "user", "content": "Who is the GOAT in Tennis?"}
    ]
    response = dochat(messages=messages, json=True, llm="openai")
    print(f"Response: {response}\n")
    

    