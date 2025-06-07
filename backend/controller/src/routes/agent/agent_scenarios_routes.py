"""
This file contains the endpoints related to AgentSimulator scenarios.

The endpoints are:
- /storage/upload-agent-scenario: Uploads an AgentSimulator scenario to the database.
- /storage/list-agent-scenarios: Lists all AgentSimulator scenarios for a given user and optional event log ID.
- /storage/get-agent-scenario: Retrieves an AgentSimulator scenario by its ID.
- /storage/update-agent-scenario: Updates an AgentSimulator scenarios name or parameters.
- /storage/delete-agent-scenario: Deletes an AgentSimulator scenario by its ID.

Example curl commands:
- Upload:
    curl -v -X POST http://localhost:8888/storage/upload-agent-scenario \
      -F event_log_id=1 \
      -F name=test_scenario \
      -F model_pkl=@agent_test_model.pkl \
      -F param_json=@agent_test_params.json \
      -F visualization_json=@agent_test_visualization.json
- List:
    curl -X GET "http://localhost:8888/storage/list-agent-scenarios?user_id=cs_user"
    OR
    curl -X GET "http://localhost:8888/storage/list-agent-scenarios?user_id=cs_user&event_log_id=1"
- Download:
    curl -v -X GET "http://localhost:8888/storage/get-agent-scenario?id=1" \
      -o scenario.zip
- Update:
    curl -X PUT http://localhost:8888/storage/update-agent-scenario \
      -F id=1 \
      -F name=new_name \
      -F param_json=@new_params.json
- Delete:
    curl -X DELETE "http://localhost:8888/storage/delete-agent-scenario?id=1"
"""

import zipfile
from io import BytesIO

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_agent_scenarios import DBManagerAgentScenarios

db_manager = DBManagerAgentScenarios()
agent_scenarios_bp = Blueprint("agent_scenarios", __name__)


@agent_scenarios_bp.route("/storage/upload-agent-scenario", methods=["POST"])
def upload_agent_scenario_api():
    """
    Upload an AgentSimulator scenario to the database.

    Args:
        event_log_id (form int): The ID of the event log to associate with this scenario (required).
        name (form str): The user-defined name for the scenario (required).
        model_pkl (form file): A .pkl file containing the agent model (required).
        param_json (form file): A .json file containing the scenario parameters (required).
        visualization_json (form file): A .json file containing visualization data (required).

    Returns:
        JSON (201): {"status": "success", "message": "Scenario uploaded successfully.", "scenario_id": int}
        JSON (400): {"status": "error", "message": str}
        JSON (500): {"status": "error", "message": str}

    Curl example:
        curl -v -X POST http://localhost:8888/storage/upload-agent-scenario \
          -F event_log_id=1 \
          -F name=test_scenario \
          -F model_pkl=@modelagent.pkl \
          -F param_json=@paramsagent.json \
          -F visualization_json=@visualization.json
    """
    event_log_id = request.form.get("event_log_id", type=int)
    if event_log_id is None:
        return (
            jsonify({"status": "error", "message": "event_log_id is required and must be a valid integer."}),
            400,
        )

    name = request.form.get("name")
    if not name:
        return jsonify({"status": "error", "message": "name is required."}), 400

    if "model_pkl" not in request.files:
        return (
            jsonify({"status": "error", "message": "no pkl file uploaded"}),
            400,
        )
    model_pkl = request.files["model_pkl"]
    model_filename = model_pkl.filename
    if not model_filename.lower().endswith(".pkl"):
        return jsonify({"status": "error", "message": "the file does not end with .pkl"}), 400

    if "param_json" not in request.files:
        return (
            jsonify({"status": "error", "message": "no param json file uploaded"}),
            400,
        )
    param_json = request.files["param_json"]
    param_filename = param_json.filename
    if not param_filename.lower().endswith(".json"):
        return jsonify({"status": "error", "message": "the file does not end with .json"}), 400

    if "visualization_json" not in request.files:
        return (
            jsonify({"status": "error", "message": "no visualization json file uploaded"}),
            400,
        )
    visualization_json = request.files["visualization_json"]
    visualization_filename = visualization_json.filename
    if not visualization_filename.lower().endswith(".json"):
        return jsonify({"status": "error", "message": "the file does not end with .json"}), 400

    try:
        model_pkl.seek(0)
        model_content = model_pkl.read()
        param_json.seek(0)
        param_content = param_json.read()
        visualization_json.seek(0)
        visualization_content = visualization_json.read()

        data = {
            "event_log_id": event_log_id,
            "name": name,
            "model_pkl": model_content,
            "param_json": param_content,
            "visualization_json": visualization_content,
        }
        scenario_id = db_manager.upload_agent_scenario(data)
    except Exception as e:
        return jsonify({"status": "error", "message": f"an error occured uploading the scenario: {str(e)}"}), 500

    return (
        jsonify(
            {
                "status": "success",
                "message": "Scenario uploaded successfully.",
                "scenario_id": scenario_id,
            }
        ),
        201,
    )


