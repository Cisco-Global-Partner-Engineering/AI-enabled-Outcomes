
# Agentic AI for Network Operations: Hands-On Lab Guide

## Introduction

Welcome to the Agentic AI for Network Operations lab! This hands-on guide will walk you through setting up and exploring an autonomous network troubleshooting system powered by AI. By the end of this lab, you'll understand how AI agents can detect, diagnose, and remediate network issues with minimal human intervention.

This lab demonstrates a practical implementation of the concepts discussed in the technical blog about Agentic AI for Network Operations. You'll experience firsthand how AI can transform traditional network troubleshooting approaches into efficient, autonomous operations.

## Lab Overview

In this lab, you will:

1. Set up a simulated network environment using Cisco Modeling Labs (CML)
2. Configure and run an AI-powered network troubleshooting agent
3. Introduce a network failure scenario
4. Observe the agent autonomously detect, diagnose, and fix the issue
5. Review the generated reports and insights

## Prerequisites

Before beginning this lab, you'll need:

- A computer with internet access
- Basic understanding of networking concepts
- Python 3.6 or higher installed on your system
- Git installed on your system
- Access to an LLM API (OpenAI GPT-4-1 recommended)
- Ability to connect to a VPN

No advanced programming or networking skills are required - this guide explains each step in detail.

## Detailed Lab Instructions

### Step 1: Book the Cisco dCloud Lab Environment

1. Go to the dCloud catalog: https://dcloud2.cisco.com/content/catalogue
2. In the search bar, type "Cisco Modeling Labs 2.6.1-b11 Sandbox"
3. Click on the lab when it appears in the search results
4. Click the "Schedule" button to reserve your lab instance
5. Choose a date and time slot that works for you
6. Complete the reservation process

After booking, you'll receive an email with VPN connection details. These details will also be available in your dCloud dashboard under "My Hub".

> **Note**: If you're new to dCloud, watch the introduction video here: https://www.youtube.com/watch?v=YtGXPjdFB2Q

### Step 2: Clone the GitHub Repository

1. Open a terminal or command prompt on your computer
2. Navigate to the directory where you want to store the lab files
3. Run the following command:

```
git clone https://github.com/Cisco-Global-Partner-Engineering/AI-enabled-Outcomes.git
```

4. Navigate into the cloned repository:

```
cd "AI-enabled-Outcomes/Usecase 7"
```

### Step 3: Obtain LLM API Keys

This lab uses a Large Language Model (LLM) to power the AI agent. The recommended option is GPT-4-1 from OpenAI.

1. Go to https://platform.openai.com/
2. Sign up or log in to your OpenAI account
3. Navigate to the API section
4. Create a new API key
5. Copy the API key and enter it in 'azure_openai_gpt41_token' in the modules/credentials.py file.

Alternatively, you can use other equivalent LLM services after making sure to adjust the code accordingly in the credentials.py and dochat.py files.

### Step 4: Connect to the dCloud VPN

1. Locate the VPN connection details in your dCloud email or dashboard
2. Using your preferred VPN client, connect to the dCloud VPN with the provided credentials
3. Verify your connection is successful

### Step 5: Set Up the Lab in Cisco Modeling Labs (CML)

1. In your web browser, navigate to https://cml.demo.dcloud.cisco.com/
2. Log in with the following credentials:
   - Username: admin
   - Password: C1sco12345

3. Enter the lab topology :
   - Click on topology titled "Branch office lab Enhanced with configs" 

4. You'll see a network topology appear with multiple devices, similar to 'data/input/topology.png'

5. Verify the lab:
   - Verify that all nodes display a green status, indicating they are running

6. Verify the topology matches the reference image:
   - Open the file `data/input/topology.png` in your cloned repository
   - Compare it with the topology displayed in CML
   - They should look similar, with various network devices connected to each other
   - use the below configs as needed for the nodes to come up
      IOS : 
      ip ssh version 2 
      crypto key generate rsa (and then generate key of 4096 bits)
      username cisco password cisco
      ASA : 
      crypto key generate rsa modulus 4096
      username cisco124 password cisco124
      Then login to asa via ssh from the host and set new password (cisco124) for the 1st time.. use same password as in the credentials file.

### Step 6: Test SSH Connectivity to Lab Devices and install pip packages

1. In your terminal, navigate to the 'modules' directory of the cloned repository
2. Run the lab check script to verify connectivity to all devices:

```
python labcheck.py
```

3. The script should show successful connections to all devices in the lab
4. from the 'Usecase 7' directory, run 'pip install -r requirements.txt' to install all the required packages

### Step 7: Run the Agentic AI Solution (Baseline Test)

1. In your terminal, make sure you're in the 'main' directory of the cloned repository
2. Run the agent script:

```
python agentic.py
```

3. The script will run and should complete successfully, producing a report indicating that the network is healthy
4. Review the output, which shows the agent's process of:
   - Collecting network information
   - Running diagnostics
   - Verifying connectivity
   - Generating a report

### Step 8: Introduce a Network Failure

Now, let's simulate a network failure to see how the agent handles it:

1. In your web browser, go back to the CML interface
2. Right-click on the "branch-router" device in the topology
3. Select "Console" to open a console connection to the device
4. Log in to the router (if prompted for credentials)
5. Enter configuration mode:

```
branch-router# configure terminal
```

6. Shut down an interface to simulate a failure:

```
branch-router(config)# interface GigabitEthernet 0/1
branch-router(config-if)# shutdown
branch-router(config-if)# end
branch-router# write memory
```

