"""
This file contains the endpoints related to analysis.

The endpoints are:
- /analyze/simod-scenario-output: Analyze a simod scenario output and return the results.
- /analyze/agent-scenario-output: Analyze a agent scenario output and return the results.

Example curl commands:
- Analyze a simod scenario output
    curl -X GET "http://localhost:8888/analyze/simod-scenario-output?user_id=skib&simod_scenario_id=1"
- Analyze a agent scenario output
    curl -X GET "http://localhost:8888/analyze/agent-scenario-output?user_id=skib&agent_scenario_id=1"
"""

import json
import os
import tempfile
import zipfile
from io import BytesIO

import pandas as pd
import requests
from flask import Blueprint
from flask import jsonify
from flask import request
from src.analyze.analyze import analyze_agent_scenario_output
from src.analyze.analyze import analyze_simod_scenario_output
from src.db_managers.db_manager_agent_output import DBManagerAgentOutput
from src.db_managers.db_manager_agent_scenarios import DBManagerAgentScenarios
from src.db_managers.db_manager_event_log import DBManagerEventLog
from src.db_managers.db_manager_simod_output import DBManagerSimodOutput
from src.db_managers.db_manager_simod_scenarios import DBManagerSimodScenario

analyze_bp = Blueprint("analyze", __name__)
db_manager_event_log = DBManagerEventLog()
db_manager_simod_scenario = DBManagerSimodScenario()
db_manager_simod_output = DBManagerSimodOutput()
db_manager_agent_scenario = DBManagerAgentScenarios()
db_manager_agent_output = DBManagerAgentOutput()


