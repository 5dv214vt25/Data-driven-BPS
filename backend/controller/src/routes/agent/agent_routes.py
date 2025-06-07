"""
This file contains the endpoints for the AgentSimulator API.

The endpoints are:
- /api/start-agent-discovery
- /api/start-agent-simulation
- /api/update-agent-parameters

Example curl commands:
- Start agent discovery
    curl -X POST "http://localhost:8888/api/start-agent-discovery?user_id=cs_user&event_log_id=1&save_boolean=true&name=name_scenario" \
    -F "parameters=@params.json" \
    -o agent_output.zip
- Start agent simulation
    curl -X GET "http://localhost:8888/api/start-agent-simulation?user_id=cs_user&scenario_id=1" -o simulated_event_logs.zip
    curl -X GET "http://localhost:8888/api/start-agent-simulation?user_id=cs_user&scenario_id=1&save_boolean=true" -o simulated_event_logs.zip
- Update agent parameters
    curl -X POST "http://localhost:8888/api/update-agent-parameters?user_id=cs_user&scenario_id=1&name=name_updated" \
    -F "changed_parameters=@fakeparam.json" \
    -D headers_cs_user.txt \
    -o updated_scenario.zip
"""

import zipfile
from io import BytesIO

import requests
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_agent_output import DBManagerAgentOutput
from src.db_managers.db_manager_agent_scenarios import DBManagerAgentScenarios
from src.db_managers.db_manager_event_log import DBManagerEventLog

db_manager = DBManagerEventLog()
db_manager_agent_scenario = DBManagerAgentScenarios()
db_manager_agent_output = DBManagerAgentOutput()

agent_bp = Blueprint("agent", __name__)


@agent_bp.route("/api/start-agent-discovery", methods=["POST"])
def start_agent_discovery():
    """
    Start an Agent discovery given an event log id.

    Args:
        user_id (query): ID of the user (required).
        event_log_id (query): ID of the event log (required).
        save_boolean (query, optional): Boolean to save the discovery scenario in the database.
        name (query, optional): Name of the discovery scenario to save in the database.
        parameters (form, optional): JSON with the discovery input parameters.

    Returns:
        file: ZIP file containing the discovered process model, the pkl file to be used for simulation,
        params.json containing the simulation parameters and visualization.json containing the visualization data.

        header: X-Scenario-ID containing the id of the saved discovery scenario.

    Curl example:
        curl -X POST "http://localhost:8888/api/start-agent-discovery?user_id=cs_user&event_log_id=1&save_boolean=true&name=name_scenario" \
        -F "parameters=@params.json" \
        -o agent_output.zip
        curl -X POST "http://localhost:8888/api/start-agent-discovery?user_id=cs_user&event_log_id=1" \
        -F "parameters=@params.json" \
        -o agent_output.zip
    """
    # Get query parameters
    user_id = request.args.get("user_id")
    event_log_id = request.args.get("event_log_id")
    name = request.args.get("name")
    save_boolean = request.args.get("save_boolean")

    if not user_id or not event_log_id:
        return jsonify({"status": "error", "message": "Missing user_id or event_log_id parameters"}), 400

    # Get event log file from database
    result = db_manager.get_event_log(user_id, event_log_id)

    if not result:
        return jsonify({"status": "error", "message": "Event log not found"}), 404

    filename, file_like = result["filename"], result["event_log"]
    # print filename to fix linter issue
    print(f"Filename: {filename}")
    event_log_bytes_io = BytesIO(file_like)

    # Send the event log to Agent API for discovery
    url = "http://agent_simulator:6002/api/start-agent-discovery"
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
    visualization_json = zip_file.read("visualization.json")
    params_json = zip_file.read("params.json")
    model_pkl = zip_file.read("model.pkl")

    # Save the data in the database
    if save_boolean == "true":
        data = {
            "event_log_id": event_log_id,
            "name": name,
            "param_json": params_json,
            "model_pkl": model_pkl,
            "visualization_json": visualization_json,
        }
        scenario_id = db_manager_agent_scenario.upload_agent_scenario(data)
    else:
        scenario_id = None

    if response.status_code == 200:
        zip_io = BytesIO(response.content)
        response = send_file(zip_io, mimetype="application/zip", download_name="agent_output.zip", as_attachment=True)
        response.headers["X-Scenario-ID"] = str(scenario_id)
        response.headers["Access-Control-Expose-Headers"] = "X-Scenario-ID"
        return response
    else:
        # Return error message
        try:
            error_data = response.json()
            return jsonify(error_data)
        except requests.RequestException:
            return (
                jsonify(
                    {"status": "error", "message": f"Agent discovery failed with status code {response.status_code}"}
                ),
                500,
            )


