from flask import Flask, jsonify, request, Response 
import json  
from agentic import agentic  # Import the Agentic AI functions  
import time
from flask_cors import CORS  

app = Flask(__name__)  
CORS(app)  # Enable CORS for all routes 

# Path to the JSON files used by the Agentic AI system
AGENTIC_RESPONSE_FILE = 'agentic_response_insights.json'   
COMBINED_ALARMS_FILE = AGENTIC_RESPONSE_FILE 
 
  
  
# Helper function to load JSON data  
def load_json(filepath):  
    try:  
        with open(filepath, 'r') as f:  
            return json.load(f)  
    except FileNotFoundError:  
        return {}  
  
  
# Helper function to save JSON data  
def save_json(filepath, data):  
    with open(filepath, 'w') as f:  
        json.dump(data, f, indent=4)  
  
  
# Endpoint: GET /alarms  
@app.route('/alarms', methods=['GET'])  
def get_alarms():  
    """  
    Fetch all alarms. Supports optional query parameters for filtering.  
    Example: /alarms?severity=High&status=Urgent  
    """  
    alarms = load_json(AGENTIC_RESPONSE_FILE).get("Alarms", [])  
  
    return jsonify({"alarms": alarms})

# Endpoint: GET /runbook  
@app.route('/runbook', methods=['GET'])  
def get_runbook():  
    with open("runbook.txt", "r") as f:
        runbook = f.read()
    return jsonify({"runbook": runbook})

#Endpoint: POST /runbook
@app.route('/runbook', methods=['POST'])
def update_runbook():
    runbook = request.json.get("runbook", "")
    with open("runbook.txt", "w") as f:
        f.write(runbook)
    return jsonify({"message": "Runbook updated successfully."})

  
# Endpoint: GET /alarms/<alarm_id>  
@app.route('/alarms/<alarm_id>', methods=['GET'])  
def get_alarm_by_id(alarm_id):  
    """  
    Fetch detailed information about a specific alarm by ID.  
    """  
    alarms = load_json(AGENTIC_RESPONSE_FILE).get("Alarms", [])  
    alarm = next((alarm for alarm in alarms if alarm.get('Alarm ID') == alarm_id), None)  
  
    if alarm is None:  
        return jsonify({"error": "Alarm not found"}), 404  
  
    return jsonify({"alarm": alarm})  
  
  
# Endpoint: POST /alarms/<alarm_id>/resolve  
@app.route('/alarms/<alarm_id>/resolve', methods=['POST'])  
def resolve_alarm(alarm_id):  
    """  
    Mark an alarm as resolved.  
    """  
    alarms = load_json(AGENTIC_RESPONSE_FILE).get("Alarms", [])  
    alarm = next((alarm for alarm in alarms if alarm.get('Alarm ID') == alarm_id), None)  
  
    if alarm is None:  
        return jsonify({"error": "Alarm not found"}), 404  
  
    # Update the alarm status  
    alarm['Status'] = 'Resolved (marked)'  
    alarm['Resolved Time'] = time.strftime("%Y-%m-%d %H:%M:%S")  

    with open("alarm_history.json", "r") as f:
        alarm_history = json.load(f)
        alarm_history.append(alarm)
    with open("alarm_history.json", "w") as f:
        json.dump(alarm_history, f, indent=4)

    with open("agentic_response.json","r") as f:
        agentic_response = json.load(f)
        agentic_response["Alarms"] = [alarm for alarm in agentic_response["Alarms"] if alarm.get('Alarm ID') != alarm_id]
    with open("agentic_response.json","w") as f:
        json.dump(agentic_response, f, indent=4)

    # remove alarm from alarms
    alarms = [alarm for alarm in alarms if alarm.get('Alarm ID') != alarm_id]

    # Save the updated alarms back to the file  
    save_json(AGENTIC_RESPONSE_FILE, {"Alarms": alarms})  
  
    return jsonify({"message": f"Alarm {alarm_id} marked as resolved.", "alarm": alarm})  
  
@app.route('/stream_log')
def stream_log():
    def generate_log():
        try:
            with open('agentic_debug.log', 'r') as f:
                # Start from the beginning of the file
                f.seek(0)
                while True:
                    line = f.readline()
                    if not line:
                        # If EOF, wait briefly and check again
                        time.sleep(0.1)
                        continue
                    # Yield the line as an SSE-formatted message
                    yield f"data: {line}\n\n"
        except Exception as e:
            app.logger.error(f"Error streaming log: {str(e)}")
    
    return Response(generate_log(), mimetype='text/event-stream')

  
# Endpoint: POST /alarms/<alarm_id>/workflow  
@app.route('/alarms/<alarm_id>/workflow', methods=['POST'])  
def trigger_workflow(alarm_id):  
    """  
    Trigger a workflow (e.g., Webex Notification) for the given alarm.  
    """  
    alarms = load_json(AGENTIC_RESPONSE_FILE).get("Alarms", [])  
    alarm = next((alarm for alarm in alarms if alarm.get('Alarm ID') == alarm_id), None)  
  
    if alarm is None:  
        return jsonify({"error": "Alarm not found"}), 404  
  
    # Trigger a workflow (stubbed here; replace with actual workflow logic)  
    workflow = request.json.get("workflow", "webex_notification")  
    if workflow == "webex_notification":  
        # Example: send a Webex notification (stubbed)  
        return jsonify({"message": f"Webex notification triggered for alarm {alarm_id}."})  
  
    return jsonify({"error": "Invalid workflow specified"}), 400  
  
  
# Endpoint: POST /alarms/refresh  
@app.route('/alarms/refresh', methods=['POST'])  
def refresh_alarms():  
    """  
    Trigger the Agentic AI pipeline to process new alarm data.  
    """  
    try:  
        print("Refreshing alarm data...")
        # Execute the Agentic AI pipeline 
        insights = agentic()  
        return jsonify({"message": "Alarm data refreshed successfully.", "insights": insights})  
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  
  
  
if __name__ == '__main__':  
    app.run(debug=True)  