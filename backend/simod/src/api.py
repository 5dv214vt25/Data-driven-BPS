"""
This script is the main entry point for the simod, responsible for starting the Flask
application and defining the API endpoints between Simod API and Controller.

The API provides endpoints for:
- Testing the API connection
- Starting process discovery from event logs
- Running simulations using discovered models
"""

import json
import zipfile
from io import BytesIO
from pathlib import Path

from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
from sandler import Sandler

from simod.event_log.event_log import EventLog
from simod.settings.simod_settings import SimodSettings
from simod.simod import Simod

app = Flask(__name__)


@app.route("/api/get-test-message-from-simod-api", methods=["GET"])
def get_test_message_simod_api():
    """
    Demo request to get a test message from the Simod API.

    Args:
        None

    Returns:
        Dict[str, str]: A JSON object with a message

    Curl example:
        curl http://localhost:6001/api/get-test-message-from-simod-api
    """
    return jsonify({"message": "Hello World From Simod API!"})


@app.route("/api/start-simod-discovery", methods=["POST"])
def start_simod_discovery():
    """
    Start a Simod discovery.

    Args:
        Event log file (required): CSV file containing the event log
        Parameters file (optional): JSON file with modifiable settings

    Returns:
        Response: A ZIP file containing:
            - simod_model.bpmn: The discovered process model
            - parameters.json: The discovered parameters

    Curl example:
        curl -X POST http://localhost:6001/api/start-simod-discovery \
             -F "event_log=@event_log.csv" \
             -o simod_output.zip

        curl -X POST http://localhost:6001/api/start-simod-discovery \
             -F "event_log=@event_log.csv" \
             -F "parameters=@params.json" \
             -o simod_output.zip
    """
    event_log_file = request.files["event_log"]

    # Convert filestorage from requests into BytesIO object
    event_log_file.stream.seek(0)  # rewind
    event_log_buffer = BytesIO(event_log_file.read())

    # Handle optional parameters file
    modifiable_settings = None
    if "parameters" in request.files:
        parameters_file = request.files["parameters"]
        parameters_file.stream.seek(0)  # rewind
        try:
            parameters_content = parameters_file.read().decode("utf-8")
            modifiable_settings = json.loads(parameters_content)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return jsonify({"status": "error", "message": f"Invalid parameters file: {str(e)}"}), 400

    sandler = Sandler()
    try:
        bpmn_io, json_io = sandler.discover(event_log_buffer, modifiable_settings)  # Pass parameters
    except Exception as e:
        return jsonify({"status": "error", "message": f"Discovery failed: {str(e)}"}), 500
    # Create a ZIP archive in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("simod_model.bpmn", bpmn_io.getvalue())
        zip_file.writestr("parameters.json", json_io.getvalue())

    zip_buffer.seek(0)

    # Create a Flask Response with the Zip content
    return Response(
        zip_buffer, mimetype="application/zip", headers={"Content-Disposition": "attachment; filename=simod_output.zip"}
    )


@app.route("/api/start-simod-simulation", methods=["POST"])
def start_simod_simulation():
    """
    Start a Simod simulation given a discovery output, eg. bpmn and json.

    Args:
        Bpmn file (required): Bpmn file, output from discovery
        Parameters file (required): JSON file with parameters, output from discovery

    Returns:
        Response: A CSV file containing the simulated event log

    Curl example:
        curl -X POST http://localhost:6001/api/start-simod-simulation \
            -F "discovery_output=@bpmn.bpmn" \
            -F "parameters=@json.json" \
            -o simulated_event_log.csv
    """

    discovery_output_file = request.files["discovery_output"]
    parameters_file = request.files["parameters"]

    # Convert filestorages from requests into BytesIO objects
    discovery_output_file.stream.seek(0)
    discovery_output_buffer = BytesIO(discovery_output_file.read())

    parameters_file.stream.seek(0)
    parameters_buffer = BytesIO(parameters_file.read())

    sandler = Sandler()
    csv_io = sandler.simulate(
        discovery_output_buffer, parameters_buffer
    )  # Returns a BytesIO object containing CSV data
    # Create a Flask Response with the BytesIO content
    return Response(
        csv_io, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=simulated_event_log.csv"}
    )


def main():
    """
    Main function to test the Simod application with default settings.

    This function:
    1. Initializes the output directory
    2. Loads default settings
    3. Reads and preprocesses the event log
    4. Runs the Simod discovery process

    The function uses a simplified loan application event log for testing.
    The output will be stored in the 'simod_src/outputs' directory.
    """

    # Initialize 'output' folder and read configuration file
    output = Path("simod_src/outputs")

    settings = SimodSettings.default()
    settings.common.train_log_path = Path("simod_src/resources/event_logs/LoanApp_simplified_train.csv.gz")
    settings.common.perform_final_evaluation = False

    # Read and preprocess event log
    event_log = EventLog.from_path(
        log_ids=settings.common.log_ids,
        train_log_path=settings.common.train_log_path,
        test_log_path=settings.common.test_log_path,
        preprocessing_settings=settings.preprocessing,
        need_test_partition=settings.common.perform_final_evaluation,
    )

    # Instantiate and run SIMOD
    simod = Simod(settings=settings, event_log=event_log, output_dir=output)
    simod.run()

    # Optionally start the Flask app
    # app.run(host="0.0.0.0", port=6001, debug=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6001)