7. Exit the console by closing the console window or typing `exit`

> **Note**: You've just simulated a real-world network failure by shutting down an interface on the branch router.

### Step 9: Run the Agentic AI Solution (Troubleshooting Mode)

1. In your terminal, run the agent script again:

```
python agentic.py
```

2. This time, the agent will:
   - Detect a connectivity problem (ping failure)
   - Begin autonomous troubleshooting
   - Collect data from multiple devices in parallel
   - Analyze the collected data
   - Determine the root cause of the issue
   - Generate a detailed Root Cause Analysis (RCA) report
   - Propose remediation commands

3. The script will pause and wait for your confirmation before proceeding with remediation
4. Review the RCA output carefully to understand what the agent discovered. (optionally) If you want to, you can modify 'data/reports/RCA.md' to make any needed changes.
5. When prompted, type `confirm` to allow the agent to implement the fix

### Step 10: Review the Final Report

1. After remediation, the agent will:
   - Verify that the fix was successful
   - Generate a final report
   - Store detailed logs of the entire process

2. Review the final report located at:

```
data/reports/agentic_final_report.json
```

3. Also review the Root Cause Analysis document:

```
data/reports/RCA.md
```

4. Examine the detailed logs for insights about what happened during the troubleshooting:

```
data/insights/detailed/
```

## Understanding How It Works

Now that you've seen the agent in action, let's understand the key components behind it:

### System Architecture

The Agentic AI solution consists of several components:

1. **Orchestration Engine (`agentic.py`)**: Coordinates the end-to-end workflow from detecting issues to remediation.

2. **Root Cause Analysis Engine (`parallel_rca_loop.py`)**: Collects and analyzes device data in parallel to determine the most likely root cause.

3. **Device Interaction Modules**: Connect to different network devices to gather information and implement changes.

4. **AI Integration Layer (`dochat.py`)**: Connects the system to Large Language Models for intelligent analysis.

5. **Telemetry and Verification Modules**: Collect network health data and verify remediation success.

### AI-Powered Process Flow

The system follows a logical troubleshooting workflow:

1. **Alarm Detection**: Identifies when a network issue occurs
2. **Initial Analysis**: Gathers basic information about the problem
3. **Traffic Path Mapping**: Determines which devices might be involved
4. **Device Reconnaissance**: Collects diagnostic information from relevant devices
5. **Root Cause Analysis**: Uses AI to determine the most likely cause
6. **Remediation Planning**: Generates precise commands to fix the issue
7. **Command Execution**: Implements the fix
8. **Verification**: Confirms the issue is resolved
9. **Report Generation**: Documents the entire process

### Benefits Over Traditional Methods

Traditional network troubleshooting requires:
- 30-60 minutes for initial triage
- 1-2 hours for data collection across multiple devices
- 1-3 hours for expert analysis
- 30-60 minutes for remediation planning and execution
- Total: 3-7 hours

The agentic solution reduces this to:
- Automatic triage: < 1 minute
- Parallel data collection: 3-5 minutes
- AI-powered analysis: 2-3 minutes
- Automated remediation: 2-3 minutes
- Total: 8-12 minutes

That's approximately a 95% reduction in time-to-resolution!

## Advanced Exploration (Optional)

If you want to explore further, try these additional activities:

### Examining the Code

1. Open and review key Python files to understand how the system works:
   - `main/agentic.py`: The main orchestration script
   - `main/parallel_rca_loop.py`: The parallel processing engine
   - `modules/dochat.py`: The LLM integration module

2. Look at how the system handles different device types:
   - `modules/send_router.py`: For router communication
   - `modules/execute_cmd_ubuntu.py`: For Linux host communication

### Creating Different Failure Scenarios

Try creating different network failures and see how the agent responds:

1. Shut down different interfaces on various devices
2. Introduce ACL or firewall rules that block traffic
3. Change routing configurations to create suboptimal paths

For each scenario, run the agent and observe its troubleshooting approach.

## Conclusion

Congratulations! You've successfully completed the Agentic AI for Network Operations lab. You've experienced firsthand how AI can transform network operations by:

1. Autonomously detecting network issues
2. Conducting parallel device reconnaissance
3. Using AI to analyze command outputs and determine root causes
4. Generating precise remediation commands
5. Verifying that issues are resolved

This lab demonstrates the future of network operations, where AI agents can dramatically reduce time-to-resolution while improving accuracy and consistency. As this technology evolves, we can expect even more sophisticated capabilities with multi-agent systems providing predictive operations and self-healing infrastructure.

## Additional Resources

- Video demonstration: https://app.vidcast.io/share/1d9f75e5-2c34-4344-a161-cd2a993d8063
- GitHub repository: https://github.com/Cisco-Global-Partner-Engineering/AI-enabled-Outcomes.git
- Technical blog: See [Introducing Agentic AI for Network Operations](https://www.linkedin.com/pulse/agentic-ai-network-operations-expert-level-analysis-autonomous-jose-uugne) for in-depth discussion of the concepts

## Troubleshooting

If you encounter issues during the lab, try these steps:

1. **VPN Connection Problems**: Ensure your VPN is correctly connected to dCloud
2. **CML Access Issues**: Verify you're using the correct URL and credentials
3. **Device Connectivity**: Run the labcheck script again to verify SSH connectivity
4. **Python Errors**: Ensure you have all required Python packages installed
5. **LLM API Issues**: Check that your API key is correctly configured

If problems persist, refer to the demo video or reach out to the lab administrator for assistance.