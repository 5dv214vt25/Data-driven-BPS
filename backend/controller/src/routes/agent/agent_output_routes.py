"""
This file contains the endpoints related to AgentSimulators simulation output.

The endpoints are:
- /storage/upload-agent-output: Upload a new AgentSimulator simulation output CSV for a given scenario.
- /storage/list-agent-outputs: List all AgentSimulator simulation outputs for a given user id and optional scenario id.
- /storage/get-agent-output: Download a single AgentSimulator simulation output CSV by its scenario ID.
- /storage/update-agent-output: Replace the CSV for an existing AgentSimulator simulation output.
- /storage/delete-agent-output: Delete an AgentSimulation simulation output by its scenario ID.

Example curl commands:
- Upload:
    curl -v -X POST http://localhost:8888/storage/upload-agent-output \
    -F agent_scenario_id=1 \
    -F file=@event_log_example.csv
- List:
    curl -v -X GET "http://localhost:8888/storage/list-agent-outputs?user_id=cs_user&agent_scenario_id=1"
    curl -v -X GET "http://localhost:8888/storage/list-agent-outputs?user_id=cs_user"
- Download:
    curl -v -X GET "http://localhost:8888/storage/get-agent-output?agent_scenario_id=1" \
    -o output.csv
- Delete:
    curl -v -X DELETE "http://localhost:8888/storage/delete-agent-output?agent_scenario_id=1"
- Update:
    curl -v -X PUT http://localhost:8888/storage/update-agent-output \
    -F agent_scenario_id=1 \
    -F file=@event_log_example.csv
"""

from io import BytesIO

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_agent_output import DBManagerAgentOutput

db_manager = DBManagerAgentOutput()
agent_output_bp = Blueprint("agent_output", __name__)


@agent_output_bp.route("/storage/upload-agent-output", methods=["POST"])
def upload_agent_output_api():
    """
    Upload a new AgentSimulator simulation output CSV for a given scenario

    Args:
        agent_scenario_id (form int): ID of the agent scenario (required).
        file (form file): CSV file containing the simulation output (required).

    Returns:
        JSON response (201): {"status": "success", "message": str, "agent_scenario_id": int}
        JSON response (400): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X POST http://localhost:8888/storage/upload-agent-output \
            -F "agent_scenario_id=101" \
            -F "file=@LoanApp.csv"
    """
    agent_scenario_id = request.form.get("agent_scenario_id", type=int)
    if agent_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "agent_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not agent_scenario_id:
        return jsonify({"status": "error", "message": "agent_scenario_id is required."}), 400

    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400
    file = request.files["file"]

    file.seek(0)
    raw_data = file.read()
    if not raw_data:
        return jsonify({"status": "error", "message": "No data found in the file"}), 400

    try:
        created = db_manager.upload_agent_output(agent_scenario_id, file.filename, raw_data)
        if not created:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Failed to create agent output for agent_scenario_id {agent_scenario_id}.",
                    }
                ),
                500,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error storing agent output: {e}"}), 500

    return (
        jsonify(
            {
                "status": "success",
                "message": "Agent output uploaded successfully.",
                "agent_scenario_id": agent_scenario_id,
            }
        ),
        201,
    )


@agent_output_bp.route("/storage/list-agent-outputs", methods=["GET"])
def list_agent_outputs_api():
    """
    Lists all AgentSimulator outputs for a given user ID, optionally filtered by a scenario id.

    Args:
        user_id (query str): ID of the user (required).
        scenario_id (query int, optional): ID of the agent scenario.

        JSON response (200): List of output information
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X GET "http://localhost:8888/storage/list-agent-outputs?user_id=cs_user&agent_scenario_id=1"
        curl -X GET "http://localhost:8888/storage/list-agent-outputs?user_id=cs_user"
    """
    user_id = request.args.get("user_id")
    if user_id is None:
        return jsonify({"status": "error", "message": "user_id is required."}), 400

    scenario_id = request.args.get("agent_scenario_id", type=int)

    outputs = db_manager.list_agent_outputs(user_id, scenario_id)
    if outputs is None:
        return (
            jsonify({"status": "error", "message": "Database error when retrieving all agent outputs information"}),
            500,
        )

    if not outputs:
        if scenario_id:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"No outputs found for user_id: {user_id} and scenario_id: {scenario_id}",
                    }
                ),
                404,
            )
        else:
            return jsonify({"status": "error", "message": f"No outputs found for user_id: {user_id}"}), 404

    return jsonify(outputs), 200


