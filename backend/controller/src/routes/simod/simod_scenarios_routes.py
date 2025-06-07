"""
This file contains the endpoints related to Simod scenarios.

The endpoints are:
- /storage/upload-simod-scenario: Upload a new Simod scenario to the database.
- /storage/get-simod-scenario: Get a Simod scenario from the database.
- /storage/list-simod-scenarios: List all Simod scenarios for a given user id and optional event log id.
- /storage/update-simod-scenario: Update an Simod scenario.
- /storage/delete-simod-scenario: Delete an Simod scenario.

Example curl commands:
- Upload:
    curl -X POST http://localhost:8888/storage/upload-simod-scenario -F "event_log_id=1" -F "name=scenario_test" -F "file_bpmn=@discovered_model.bpmn" -F "param_json=@fakeparam.json"
- Get:
    curl -X GET http://localhost:8888/storage/get-simod-scenario?scenario_id=1 -o result.zip
- List:
    curl -X GET "http://localhost:8888/storage/list-simod-scenarios?user_id=cs_user&event_log_id=1"
    curl -X GET "http://localhost:8888/storage/list-simod-scenarios?user_id=cs_user"
- Update:
    curl -X PUT http://localhost:8888/storage/update-simod-scenario -F "scenario_id=1" -F "name=new_name" -F "param_json=@new_params.json"
- Delete:
    curl -X DELETE http://localhost:8888/storage/delete-simod-scenario -F "scenario_id=1"
"""

import zipfile
from io import BytesIO

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_simod_scenarios import DBManagerSimodScenario

db_manager = DBManagerSimodScenario()

simod_scenarios_bp = Blueprint("simod_scenarios", __name__)


@simod_scenarios_bp.route("/storage/upload-simod-scenario", methods=["POST"])
def upload_simod_scenario():
    """
    Upload an simod_scenario to the server.

    Args:
        event_log_id (form): ID of the event log (required).
        name (form): Name of the scenario (required).
        file_bpmn (form):  file containing the bpmn diagram (required).
        param_json (form): json file containing the parameters (required).

    Returns:
        json: Status and scenario ID if successful.

    Curl example:
        curl -X POST http://localhost:8888/storage/upload-simod-scenario -F "event_log_id=1" -F "name=scenario_test" -F "file_bpmn=@discovered_model.bpmn" -F "param_json=@fakeparam.json"
    """
    # Get eventlog id
    try:
        event_log_id = request.form.get("event_log_id")
        if not event_log_id:
            return jsonify({"status": "error", "message": "event_log_id is required."}), 400
        event_log_id = int(event_log_id)  # Convert to integer
    except ValueError:
        return jsonify({"status": "error", "message": "event_log_id must be a valid integer."}), 400

    # Get name
    name = request.form.get("name")
    if not name:
        return jsonify({"status": "error", "message": "name is required."}), 400

    # Check if the bpmn is in the request
    if "file_bpmn" not in request.files:
        return jsonify({"status": "error", "error": "No bpmn file uploaded"}), 400
    file_bpmn = request.files["file_bpmn"]
    filename = file_bpmn.filename
    if not filename.lower().endswith(".bpmn"):
        return jsonify({"status": "error", "error": "No bpmn file uploaded: does not end with .bpmn"}), 400

    # Check if the parameters are in the request
    if "param_json" not in request.files:
        return jsonify({"status": "error", "error": "No param json file uploaded"}), 400
    param_json = request.files["param_json"]
    filename = param_json.filename
    if not filename.lower().endswith(".json"):
        return jsonify({"status": "error", "error": "No param json file uploaded: does not end with .json"}), 400

    # Store the event log
    try:
        file_bpmn.seek(0)
        bpmn_content = file_bpmn.read()
        param_json.seek(0)
        param_content = param_json.read()
        data = {"event_log_id": event_log_id, "name": name, "file_bpmn": bpmn_content, "param_json": param_content}
        scenario_id = db_manager.create_simod_scenario(data)
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred storing the event log: {str(e)}"}), 500

    # Return the processed events as a response
    return (
        jsonify({"status": "success", "message": "Scenario uploaded successfully.", "scenario_id": str(scenario_id)}),
        201,
    )


