# AI enabled Outcomes - Outcome 2

## Overview
This project aims to provide a unified dashboard that delivers three main outcomes: Alerting, Monitoring, and a GenAI interface. It utilizes data from Meraki, Umbrella, and ThousandEyes, and integrates with MongoDB Atlas. The primary goal is to offer pre-configured, ready-to-use solutions that remove the need to work with complex APIs across the Cisco portfolio. The outcomes are pre-tested and guaranteed to work, and the lifecycle of APIs through software versions is maintained.

## Key Features

### 1. Alerting
- **Custom Ticketing**: Integrated with ServiceNow for customizable issue reporting based on specific triggers and Service Level Objectives (SLOs), with cross-domain context enrichment.
- **Reporting**: Comprehensive reporting capabilities.
- **Notifications**: Ability to send Webex notifications for any change in the dashboard elements, allowing near real-time response to service degradation or timely ticket closure.
- **SLOs**: Service Level Objectives for monitoring and reporting.

### 2. Monitoring
- **Modern Single-Pane-of-Glass Dashboard**:
 - **Alarms**: Aggregated alarms from Cisco Meraki, Cisco Umbrella and Cisco ThousandEyes.
 - **Network Health**: Network health aggregation from Cisco Meraki devices, Cisco Umbrella tunnels and Cisco ThousandEyes agents.
 - **Application Health**: Visibility into application flows with health issues flagged by Cisco Meraki and Cisco ThousandEyes.

### 3. GenAI Interface
- **GPT-4 Powered Conversational Interface**: Interact with the dashboard using natural language through a GPT-4 powered conversational interface for AIOps.

## Benefits

- **Get desired outcomes out of the box**: Pre-configured solutions eliminate the need to work with complex APIs.
- **Pre-tested and definite outcomes**: The provided outcomes are thoroughly tested and guaranteed to work as expected.
- **Lifecycle management**: The lifecycle of APIs through software versions is maintained.
- **Cross-architecture dashboard**: Ability to build a unified dashboard across the Cisco architecture.
- **Maximize value from investments**: Extract more value from existing investments in Cisco solutions.

## Technologies Used
- **Programming Languages**: Python, React
- **Data Model**: JSON
- **Database**: MongoDB Atlas


# AI enabled Outcomes - Outcome 2 - For Developers : 

This repository will hold the code for the outcome2

This is a Cross-Domain dashboard for displaying day 2 operations data from the Cisco Controllers.

![image](https://github.com/CiscoDevNet/global-partner-engineering/assets/11584709/4a5ce275-49e1-47c2-9e21-ad0525a7291d)


_Note : The steps here are only for a lab environment. There may be additional considerations like security, performance, scalability, maintainability..etc needed before production use._

Recommended to use Python virtualenv for your python projects :
a) python3 -m venv my_env
b) source my_env/bin/activate

Main steps to run the repo in your local machine :

1) do a git clone of this repository
2) add in the correct .env file in the backend folder
3) For Frontend:
 a) execute "python dashboardControllerREST.py"
 b) go to the frontend folder and execute "npm install" and then "npm start"
4) For Backend:
  a) execute "python ControllerREST.py
  b) to do a dry run, without affecting the db : execute "python drydbPush.py" or to check db content : execute "python dbPull.py" or to update the db : execute "python dbPush.py"

