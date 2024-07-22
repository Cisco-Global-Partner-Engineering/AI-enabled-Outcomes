# AI enabled Outcomes - Outcome 1

## Overview
This project aims to provide a unified dashboard that delivers three main outcomes: Alerting, Monitoring, and a GenAI interface. It utilizes data from Cisco Catalyst Center, Cisco Catalyst SDWAN, and Cisco ThousandEyes, and integrates with MongoDB Atlas. The primary goal is to offer pre-configured, ready-to-use solutions that remove the need to work with complex APIs across the Cisco portfolio. The outcomes are pre-tested and guaranteed to work, and the lifecycle of APIs through software versions is maintained.

## Key Features

### 1. Alerting
- **Custom Ticketing**: Integrated with ServiceNow for customizable issue reporting based on specific triggers and Service Level Objectives (SLOs), with cross-domain context enrichment.
- **Reporting**: Comprehensive reporting capabilities.
- **Notifications**: Ability to send Webex notifications for any change in the dashboard elements, allowing near real-time response to service degradation or timely ticket closure.
- **SLOs**: Service Level Objectives for monitoring and reporting.

### 2. Monitoring
- **Modern Single-Pane-of-Glass Dashboard**:
 - **Alarms**: Aggregated alarms from Cisco Catalyst Center and SD-WAN.
 - **Network Health**: Network health aggregation from Cisco Catalyst Center and SD-WAN devices.
 - **Application Health**: Visibility into application flows with health issues flagged by Cisco Catalyst Center, SD-WAN, and ThousandEyes.

### 3. GenAI Interface
- **GPT-4 Powered Conversational Interface**: Interact with the dashboard using natural language through a GPT-4 powered conversational interface for AIOps.

## Benefits

- **Get desired outcomes out of the box**: Pre-configured solutions eliminate the need to work with complex APIs.
- **Pre-tested and definite outcomes**: The provided outcomes are thoroughly tested and guaranteed to work as expected.
- **Lifecycle management**: The lifecycle of APIs through software versions is maintained.
- **Cross-architecture dashboard**: Ability to build a unified dashboard across the Cisco architecture.
- **Maximize value from investments**: Extract more value from existing investments in Cisco solutions.

## Technologies Used
- **Programming Languages**: Python
- **Data Model**: JSON
- **Database**: MongoDB Atlas, Charts

# AI enabled Outcomes - Outcome 2 - For Developers : 

This repository will hold the code for the MSP Dashboard : https://charts.mongodb.com/charts-global-msp-noc-vktwd/public/dashboards/9aaa143d-2ec9-44a1-a4e2-44dee0a18c64 

![242937219-bef22c53-412a-44d0-8dbe-48d87e9d66ab](https://github.com/joeljos/GPRS-MSP-Dashboard/assets/11584709/d41bad5b-7006-4eee-8067-43b88c15bb06)

This is a Cross-Domain dashboard for displaying day 2 operations data from the Cisco Controllers. The final output is as shown in the chart above.

_Note : The steps here are only for a lab environment. There may be additional considerations like security, performance, scalability, maintainability..etc needed before production use._

Recommended to use Python virtualenv for your python projects :
1. python3 -m venv my_env
2. source my_env/bin/activate

![Lab Guide](https://github.com/CiscoSE/GPRS-MSP-Dashboard/assets/11584709/2eff5d71-6aac-4cfe-b180-cd34e56bb52f)