@agent_scenarios_bp.route("/storage/list-agent-scenarios", methods=["GET"])
def list_agent_scenarios_api():
    """
    Lists all AgentSimulator scenarios for a given user ID, optionally filtered by event log ID.

    Args:
        user_id (query str): The ID of the user (required).
        event_log_id (query int, optional): The ID of the event log.

    Returns:
        JSON response (200): A list of scenarios:
            [
                {"id": 1, "event_log_id": 1, "name": "Scenario 1"},
                ...
            ]
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X GET "http://localhost:8888/storage/list-agent-scenarios?user_id=1"
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required."}), 400

    event_log_id = request.args.get("event_log_id", type=int)

    try:
        scenarios = db_manager.list_agent_scenarios(user_id, event_log_id)
        if scenarios is None:
            return "", 204
    except Exception as e:
        return (
            jsonify({"status": "error", "message": str(e)}),
            500,
        )

    return jsonify(scenarios), 200


@agent_scenarios_bp.route("/storage/get-agent-scenario", methods=["GET"])
def get_agent_scenario_api():
    """
    Retrieve an AgentSimulator scenario by its ID and return it as a ZIP download.

    Args:
        id (query int): The ID of the scenario to retrieve (required).

    Returns:
        File response (200): A ZIP archive ('application/zip') containing:
            - model.pkl: Agent model pkl
            - param.json: Scenario parameters
            - visualization.json: Visualization data
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -v -X GET "http://localhost:8888/storage/get-agent-scenario?id=1" -o scenario.zip
    """
    scenario_id = request.args.get("id", type=int)
    if scenario_id is None:
        return (
            jsonify({"status": "error", "message": "id is required and must be a valid integer."}),
            400,
        )

    scenario = db_manager.get_agent_scenario(scenario_id)
    if scenario is None:
        return "", 204

    name, model_pkl, param_json, visualization_json = (
        scenario["name"],
        scenario["model_pkl"],
        scenario["param_json"],
        scenario["visualization_json"],
    )

    if name is None or model_pkl is None or param_json is None or visualization_json is None:
        return jsonify({"status": "error", "message": "invalid scenario data format"}), 500

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if not isinstance(model_pkl, BytesIO):
            model_pkl = BytesIO(model_pkl)

        if not isinstance(param_json, BytesIO):
            param_json = BytesIO(param_json)

        if not isinstance(visualization_json, BytesIO):
            visualization_json = BytesIO(visualization_json)

        zip_file.writestr("model.pkl", model_pkl.getvalue())
        zip_file.writestr("param.json", param_json.getvalue())
        zip_file.writestr("visualization.json", visualization_json.getvalue())

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{name}.zip",
    )


@agent_scenarios_bp.route("/storage/update-agent-scenario", methods=["PUT"])
def update_agent_scenario_api():
    """
    Update an AgentSimulator scenario by its ID, and optionally its param_json file and/or name.

    Args:
        id (form int): The ID of the scenario to update (required).
        name (form str, optional): A new name for the scenario.
        param_json (form file, optional): A .json file with new parameters.

    Returns:
        JSON response (200): {"status": "success", "message": "Scenario updated successfully.", "scenario_id": int}
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X PUT "http://localhost:8888/storage/update-agent-scenario" \
             -F "id=1" \
             -F "name=new_name" \
             -F "param_json=@new_params.json"
    """
    scenario_id = request.form.get("id", type=int)
    if scenario_id is None:
        return jsonify({"status": "error", "message": "id is required and must be an integer."}), 400

    name = request.form.get("name")
    param_json = request.files.get("param_json")

    if not name and not param_json:
        return jsonify({"status": "error", "message": "At least one of name or param_json must be provided"}), 400

    param_json_content = None
    if param_json:
        filename = param_json.filename
        if not filename.lower().endswith(".json"):
            return jsonify({"status": "error", "message": "invalid json file, does not end with .json"}), 400
        param_json.seek(0)
        param_json_content = param_json.read()

    try:
        result = db_manager.update_agent_scenario(scenario_id, name, param_json_content)
        if isinstance(result, tuple) and isinstance(result[0], dict) and result[0].get("status") == "error":
            return jsonify({"status": "error", "message": result[0]["message"]}), result[1]
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occured updating the scenario: {str(e)}"}), 500

    return (
        jsonify(
            {
                "status": "success",
                "message": "Scenario updated successfully.",
                "scenario_id": result,
            }
        ),
        200,
    )


@agent_scenarios_bp.route("/storage/delete-agent-scenario", methods=["DELETE"])
def delete_agent_scenario_api():
    """
    Delete an AgentSimulator scenario from the database by its ID.

    Args:
        id (query int): The ID of the scenario to delete (required).

    Returns:
        JSON response (200): {"status": "success", "message": "Agent scenario deleted successfully."}
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X DELETE "http://localhost:8888/storage/delete-agent-scenario?id=1"
    """
    scenario_id = request.args.get("id", type=int)
    if scenario_id is None:
        return jsonify({"status": "error", "message": "id is required and must be an integer."}), 400

    result = db_manager.delete_agent_scenario(scenario_id)

    if result["status"] == "error":
        code = 404 if result["message"] == "Scenario not found" else 500
        return jsonify(result), code

    return jsonify(result), 200