@agent_bp.route("/api/start-agent-simulation", methods=["GET"])
def start_agent_simulation():
    """
    Start an Agent simulation given a user id and a scenario id and an optional save boolean.

    Args:
        user_id (query): ID of the user (required).
        scenario_id (query): ID of the discovery scenario (required).
        save_boolean (query, optional): Boolean to save the simulation in the database.

    Returns:
        file: ZIP file containing all the simulated event logs, the number of simulated event logs
            depends on parameters set by the user.

    Curl example:
        curl -X GET "http://localhost:8888/api/start-agent-simulation?user_id=cs_user&scenario_id=1" -o simulated_event_logs.zip
        curl -X GET "http://localhost:8888/api/start-agent-simulation?user_id=cs_user&scenario_id=1&save_boolean=true" -o simulated_event_logs.zip
    """
    # Get user id and scenario id from query parameters
    user_id = request.args.get("user_id")
    scenario_id = request.args.get("scenario_id")
    save_boolean = request.args.get("save_boolean")
    if not user_id or not scenario_id:
        return jsonify({"status": "error", "message": "Missing user_id or scenario_id parameters"}), 400

    # Get discovery scenario from database
    scenario_result = db_manager_agent_scenario.get_agent_scenario(scenario_id)
    if not scenario_result:
        return jsonify({"status": "error", "message": "Scenario not found"}), 404

    # Convert to BytesIO objects for sending to the API
    pkl_data_io = BytesIO(scenario_result["model_pkl"])

    # Send request to Agent Simulator API for simulation
    url = "http://agent_simulator:6002/api/start-agent-simulation"
    files = {"simulation_config_pkl": ("simulation_config.pkl", pkl_data_io, "application/octet-stream")}
    try:
        response = requests.post(url, files=files)

        if save_boolean == "true":
            filename = "simulated_event_logs.zip"
            db_manager_agent_output.upload_agent_output(scenario_id, filename, response.content)

        if response.status_code == 200:
            # Return the ZIP file
            zip_io = BytesIO(response.content)
            return send_file(
                zip_io, mimetype="application/zip", download_name="simulated_event_logs.zip", as_attachment=True
            )
        else:
            # Return error message
            try:
                error_data = response.json()
                return jsonify(error_data)
            except Exception as e:
                print(f"Error: {e}")
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Agent simulation failed with status code {response.status_code}",
                        }
                    ),
                    500,
                )
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Error connecting to Agent API: {str(e)}"}), 502


@agent_bp.route("/api/update-agent-parameters", methods=["POST"])
def update_agent_parameters():
    """
    Fetch an existing scenarios model.pkl from the DB, apply parameter changes via
    the simulation api, save the new scenario, and return the updated ZIP.

    Args:
        user_id (str): ID of the user (required).
        scenario_id (int): ID of the scenario to update (required).
        name (str, optional): New name for the scenario.

    Form-data:
        changed_parameters (form file): JSON with the parameter changes (required).

    Returns:
        ZIP file (model.pkl, params.json, visualization.json) +
        X-Scenario-ID header with the new scenarios ID.

    Curl example:
        curl -X POST "http://localhost:8888/api/update-agent-parameters?user_id=cs_user&scenario_id=1&name=name_updated" \
        -F "changed_parameters=@fakeparam.json" \
        -D headers_cs_user.txt \
        -o updated_scenario.zip
    """
    user_id = request.args.get("user_id")
    scenario_id = request.args.get("scenario_id")
    new_name = request.args.get("name")

    if not user_id or not scenario_id:
        return jsonify({"status": "error", "message": "Missing user_id or scenario_id"}), 400
    if "changed_parameters" not in request.files:
        return jsonify({"status": "error", "message": "Missing changed_parameters (.json)"}), 400

    json_file = request.files["changed_parameters"]
    if not json_file.filename.endswith(".json"):
        return jsonify({"status": "error", "message": "Invalid JSON file"}), 400

    original = db_manager_agent_scenario.get_agent_scenario(scenario_id)
    if not original:
        return jsonify({"status": "error", "message": "Scenario not found"}), 404

    model_bytes = original["model_pkl"]
    pkl_io = BytesIO(model_bytes)

    pkl_tuple = ("model.pkl", pkl_io, "application/octet-stream")
    json_tuple = (json_file.filename, json_file.stream, "application/json")

    try:
        response = requests.post(
            "http://agent_simulator:6002/api/update-parameters",
            files={"simulation_config_pkl": pkl_tuple, "changed_parameters": json_tuple},
        )
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Could not connect to AgentSimulator: {e}"}), 502

    if response.status_code != 200:
        try:
            return jsonify(response.json()), response.status_code
        except ValueError:
            return (
                jsonify({"status": "error", "message": f"AgentSimulator error {response.status_code}"}),
                response.status_code,
            )

    bundle_io = BytesIO(response.content)
    zf = zipfile.ZipFile(bundle_io)
    new_params = zf.read("params.json")
    new_model_pkl = zf.read("model.pkl")
    new_visualization = zf.read("visualization.json")

    save_data = {
        "event_log_id": original["event_log_id"],
        "name": new_name or original.get("name", ""),
        "param_json": new_params,
        "model_pkl": new_model_pkl,
        "visualization_json": new_visualization,
    }
    new_scenario_id = db_manager_agent_scenario.upload_agent_scenario(save_data)

    bundle_io.seek(0)
    out = send_file(bundle_io, mimetype="application/zip", download_name="updated_scenario.zip", as_attachment=True)
    out.headers["X-Scenario-ID"] = str(new_scenario_id)
    out.headers["Access-Control-Expose-Headers"] = "X-Scenario-ID"
    return out