@simod_scenarios_bp.route("/storage/get-simod-scenario", methods=["GET"])
def get_simod_scenario():
    """
    Get a scenario from the database.

    Args:
        scenario_id (query): ID of the scenario (required).

    Returns:
        file: ZIP file containing the scenario files, bpmn and json.

    Curl example:
        curl -X GET http://localhost:8888/storage/get-simod-scenario?scenario_id=1 -o result.zip
    """
    # Get scenario id
    try:
        scenario_id = request.args.get("scenario_id", type=int)
        if not scenario_id:
            return jsonify({"status": "error", "message": "scenario_id is required."}), 400
        scenario_id = int(scenario_id)  # Convert to integer
    except ValueError:
        return jsonify({"status": "error", "message": "scenario_id must be a valid integer."}), 400

    result = db_manager.get_simod_scenario(scenario_id)
    # Check if result is a tuple (error response)
    if isinstance(result, tuple):
        return jsonify({"status": "error", "error": result[0]["error"]}), result[1]

    if result is None:
        return "", 204

    name, file_bpmn, param_json = result["name"], result["file_bpmn"], result["param_json"]

    if name is None or file_bpmn is None or param_json is None:
        return jsonify({"status": "error", "error": "Invalid scenario data format"}), 500

    # Convert files to a file object
    zip_buffer = BytesIO()

    # Create a ZIP file in memory
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Convert file_bpmn to BytesIO if not already
        if not isinstance(file_bpmn, BytesIO):
            file_bpmn = BytesIO(file_bpmn)

        # Convert param_json to BytesIO if not already
        if not isinstance(param_json, BytesIO):
            param_json = BytesIO(param_json)

        # Add file_bpmn to the ZIP (e.g., as 'model.bpmn')
        zip_file.writestr("model.bpmn", file_bpmn.getvalue())

        # Add param_json to the ZIP (e.g., as 'params.json')
        zip_file.writestr("params.json", param_json.getvalue())

    # Reset the buffer's position to the beginning
    zip_buffer.seek(0)

    return (
        send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"{name}.zip",
        ),
        200,
    )


@simod_scenarios_bp.route("/storage/list-simod-scenarios", methods=["GET"])
def list_simod_scenarios():
    """
    Retrieve the simod scenarios as a summarized list.

    Args:
        user_id (query): ID of the user (required)
        event_log_id (query, optional): ID of the event log.

    Returns:
        json: List of scenarios IDs, event log IDs, names

    Curl example:
        curl -X GET "http://localhost:8888/storage/list-simod-scenarios?user_id=cs_user&event_log_id=1"
        curl -X GET "http://localhost:8888/storage/list-simod-scenarios?user_id=cs_user"
    """
    # Get user_id (required)
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required."}), 400

    # Get event_log_id (optional)
    event_log_id = request.args.get("event_log_id")

    try:
        # Convert to integer if provided
        if event_log_id:
            event_log_id = int(event_log_id)
    except ValueError:
        return jsonify({"status": "error", "message": "event_log_id must be a valid integer."}), 400

    scenarios = db_manager.list_simod_scenarios(user_id, event_log_id)
    if not scenarios:
        return "", 204
    else:
        return jsonify(scenarios), 200


@simod_scenarios_bp.route("/storage/update-simod-scenario", methods=["PUT"])
def update_simod_scenario():
    """
    Update an existing simod_scenario on the database.

    Args:
        scenario_id (form): ID of the scenario to update (required).
        name (form, optional): New name for the scenario.
        param_json (form, optional): New JSON parameters file

    Returns:
        json: Status and scenario ID if successful

    Curl example:
        curl -X PUT http://localhost:8888/storage/update-simod-scenario -F "scenario_id=1" -F "name=new_name" -F "param_json=@new_params.json"
    """
    # Get scenario id
    try:
        scenario_id = request.form.get("scenario_id")
        if not scenario_id:
            return jsonify({"status": "error", "message": "scenario_id is required."}), 400
        scenario_id = int(scenario_id)  # Convert to integer
    except ValueError:
        return jsonify({"status": "error", "message": "scenario_id must be a valid integer."}), 400

    # Get optional parameters
    name = request.form.get("name")
    param_json_file = request.files.get("param_json")

    # Validate that at least one parameter to update was provided
    if not name and not param_json_file:
        return jsonify({"status": "error", "message": "At least one of name or param_json must be provided."}), 400

    # Read param_json content if file was provided
    param_json_content = None
    if param_json_file:
        # Validate file extension
        filename = param_json_file.filename
        if not filename.lower().endswith(".json"):
            return jsonify({"status": "error", "error": "Invalid param json file: does not end with .json"}), 400

        # Read file content
        param_json_file.seek(0)
        param_json_content = param_json_file.read()

    # Update the scenario
    try:
        result = db_manager.update_simod_scenario(scenario_id, name, param_json_content)
        if isinstance(result, tuple) and isinstance(result[0], dict) and "error" in result[0]:
            return jsonify({"status": "error", "message": result[0]["error"]}), result[1]
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred updating the scenario: {str(e)}"}), 500

    # Return the processed events as a response
    return (
        jsonify({"status": "success", "message": "Scenario updated successfully.", "scenario_id": result}),
        200,
    )


@simod_scenarios_bp.route("/storage/delete-simod-scenario", methods=["DELETE"])
def delete_simod_scenario():
    """
    Deletes an existing simod scenario on the database.

    Args:
        scenario_id (form): ID of the scenario to delete (required).

    Returns:
        json: Status

    Curl example:
        curl -X DELETE http://localhost:8888/storage/delete-simod-scenario -F "scenario_id=1"
    """
    # Get scenario id
    try:
        scenario_id = request.form.get("scenario_id")
        if not scenario_id:
            return jsonify({"status": "error", "message": "scenario_id is required."}), 400
        scenario_id = int(scenario_id)  # Convert to integer
    except ValueError:
        return jsonify({"status": "error", "message": "scenario_id must be a valid integer."}), 400

    # Delete the scenario
    try:
        db_manager.delete_simod_scenario(scenario_id)
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred deleting the scenario: {str(e)}"}), 500

    return jsonify({"status": "success", "message": "Scenario deleted successfully"}), 204
