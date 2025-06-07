"""
This file contains the endpoints calling the Simod API.

The endpoints are:
- /api/start-simod-discovery
- /api/start-simod-simulation

Example curl commands:
- Start simod discovery
    curl -D headers.txt -X POST "http://localhost:8888/api/start-simod-discovery?user_id=cs_user&event_log_id=1" -o simod_output.zip
    curl -D headers.txt -X POST "http://localhost:8888/api/start-simod-discovery?user_id=cs_user&event_log_id=1&name=name_scenario&save_boolean=true" -o simod_output.zip
- Start simod simulation
    curl -X GET "http://localhost:8888/api/start-simod-simulation?user_id=cs_user&scenario_id=1" -o simulated_event_log.csv
    curl -X GET "http://localhost:8888/api/start-simod-simulation?user_id=cs_user&scenario_id=1&save_boolean=true" -o simulated_event_log.csv
"""

import zipfile
from io import BytesIO

import requests
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_event_log import DBManagerEventLog
from src.db_managers.db_manager_simod_output import DBManagerSimodOutput
from src.db_managers.db_manager_simod_scenarios import DBManagerSimodScenario

db_manager_event_log = DBManagerEventLog()
db_manager_simod_scenario = DBManagerSimodScenario()
db_manager_simod_output = DBManagerSimodOutput()

simod_bp = Blueprint("simod", __name__)


@simod_bp.route("/api/start-simod-discovery", methods=["POST"])
def start_simod_discovery():
    """
    Start a Simod discovery given a user id and an event log id.

    Args:
        user_id (query): ID of the user (required).
        event_log_id (query): ID of the event log (required).
        save_boolean (query, optional): Boolean to save the discovery scenario in the database
        name (query, optional): Name of the discovery scenario to save in the database

    Returns:
        file: ZIP file containing the discovered process model (BPMN) and parameters.
        header: X-Scenario-ID containing the id of the saved discovery scenario.

    Curl example:
        curl -D headers.txt -X POST "http://localhost:8888/api/start-simod-discovery?user_id=cs_user&event_log_id=1" -o simod_output.zip
        curl -D headers.txt -X POST "http://localhost:8888/api/start-simod-discovery?user_id=cs_user&event_log_id=1&name=name_scenario&save_boolean=true" -o simod_output.zip
        curl -D headers.txt -X POST "http://localhost:8888/api/start-simod-discovery?user_id=cs_user&event_log_id=1&name=name_scenario&save_boolean=true" -F "parameters=@params.json" -o simod_output.zip
    """
    # Get user id and event log id from query parameters
    user_id = request.args.get("user_id")
    event_log_id = request.args.get("event_log_id")
    name = request.args.get("name")
    save_boolean = request.args.get("save_boolean")
    if not user_id or not event_log_id:
        return jsonify({"status": "error", "message": "Missing user_id or event_log_id parameters"}), 400

    # Get event log from database
    result = db_manager_event_log.get_event_log(user_id, event_log_id)
    if not result:
        return jsonify({"status": "error", "message": "Event log not found"}), 404
    filename, event_log_bytes = result["filename"], result["event_log"]
    # print filename to fix linter issue
    print(f"Filename: {filename}")
    event_log_bytes_io = BytesIO(event_log_bytes)

    # Send the event log to Simod API for discovery
    url = "http://simod:6001/api/start-simod-discovery"
    files = {"event_log": event_log_bytes_io}

    # if parameters are provided, add them to the files
    if "parameters" in request.files:
        parameters_file = request.files["parameters"]
        parameters_bytes_io = BytesIO(parameters_file.read())
        files["parameters"] = parameters_bytes_io

    response = requests.post(url, files=files)

    # Unpack the ZIP file
    zip_io = BytesIO(response.content)
    zip_file = zipfile.ZipFile(zip_io)
    bpmn_file = zip_file.read("simod_model.bpmn")
    json_file = zip_file.read("parameters.json")

    # Save the data in the database
    if save_boolean == "true":
        data = {"event_log_id": event_log_id, "name": name, "file_bpmn": bpmn_file, "param_json": json_file}
        scenario_id = db_manager_simod_scenario.create_simod_scenario(data)
    else:
        scenario_id = None

    if response.status_code == 200:
        # Return the ZIP file with the scenario ID in a header
        zip_io = BytesIO(response.content)
        response = send_file(zip_io, mimetype="application/zip", download_name="simod_output.zip", as_attachment=True)
        response.headers["X-Scenario-ID"] = str(scenario_id)
        response.headers["Access-Control-Expose-Headers"] = "X-Scenario-ID"
        return response, 200
    else:
        # Return error message
        try:
            error_data = response.json()
            return jsonify(error_data), 500
        except requests.RequestException:
            return (
                jsonify(
                    {"status": "error", "message": f"Simod discovery failed with status code {response.status_code}"}
                ),
                500,
            )


@simod_bp.route("/api/start-simod-simulation", methods=["GET"])
def start_simod_simulation():
    """
    Start a Simod simulation given a user id and a scenario id.

    Args:
        user_id (query): ID of the user (required).
        scenario_id (query): ID of the discovery scenario (required).
        save_boolean (query, optional): Boolean to save the simulation in the database.

    Returns:
        file: CSV file containing the simulated event log.

    Curl example:
        curl -X GET "http://localhost:8888/api/start-simod-simulation?user_id=cs_user&scenario_id=1" -o simulated_event_log.csv
        curl -X GET "http://localhost:8888/api/start-simod-simulation?user_id=cs_user&scenario_id=1&save_boolean=true" -o simulated_event_log.csv
    """
    # Get user id and scenario id from query parameters
    user_id = request.args.get("user_id")
    scenario_id = request.args.get("scenario_id")
    save_boolean = request.args.get("save_boolean")
    if not user_id or not scenario_id:
        return jsonify({"status": "error", "message": "Missing user_id or scenario_id parameters"}), 400

    # Get discovery scenario from database
    scenario_result = db_manager_simod_scenario.get_simod_scenario(scenario_id)

    # Check if scenario_result is a tuple (error case) or dictionary (success case)
    if isinstance(scenario_result, tuple):
        return jsonify(scenario_result[0]), scenario_result[1]

    # Convert to BytesIO objects for sending to the API
    bpmn_io = BytesIO(scenario_result["file_bpmn"])
    json_io = BytesIO(scenario_result["param_json"])

    # Send the files to Simod API for simulation
    url = "http://simod:6001/api/start-simod-simulation"
    files = {"discovery_output": bpmn_io, "parameters": json_io}

    try:
        response = requests.post(url, files=files)

        if save_boolean == "true":
            filename = "simulated_event_log_.csv"
            db_manager_simod_output.upload_simod_output(scenario_id, filename, response.content)

        if response.status_code == 200:
            # Return the CSV file
            csv_io = BytesIO(response.content)
            return (
                send_file(csv_io, mimetype="text/csv", download_name="simulated_event_log.csv", as_attachment=True),
                200,
            )
        else:
            # Return error message
            try:
                error_data = response.json()
                return jsonify(error_data), 500
            except Exception as e:
                print(f"Error: {e}")
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Simod simulation failed with status code {response.status_code}",
                        }
                    ),
                    500,
                )
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Error connecting to Simod API: {str(e)}"}), 500
