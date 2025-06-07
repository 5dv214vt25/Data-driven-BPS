"""
This file contains the endpoints related to Simod simulation output.

The endpoints are:
- /storage/upload-simod-output: Upload a new Simod simulation output CSV for a given scenario.
- /storage/list-simod-outputs: List all Simod simulation outputs for a given user, optionally filtered by scenario ID.
- /storage/get-simod-output: Download a single Simod simulation output CSV by scenario ID.
- /storage/delete-simod-output: Delete an Simod simulation output by its scenario ID.
- /storage/update-simod-output: Replace the CSV for an existing Simod simulation output.

Example curl commands:
- Upload:
    curl -X POST http://localhost:8888/storage/upload-simod-output \
    -F "simod_scenario_id=1" \
    -F "file=@LoanApp.csv"
- List:
    curl -X GET "http://localhost:8888/storage/list-simod-outputs?user_id=cs_user&scenario_id=1"
    curl -X GET "http://localhost:8888/storage/list-simod-outputs?user_id=cs_user"
- Download:
    curl -X GET "http://localhost:8888/storage/get-simod-output?simod_scenario_id=1" -o output.csv
- Delete:
    curl -X DELETE "http://localhost:8888/storage/delete-simod-output?simod_scenario_id=1"
- Update:
    curl -X PUT "http://localhost:8888/storage/update-simod-output?simod_scenario_id=1" \
    -F "file=@LoanApp.csv"
"""

from io import BytesIO

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_simod_output import DBManagerSimodOutput

db_manager = DBManagerSimodOutput()
simod_output_bp = Blueprint("simod_output", __name__)


@simod_output_bp.route("/storage/upload-simod-output", methods=["POST"])
def upload_simod_output_api():
    """
    Upload a new SimodSimulator simulation output CSV for a given scenario

    Args:
        simod_scenario_id (form int): ID of the simod scenario (required).
        file (form file): CSV file containing the simulation output (required).

    Returns:
        JSON response (201): {"status": "success", "message": str, "simod_scenario_id": int}
        JSON response (400): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X POST http://localhost:8888/storage/upload-simod-output \
            -F "simod_scenario_id=1" \
            -F "file=@LoanApp.csv"
    """
    simod_scenario_id = request.form.get("simod_scenario_id", type=int)
    if simod_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "simod_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not simod_scenario_id:
        return jsonify({"status": "error", "message": "simod_scenario_id is required."}), 400

    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400
    file = request.files["file"]

    file.seek(0)
    raw_data = file.read()
    if not raw_data:
        return jsonify({"status": "error", "message": "No data found in the file"}), 400

    try:
        created = db_manager.upload_simod_output(simod_scenario_id, file.filename, raw_data)
        if not created:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Failed to create simod output for simod_scenario_id {simod_scenario_id}.",
                    }
                ),
                500,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error storing simod output: {e}"}), 500

    return (
        jsonify(
            {
                "status": "success",
                "message": "simod output uploaded successfully.",
                "simod_scenario_id": simod_scenario_id,
            }
        ),
        201,
    )


