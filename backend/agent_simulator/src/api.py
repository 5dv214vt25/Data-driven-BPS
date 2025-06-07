import io
import json
import os
import pickle
import tempfile
import warnings
import zipfile
from io import BytesIO

import agent_simulator_manager
from flask import Flask
from flask import jsonify
from flask import request
from flask import send_file
from simulation_config import SimulationConfig
from source.discovery_to_json import agent_to_json

"""
This script is the main entry point for the agent simulator, responsible for starting the Flask
application and defining the API endpoints between the Agent Simulator API and Controller.
"""

warnings.filterwarnings("ignore")
app = Flask(__name__)


@app.route("/api/start-agent-discovery", methods=["POST"])
def start_agent_discovery_api():
    """
    Endpoint to start the agent discovery process, it takes in an event log and returns discovery data in a zip file

    Args:
        event_log (form): CSV file containing the event log
        parameters (form): json file with the discovery input parameters
            {
                "log_path": temp_file_path,
                "train_path": None,
                "test_path": None,
                "case_id": "case_id",
                "activity_name": "activity",
                "resource_name": "resource",
                "end_timestamp": "end_time",
                "start_timestamp": "start_time",
                "extr_delays": False,
                "central_orchestration": False,
                "determine_automatically": False,
                "num_simulations": 1,
            }

    Returns:
        zip: zip file contaning     model.pkl file to be used for the simulation
                                    params.json contaning the simulation parameters
                                    visualization.json contaning the visualizasion data

        HTTP status code            200 successful run
                                    400 error with input parameters
                                    500 error with discovery

    Curl example:
        curl -X POST http://127.0.0.1:6002/api/start-agent-discovery -F "event_log=@LoanApp.csv" -F "parameters=@params.json" --output received.zip
    """

    if "event_log" not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400

    uploaded_file = request.files["event_log"]

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "uploaded_file.csv")
        uploaded_file.save(temp_file_path)

        args = agent_simulator_manager.parse_discovery_parameters(request, temp_file_path)

        # TODO: This needs to be done another way than this below.
        # None of central_orc or determine_auto is supported with
        # the current vizualisation and therefore the program crahshes
        # if the simulation is ran without vizualisation the program works as intended.
        # This is because elizabeth's code does not support the differnet settings
        # Change this in the future, (re-do the vizu code) or implement new way of
        # imputing neccesary values when these settings are used

        args["central_orchestration"] = False
        args["determine_automatically"] = False

        try:
            sim_config = SimulationConfig()

            # Start Discovery
            visualization_data, params_data, pkl_data = agent_simulator_manager.start_discovery_from_api(
                sim_config, args
            )

            # Serialize JSON objects to string
            visualization_json = json.dumps(visualization_data, indent=2)
            params_json = json.dumps(params_data, indent=2)

            # Create in-memory ZIP
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, "w") as zf:
                zf.writestr("visualization.json", visualization_json)
                zf.writestr("params.json", params_json)
                zf.writestr("model.pkl", pkl_data)

            memory_file.seek(0)

            # Send ZIP file
            return send_file(
                memory_file, mimetype="application/zip", download_name="data_bundle.zip", as_attachment=True
            )

        except Exception as e:
            return jsonify({"status": "error", "message": "Simulation error: " + str(e)}), 500


@app.route("/api/update-parameters", methods=["POST"])
def update_parameters():
    """
    Changes parameters in the pkl file and returns the changed parameters in a zip file

    Args:
        pkl: pkl file to be used for simulation

        changed_parameters (form): json with parameters to change recived from start-agent-discovery/update-parameters

        Example params.json:
        "params": {
            "activity_durations": {
                "AML check": 60.0,
                "Assess loan risk": 10.0
            },"res_calendars": {
                "Agent_id": 7.0,
                "Days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
                "Schedule": [["09:00:00", "17:00:00"]]
            },
            "num_simulations": 3,
            "new_num_cases_to_simulate": 750
        }

    Returns:
        zip: zip file contaning     model.pkl file to be used for the simulation
                                    params.json contaning the simulation parameters
                                    visualization.json contaning the visualizasion data

        HTTP status code            200 successful run
                                    400 error with input parameters
                                    500 error with discovery

    Curl example:
        curl -X POST -F "simulation_config_pkl=@model.pkl" -F "changed_parameters=@params.json"  http://127.0.0.1:6002/api/update-parameters --output received2.zip
    """

    if "simulation_config_pkl" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    pkl_file = request.files["simulation_config_pkl"]

    json_file = request.files["changed_parameters"]

    if pkl_file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if not pkl_file.filename.endswith(".pkl"):
        return jsonify({"status": "error", "message": "Invalid file type"}), 400

    if json_file.filename == "" or not json_file.filename.endswith(".json"):
        return jsonify({"status": "error", "message": "Invalid JSON file"}), 400

    try:
        # Update parameters
        zipfile = agent_simulator_manager.update_parameters(pkl_file, json_file)

        # Send ZIP file
        return send_file(zipfile, mimetype="application/zip", download_name="data_bundle.zip", as_attachment=True)

    except Exception as e:
        return jsonify({"status": "error", "message": "Simulation error: " + str(e)}), 500


@app.route("/api/start-agent-simulation", methods=["POST"])
def start_agent_simulation_api():
    """
    Endpoint to start the agent simulation process, it takes a pkl file contaning the simulation data.

    Args:
        simulation_config_pkl(form): pkl file to run the simulation with

    Returns:
        zip:                        with the simulated log data on the form simulated_log_0.csv,
                                    simulated_log_1.csv ... to number of simulations.

        HTTP status code            200 successful run
                                    400 error with input parameters
                                    500 error with discovery

    Curl example:
        curl -X POST -F "simulation_config_pkl=@model.pkl" http://127.0.0.1:6002/api/start-agent-simulation --output out.zip
    """

    if "simulation_config_pkl" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    pkl_file = request.files["simulation_config_pkl"]

    if pkl_file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400

    if not pkl_file.filename.endswith(".pkl"):
        return jsonify({"status": "error", "message": "Invalid file type"}), 400

    try:

        simulation_zip = agent_simulator_manager.start_simulation_from_api(pkl_file)

        # Send ZIP file
        return send_file(
            simulation_zip, mimetype="application/zip", download_name="data_bundle.zip", as_attachment=True
        )

    except Exception as e:
        return jsonify({"status": "error", "message": "Simulation error: " + str(e)}), 500


@app.route("/api/get-pkl-as-json", methods=["POST"])
def get_pkl_as_json():
    """
    Endpoint to get the pkl file as a json object

    Args:
        pkl_file(form): pkl file to be converted to json

    Returns:
        json: json object

    Curl example:
        curl -X POST http://127.0.0.1:6002/api/get-pkl-as-json -F "pkl_file=@model.pkl" --output out.json
    """

    if "pkl_file" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    pkl_file = request.files["pkl_file"]

    if pkl_file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400

    buffer = io.BytesIO(pkl_file.read())
    sim_config: SimulationConfig = pickle.load(buffer)
    json_params_data = agent_to_json(sim_config.sim_instance)
    params_json = json.dumps(json_params_data["data"], indent=2)

    return jsonify({"status": "success", "message": params_json}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6002)
