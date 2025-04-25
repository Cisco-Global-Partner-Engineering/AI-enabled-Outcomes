# Agentic AI for Operations

## License

```text
Copyright (c) 2025 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
[https://developer.cisco.com/docs/licenses](https://developer.cisco.com/docs/licenses)
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
```

* **Author:** Joel Jose <joeljos@cisco.com>
* **Copyright:** Copyright (c) 2025 Cisco and/or its affiliates.
* **License:** Cisco Sample Code License, Version 1.1

## Overview

Agentic AI for Operations is an advanced network monitoring and troubleshooting system that leverages AI to automate the detection, analysis, and remediation of network issues. This solution combines telemetry collection, intelligent analysis, and automated remediation to minimize network downtime and reduce the need for manual intervention.

## Project Architecture

The project is structured as follows:

```
data/                # Data storage directory for all telemetry and analysis results
  command_results/   # Stores raw command outputs from devices
  input/             # Input data including topology and alarm information
  insights/          # AI-generated insights about device states
    detailed/        # Detailed per-device analysis
    summary/         # Summarized insights
  reports/           # Final reports and remediation logs
main/                # Core application scripts
  agentic.py         # Main orchestration script
  parallel_rca_loop.py # Root Cause Analysis engine
modules/             # Supporting modules for various functions
  credentials.py     # Device access credentials
  dochat.py          # LLM interface for AI analysis
  execute_cmd_ubuntu.py # Linux command execution
  getjson.py         # JSON handling utilities
  ping_client*.py    # Network testing utilities
  send_router.py     # Network device command execution
  telemetry.py       # Telemetry collection module
```

## Key Components

### agentic.py

The main orchestration script that drives the entire workflow with the following key functions:

1. **Alarm Intake (`new_alarm_intake()`)**: Collects telemetry data by running ping tests across the network and processes this data as alarms for analysis.

2. **Agentic Function (`agentic()`)**: Orchestrates the end-to-end workflow with these key stages:
   - Generates initial reports for current alarms
   - Initiates workflow based on AI insights
   - Maps traffic paths affected by alarms
   - Confirms alarm status through ongoing monitoring
   - Triggers Root Cause Analysis (RCA)
   - Executes automated remediation based on RCA
   - Verifies remediation success
   - Generates comprehensive summary reports

3. **Automated Remediation Loop**: Implements a feedback loop that:
   - Confirms active alarm status
   - Executes RCA to identify root causes
   - Generates and applies remediation commands
   - Verifies resolution success
   - Repeats until resolved or limit reached

### parallel_rca_loop.py

A sophisticated Root Cause Analysis engine that systematically investigates network issues:

1. **Recon Function (`recon()`)**: 
   - Collects comprehensive device data in parallel
   - Processes multiple devices simultaneously for efficiency
   - Generates detailed insights for each device

2. **Device Processing (`process_device()`)**: 
   - Intelligently generates relevant diagnostic commands per device type
   - Executes commands and collects results
   - Processes command outputs to extract actionable insights

3. **Insight Generation (`generate_insight()`)**: 
   - Analyzes command outputs using AI
   - Identifies anomalies, errors, and configuration issues
   - Correlates findings with alarm context and network topology

4. **RCA Function (`find_rca()`)**: 
   - Synthesizes all device insights
   - Determines the most probable root cause
   - Generates specific remediation commands
   - Produces a comprehensive RCA report

## Workflow

1. **Alarm Detection**: The system monitors network health through continuous telemetry collection.

2. **Initial Analysis**: When an alarm is detected, the system generates an initial report with classification and prioritization.

3. **Traffic Path Analysis**: The system identifies all devices in the affected traffic path.

4. **Device Reconnaissance**: Parallel collection of diagnostic data from all relevant devices.

5. **Root Cause Analysis**: AI analysis of collected data to determine the most likely root cause.

6. **Automated Remediation**: Generation and execution of commands to fix the identified issues.

7. **Verification**: Confirmation that remediation steps have resolved the alarm.

8. **Report Generation**: Comprehensive documentation of the entire process.

## Advanced Features

- **Parallel Processing**: Multiple devices are analyzed simultaneously for faster troubleshooting
- **Human-in-the-Loop Mode**: Optional confirmation steps for critical remediation actions
- **Progressive Remediation**: Multi-attempt remediation with verification between attempts
- **Detailed Logging**: Comprehensive logging for audit and review
- **Device-Specific Analysis**: Tailored diagnostic approaches for different network device types
- **Comprehensive Reporting**: Detailed initial and final reports documenting the entire process

## Device Support

The system supports multiple types of network devices:
- Cisco IOS Routers
- Cisco IOS Layer 2 Switches
- Cisco Virtual ASA Firewalls
- Alpine Virtual Linux hosts

## AI Integration

The system leverages multiple LLM-based components:
- **Command Generation**: AI suggests the most relevant diagnostic commands
- **Output Analysis**: AI interprets command outputs to identify issues
- **Root Cause Determination**: AI correlates findings to identify probable root causes
- **Remediation Planning**: AI generates precise remediation commands

## Example Use Case

In a typical scenario:
1. A connectivity issue is detected via ping failures
2. The system identifies all devices in the affected traffic path
3. Diagnostic commands are generated and executed on each device
4. Command outputs are analyzed to identify anomalies
5. The system identifies a specific misconfiguration (e.g., ACL issue, interface down)
6. Remediation commands are generated and executed
7. The system verifies the issue is resolved through follow-up telemetry
8. A comprehensive report documents the entire incident

## Requirements

- Python 3.6+
- Network devices with SSH/CLI access (available in [Cisco dCloud](https://dcloud2-sng.cisco.com/content/demo/512093?returnPathTitleKey=content-view))
- Required Python packages (see requirements.txt)
- Access to OpenAI or Azure OpenAI services