@agent_output_bp.route("/storage/get-agent-output", methods=["GET"])
def get_agent_output_api():
    """
    Download a single AgentSimulator simulation output CSV by scenario ID.

    Args:
        agent_scenario_id (query int): ID of the agent scenario to download (required).

    Returns:
        File response (200): CSV file attachment
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}

    Curl example:
        curl -X GET "http://localhost:8888/storage/get-agent-output?agent_scenario_id=1"
        or
        curl -X GET "http://localhost:8888/storage/get-agent-output?agent_scenario_id=1" -o output.zip
    """
    agent_scenario_id = request.args.get("agent_scenario_id", type=int)
    if agent_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "agent_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not agent_scenario_id:
        return jsonify({"status": "error", "message": "agent_scenario_id is required."}), 400

    output = db_manager.get_agent_output(agent_scenario_id)
    if not output:
        return "", 204

    filename, data = output

    zip_buffer = BytesIO(data)
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name="data_bundle.zip",
        mimetype="application/zip",
    )


@agent_output_bp.route("/storage/update-agent-output", methods=["PUT"])
def update_agent_output_api():
    """
    Replace the CSV for an existing AgentSimulator simulation output.

    Args:
        agent_scenario_id (query int): ID of the agent scenario to update (required).
        file (form file): New CSV file containing the updated output (required).

    Returns:
        JSON response (200): {"status": "success", "message": str}
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X PUT "http://localhost:8888/storage/update-agent-output?agent_scenario_id=1" \
            -F "file=@LoanApp.csv"
    """
    agent_scenario_id = request.args.get("agent_scenario_id", type=int)
    if agent_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "agent_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not agent_scenario_id:
        return jsonify({"status": "error", "message": "agent_scenario_id is required."}), 400

    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400
    file = request.files["file"]

    raw_data = file.read()
    if not raw_data:
        return jsonify({"status": "error", "message": "Uploaded file is empty."}), 400

    try:
        updated_count = db_manager.update_agent_output(agent_scenario_id, file.filename, raw_data)
        if updated_count is None:
            return (
                jsonify({"status": "error", "message": "Error updating agent output: Database operation failed."}),
                500,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error updating agent output: {e}"}), 500

    if updated_count == 0:
        return (
            jsonify(
                {"status": "error", "message": f"No output found to update for agent_scenario_id {agent_scenario_id}."}
            ),
            404,
        )
    return jsonify({"status": "success", "message": "Agent output updated successfully."}), 200


@agent_output_bp.route("/storage/delete-agent-output", methods=["DELETE"])
def delete_agent_output_api():
    """
    Delete an AgentSimulation simulation output by its scenario ID.

    Args:
        agent_scenario_id (query int): ID of the agent scenario to delete (required).

    Returns:
        JSON response (200): {"status": "success", "message": "Agent output deleted successfully."}
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X DELETE "http://localhost:8888/storage/delete-agent-output?agent_scenario_id=1"
    """
    agent_scenario_id = request.args.get("agent_scenario_id", type=int)
    if agent_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "agent_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not agent_scenario_id:
        return jsonify({"status": "error", "message": "agent_scenario_id is required."}), 400

    try:
        deleted = db_manager.delete_agent_output(agent_scenario_id)
        if not deleted:
            return (
                jsonify(
                    {"status": "error", "message": f"No agent output found for agent_scenario_id {agent_scenario_id}."}
                ),
                404,
            )
        return jsonify({"status": "success", "message": "Agent output deleted successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error deleting agent output: {e}"}), 500
