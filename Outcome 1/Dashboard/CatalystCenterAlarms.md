# Cisco Catalyst Center Alarm Retrieval

This Python code is designed to retrieve alarms from Cisco Catalyst Center and present them in a structured format. Here's a summary of the code:

## Imports
- `CatalystCenter_auth`: This module likely contains functions for authenticating with Cisco Catalyst Center API.
- `pprint`: A module for pretty-printing Python data structures.

## Functions

### `get_data()`

This function retrieves all active alarms from Cisco Catalyst Center and returns a list of dictionaries containing the following keys for each alarm:

- `severity` (str): The severity of the alarm (e.g., major, moderate, warning).
- `summary` (str): A summary of the alarm.
- `name` (str): The name of the device associated with the alarm.
- `url` (str): The URL to the alarm in the Cisco Catalyst Center dashboard.

The function performs the following steps:

1. Retrieves active issues from the `/dna/intent/api/v1/issues` endpoint.
2. For each active issue, retrieves enrichment details from the `/dna/intent/api/v1/issue-enrichment-details` endpoint.
3. For each enrichment detail, retrieves device details from the `/dna/intent/api/v1/device-detail` endpoint.
4. Formats the alarm data into a dictionary with the required keys (`severity`, `summary`, `name`, `url`).
5. Appends the formatted alarm data to a list.
6. Returns the list of alarms.

## Main Execution

If the script is run directly (not imported as a module), it calls the `get_data()` function and pretty-prints the resulting list of alarms using `pprint`.

## Dependencies

This code relies on the `CatalystCenter_auth` module for authentication and API interaction with Cisco Catalyst Center. It also assumes that the necessary authentication credentials and base URLs are defined within the `CatalystCenter_auth` module.