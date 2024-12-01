analyze.py

# Alarm Analyzer

The **Alarm Analyzer** is a Python-based tool designed to process, analyze, and reduce alarm data efficiently using clustering and other techniques. It provides insights into alarms and highlights patterns by clustering similar alarms and reducing redundancies.

## Features

- **Data Preprocessing**: Converts raw alarm data into a structured format suitable for analysis.
- **Alarm Reduction**: Implements clustering (via DBSCAN) to group similar alarms and select representative alarms.
- **Detailed Explanations**: Generates comprehensive explanations for alarm reduction and clustering.
- **Customizable Parameters**: Allows flexibility in clustering settings (`eps`, `min_samples`) and time-window-based reductions.

## Workflow

1. **Input Data**: 
   - Provide raw alarm data (JSON format).
   - Includes fields like `devices`, `values`, `entry_time`, `severity`, etc.

2. **Data Preparation**:
   - Flattens nested data structures.
   - Converts timestamps to a human-readable format.
   - Removes null/empty fields.

3. **Analysis**:
   - Choose between:
     - **Clustering-based Reduction**: Groups alarms using DBSCAN based on their similarity.
     - **Time-Window Reduction**: Groups alarms within a specified time window for simplification.
   - Generates summaries and explanations for reduced alarms.

4. **Results**:
   - Provides reduced alarms with a summary of the analysis.
   - Includes details like reduction ratio, clusters formed, and affected components.

## Example Usage

```python
from alarm_analyzer import AlarmAnalyzer

# Load your raw alarm data (replace with actual JSON data)
raw_alarms = [
    {"type": "Critical", "entry_time": 1698432000000, "devices": [{"system-ip": "192.168.1.1"}], ...}
]

# Initialize the analyzer
analyzer = AlarmAnalyzer(raw_alarms)

# Perform analysis with clustering
results = analyzer.analyze(use_clustering=True, eps=0.5, min_samples=3)

# Display the results
print(json.dumps(results, indent=2))
```

## Dependencies

- **Python 3.7+**
- Libraries:
  - `pandas`
  - `numpy`
  - `scikit-learn`

## Installation

```bash
pip install -r requirements.txt
```

## How It Works

1. **Clustering**: Groups alarms by time, severity, and component using DBSCAN.
2. **Reduction**: Selects the most significant alarms (e.g., highest severity) as representatives for each cluster.
3. **Summarization**: Provides an overview of the alarm reduction process and its impact.

## Customization

You can modify parameters to suit your needs:
- `eps`: Maximum distance between two samples for clustering.
- `min_samples`: Minimum number of samples to form a cluster.
- `time_window_seconds`: Time window size for grouping alarms without clustering.



-----------------------------------------------------------------


## Chat.py

# README.md

## Overview

This project provides an automated way to analyze alarm data and generate troubleshooting responses by utilizing AI models from Azure OpenAI and Claude. It integrates a step-by-step process to review alarm data, reference a runbook, and produce actionable insights. Users can input queries and get AI-powered responses based on the alarm data and troubleshooting steps.

## Features

- **Alarm Data Analysis**: The program reads alarm data, analyzes it based on a provided runbook, and provides troubleshooting steps.
- **Support for Multiple AI Models**: The system supports both the Azure OpenAI GPT model and Claude by Anthropic, allowing users to choose which AI model to use for generating responses.
- **Interactive Interface**: Users can input queries to get responses based on the processed alarm data.
- **Seamless Integration**: The system processes alarm data and runbook information, generating responses without requiring manual intervention.

## Setup

### Prerequisites

- Python 3.8+
- Required Python libraries (e.g., `openai`, `anthropic`, `json`, `pprint`)

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

Make sure you have the correct credentials for Azure OpenAI and Claude API.

### Configuration

- The code requires credentials for accessing both the Azure OpenAI and Claude APIs, which are stored in the `credentials.py` file. 
- The `runbook.txt` file should contain the troubleshooting steps, which will be referenced in the analysis.
- The `alarm_analysis_results.json` file should contain the alarm data to be processed.

## How It Works

1. **ChatClient Class**: 
   - This class manages the connection to either the Azure OpenAI or Claude API based on the user's preference.
   - It handles sending prompts to the selected API and receiving the responses.

2. **`chat` Method**: 
   - This method is used to send a query to the chosen AI model and retrieve a response. It calls either `_azure_chat` or `_claude_chat` based on the `api_type` argument.

3. **`_azure_chat` and `_claude_chat` Methods**: 
   - These methods structure the request in the format required by each respective API and send the alarm data along with a detailed set of instructions for analysis.
   - They receive the response and return it to the user.

4. **Main Functionality**:
   - The `main` function orchestrates the entire process:
     - It reads the alarm data and runbook file.
     - It continuously accepts user input (query).
     - It processes the alarm data in chunks, sends it to the AI model, and receives a response.
     - It displays the AI-generated response to the user.

## Example Usage

1. Run the script:

```bash
python script_name.py
```

2. When prompted, input your query related to the alarm data:

```
Enter your Query ('exit' to quit): How should we resolve the connectivity issue?
```

3. The AI will analyze the alarm data, reference the runbook, and provide a troubleshooting response.

4. To exit, type `exit`.

## Error Handling

- If the `api_type` is invalid (neither "azure" nor "claude"), an error is raised.
- If the alarm analysis fails, the program will display a failure message.

## License

This project is licensed under the Cisco Sample Code License, Version 1.1. You can find the full license details [here](https://developer.cisco.com/docs/licenses).