@analyze_bp.route("/analyze/simod-scenario-output", methods=["GET"])
def analyze_simod_scenario_output_endpoint():
    """
    Analyze a simod scenario output and return the results.

    Args:
        user_id (query): ID of the user
        simod_scenario_id (query): ID of the simod scenario to analyze

    Returns:
        json: Analysis results for the event log

    Curl example:
        curl -X GET "http://localhost:8888/analyze/simod-scenario-output?user_id=skib&simod_scenario_id=1"
    """
    # Get user_id and event_log_id from query parameters
    user_id = request.args.get("user_id")
    simod_scenario_id = request.args.get("simod_scenario_id")

    if not user_id or not simod_scenario_id:
        return jsonify({"status": "error", "message": "user_id and simod_scenario_id are required"}), 400

    simulated_event_log_df = get_simulated_event_log_df_from_scenario_id(user_id, simod_scenario_id)
    parameters_dict = get_parameters_dict(simod_scenario_id)

    # Analyze the event log
    try:
        json_result = analyze_simod_scenario_output(simulated_event_log_df, parameters_dict)
        # Parse the JSON string back to a dictionary for Flask's jsonify
        analysis_result = json.loads(json_result)
        return (
            jsonify({"status": "success", "simod_scenario_id": simod_scenario_id, "analysis_result": analysis_result}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error analyzing simod scenario output: {str(e)}"}), 500


@analyze_bp.route("/analyze/agent-scenario-output", methods=["GET"])
def analyze_agent_scenario_output_endpoint():
    """
    Analyze a agent scenario output and return the results.

    Args:
        user_id (query): ID of the user
        agent_scenario_id (query): ID of the agent scenario to analyze

    Returns:
        json: Analysis results for the event log

    Curl example:
        curl -X GET "http://localhost:8888/analyze/agent-scenario-output?user_id=skib&agent_scenario_id=1"
    """
    # Get user_id and event_log_id from query parameters
    user_id = request.args.get("user_id")
    agent_scenario_id = request.args.get("agent_scenario_id")

    if not user_id or not agent_scenario_id:
        return jsonify({"status": "error", "message": "user_id and agent_scenario_id are required"}), 400

    simulated_event_log_df = get_simulated_event_log_df_from_agent_scenario_id(user_id, agent_scenario_id)
    parameters_dict = get_agent_parameters_dict(agent_scenario_id)

    # Analyze the event log
    try:
        json_result = analyze_agent_scenario_output(simulated_event_log_df, parameters_dict)
        # Parse the JSON string back to a dictionary for Flask's jsonify
        analysis_result = json.loads(json_result)
        return (
            jsonify({"status": "success", "agent_scenario_id": agent_scenario_id, "analysis_result": analysis_result}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error analyzing simod scenario output: {str(e)}"}), 500


def get_simulated_event_log_df_from_agent_scenario_id(user_id, agent_scenario_id):
    """
    Get simulated event log dataframe from an agent scenario ID.
    """
    try:
        # First, get the scenario to find the event_log_id
        result = db_manager_agent_output.get_agent_output(agent_scenario_id)
        if result is None:
            return None

        filename, data = result

        # Data is already zipped
        zip_buffer = BytesIO(data)
        zip_buffer.seek(0)

        # Unzip the output data to a temporary directory
        with tempfile.TemporaryDirectory() as tmpdirname:
            with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                zip_ref.extractall(tmpdirname)
                # List all files in the temp directory
                extracted_files = [
                    os.path.join(tmpdirname, f)
                    for f in os.listdir(tmpdirname)
                    if os.path.isfile(os.path.join(tmpdirname, f))
                ]
                if not extracted_files:
                    return None
                # Find the first CSV file
                for file_path in extracted_files:
                    if file_path.endswith(".csv"):
                        return pd.read_csv(file_path)
                # If no CSV found, return None
                return None

    except Exception as e:
        print(f"Error loading event log from scenario: {str(e)}", flush=True)
        return None


def get_simulated_event_log_df_from_scenario_id(user_id, simod_scenario_id):
    """
    Get event log dataframe from a scenario ID.

    Args:
        user_id (str): ID of the user
        simod_scenario_id (str): ID of the simod scenario

    Returns:
        pandas.DataFrame: Dataframe containing event log data, or None if not found
    """
    try:
        # First, get the scenario to find the event_log_id
        result = db_manager_simod_output.get_simod_output(simod_scenario_id)
        if result is None:
            return None

        # Unpack the tuple returned by get_simod_output
        filename, output_data = result

        return pd.read_csv(BytesIO(output_data))
    except Exception as e:
        print(f"Error loading event log from scenario: {str(e)}", flush=True)
        return None


def get_agent_parameters_dict(agent_scenario_id):
    """
    Get parameters dictionary for an agent scenario.
    """

    try:
        scenario_data = db_manager_agent_scenario.get_agent_scenario(agent_scenario_id)
        if isinstance(scenario_data, tuple) or "error" in scenario_data:
            return None

        param_json = scenario_data.get("model_pkl")

        pkl_data_io = BytesIO(param_json)

        # Send request to Agent Simulator API.
        url = "http://agent_simulator:6002/api/get-pkl-as-json"
        files = {"pkl_file": pkl_data_io}
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                return json.loads(response.json()["message"])
            else:
                return None
        except Exception as e:
            print(f"Error getting parameters: {str(e)}", flush=True)
            return None

    except Exception as e:
        print(f"Error getting parameters: {str(e)}", flush=True)
        return None


def get_parameters_dict(simod_scenario_id):
    """
    Get parameters dictionary for a specific simod scenario.

    Args:
        simod_scenario_id (str): ID of the simod scenario

    Returns:
        dict: Parameters as a Python dictionary, or None if not found
    """
    try:
        scenario_data = db_manager_simod_scenario.get_simod_scenario(simod_scenario_id)
        if isinstance(scenario_data, tuple) or "error" in scenario_data:
            return None

        # Extract the parameters JSON data
        param_json = scenario_data.get("param_json")
        if not param_json:
            return None

        # Convert memoryview or buffer to bytes if needed
        if hasattr(param_json, "tobytes"):
            param_json = param_json.tobytes()
        elif not isinstance(param_json, (bytes, str)):
            param_json = bytes(param_json)

        # Convert bytes to string if necessary
        if isinstance(param_json, bytes):
            param_json_str = param_json.decode("utf-8")
        else:
            param_json_str = param_json

        # Convert the parameters to a dictionary
        param_dict = json.loads(param_json_str)

        # Return the dictionary directly
        return param_dict
    except Exception as e:
        print(f"Error loading parameters: {str(e)}", flush=True)
        return None