@simod_output_bp.route("/storage/list-simod-outputs", methods=["GET"])
def list_simod_outputs_api():
    """
    List all Simod simulation outputs for a given user, optionally filtered by scenario ID.

    Args:
        user_id (query str): ID of the user (required).
        scenario_id (query int, optional): ID of the scenario.

    Returns:
        JSON response (200): List of output information
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X GET "http://localhost:8888/storage/list-simod-outputs?user_id=cs_user&scenario_id=1"
        curl -X GET "http://localhost:8888/storage/list-simod-outputs?user_id=cs_user"
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required."}), 400

    # Get scenario_id (optional)
    scenario_id = request.args.get("scenario_id")

    try:
        # Convert to integer if provided
        if scenario_id:
            scenario_id = int(scenario_id)
    except ValueError:
        return jsonify({"status": "error", "message": "scenario_id must be a valid integer."}), 400

    outputs = db_manager.list_simod_outputs(user_id, scenario_id)
    if outputs is None:
        return (
            jsonify({"status": "error", "message": "Database error when retrieving simod outputs information"}),
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


@simod_output_bp.route("/storage/get-simod-output", methods=["GET"])
def get_simod_output_api():
    """
    Download a single Simod simulation output CSV by scenario ID.

    Args:
        simod_scenario_id (query int): ID of the simod scenario to download (required).

    Returns:
        File response (200): CSV file attachment
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X GET "http://localhost:8888/storage/get-simod-output?simod_scenario_id=1"
        or
        curl -X GET "http://localhost:8888/storage/get-simod-output?simod_scenario_id=1" -o output.csv
    """
    simod_scenario_id = request.args.get("simod_scenario_id", type=int)
    if simod_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "simod_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not simod_scenario_id:
        return jsonify({"status": "error", "message": "simod_scenario_id is required."}), 400

    output = db_manager.get_simod_output(simod_scenario_id)
    if not output:
        return "", 204

    filename, data = output

    buffer = BytesIO(data)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename if filename.endswith(".csv") else f"{filename}.csv",
        mimetype="text/csv",
    )


@simod_output_bp.route("/storage/delete-simod-output", methods=["DELETE"])
def delete_simod_output_api():
    """
    Delete an Simod simulation output by its scenario ID.

    Args:
        simod_scenario_id (query int): ID of the simod scenario to delete (required).

    Returns:
        JSON response (204): No content
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X DELETE "http://localhost:8888/storage/delete-simod-output?simod_scenario_id=1"
    """
    simod_scenario_id = request.args.get("simod_scenario_id", type=int)
    if simod_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "simod_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not simod_scenario_id:
        return jsonify({"status": "error", "message": "simod_scenario_id is required."}), 400

    try:
        deleted = db_manager.delete_simod_output(simod_scenario_id)
        if not deleted:
            return (
                jsonify(
                    {"status": "error", "message": f"No simod output found for simod_scenario_id {simod_scenario_id}."}
                ),
                404,
            )
        return "", 204
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error deleting simod output: {e}"}), 500


@simod_output_bp.route("/storage/update-simod-output", methods=["PUT"])
def update_simod_output_api():
    """
    Replace the CSV for an existing Simod simulation output.

    Args:
        simod_scenario_id (query int): ID of the simod scenario to update (required).
        file (form file): New CSV file containing the updated output (required).

    Returns:
        JSON response (200): {"status": "success", "message": str}
        JSON response (400): {"status": "error", "message": str}
        JSON response (404): {"status": "error", "message": str}
        JSON response (500): {"status": "error", "message": str}

    Curl example:
        curl -X PUT "http://localhost:8888/storage/update-simod-output?simod_scenario_id=1" \
            -F "file=@LoanApp.csv"
    """
    simod_scenario_id = request.args.get("simod_scenario_id", type=int)
    if simod_scenario_id is None:
        return (
            jsonify({"status": "error", "message": "simod_scenario_id is required and must be a valid integer."}),
            400,
        )
    if not simod_scenario_id:
        return jsonify({"status": "error", "message": "simod_scenario_id is required."}), 400

    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400
    file = request.files["file"]

    raw_data = file.read()
    if not raw_data:
        return jsonify({"status": "error", "message": "Uploaded file is empty."}), 400

    try:
        updated_count = db_manager.update_simod_output(simod_scenario_id, file.filename, raw_data)
        if updated_count is None:
            return (
                jsonify({"status": "error", "message": "Error updating simod output: Database operation failed."}),
                500,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error updating simod output: {e}"}), 500

    if updated_count == 0:
        return (
            jsonify(
                {"status": "error", "message": f"No output found to update for simod_scenario_id {simod_scenario_id}."}
            ),
            404,
        )
    return jsonify({"status": "success", "message": "simod output updated successfully."}), 200
