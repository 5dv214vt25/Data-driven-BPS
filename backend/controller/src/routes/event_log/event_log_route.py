"""
This file contains the endpoints related to event logs.

The endpoints are:
- /storage/upload-event-log: Upload an event log to the backend.
- /storage/get-event-log: Get an event log from the backend.
- /storage/update-event-log: Update an event log in the backend.
- /storage/list-event-logs: Get information about all event logs for a specific user.
- /storage/delete-event-log: Delete an event log from the backend.
- /storage/delete-all-event-logs: Delete all event logs for a specific user.
- /api/xes-to-csv: Convert an xes file to a csv file.
- /api/csv-to-xes: Convert a csv file to an xes file.


Example curl commands:
- Upload an event log
    curl -X POST http://localhost:8888/storage/upload-event-log -F "user_id=cs_user" -F "file=@event_log_example.csv"
- Get an event log
    curl -X GET "http://localhost:8888/storage/get-event-log?user_id=cs_user&event_log_id=1" -o event_log_example.csv
- Update an event log
    curl -X PUT "http://localhost:8888/storage/update-event-log?user_id=cs_user&event_log_id=1&filename=new_event_log.csv"
- List all event logs
    curl -X GET "http://localhost:8888/storage/list-event-logs?user_id=cs_user"
- Delete an event log
    curl -X DELETE "http://localhost:8888/storage/delete-event-log?user_id=cs_user&event_log_id=1"
- Delete all event logs
    curl -X DELETE "http://localhost:8888/storage/delete-all-event-logs?user_id=cs_user"
- Convert an xes file to a csv file
    curl -POST "http://localhost:8888/api/xes-to-csv" -F "file=@BPIC12.xes"
- Convert a csv file to an xes file
    curl -POST "http://localhost:8888/api/csv-to-xes" -F "file=@BPIC12.csv"
"""

from io import BytesIO

import pandas as pd
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import send_file
from src.db_managers.db_manager_event_log import DBManagerEventLog
from src.eventlog_validator import validate_eventlog_format
from src.routes.utils.convert_files import convert_to_csv
from src.routes.utils.convert_files import convert_to_xes

db_manager_event_log = DBManagerEventLog()


event_log_bp = Blueprint("event_log", __name__)


@event_log_bp.route("/storage/upload-event-log", methods=["POST"])
@event_log_bp.route("/api/upload-event-log", methods=["POST"])  # Deprecated
def upload_event_log():
    """
    Upload an event log to the backend.

    Args:
        user_id (form): ID of the user
        file (form): CSV file containing the event log

    Returns:
        json: Status message and event log ID if successful

    Curl example:
        curl -X POST http://localhost:8888/storage/upload-event-log -F "user_id=cs_user" -F "file=@event_log_example.csv"
    """
    # Get user_id from form data
    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required."}), 400

    # Get file from form data
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    file = request.files["file"]
    filename = file.filename

    # Validate event-log file
    file.seek(0)
    df = pd.read_csv(file)
    is_valid = validate_eventlog_format(df)
    if is_valid is not True:
        return jsonify({"status": "error", "message": is_valid}), 400

    # Store the event-log
    try:
        file.seek(0)
        file_content_bytes = file.read()
        event_log_id = db_manager_event_log.store_event_log(user_id, file_content_bytes, filename)
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred storing the event log: {str(e)}"}), 500

    # Return a status message and event-log ID
    return (
        jsonify(
            {"status": "success", "message": "Event log uploaded successfully.", "event_log_id": str(event_log_id)}
        ),
        200,
    )


@event_log_bp.route("/storage/get-event-log", methods=["GET"])
@event_log_bp.route("/api/get-event-log", methods=["GET"])  # Deprecated
def get_event_log():
    """
    Get an event log from the backend.

    Args:
        user_id (query): ID of the user
        event_log_id (query): ID of the event log

    Returns:
        file: CSV file containing the event log

    Curl example:
        curl -X GET "http://localhost:8888/storage/get-event-log?user_id=cs_user&event_log_id=1" -o event_log_example.csv
    """
    # Get user_id and event_log_id from query parameters
    user_id = request.args.get("user_id")
    event_log_id = request.args.get("event_log_id")
    if not user_id or not event_log_id:
        return jsonify({"status": "error", "message": "user_id and event_log_id are required"}), 400

    # Get the event-log from the database
    result = db_manager_event_log.get_event_log(user_id, event_log_id)
    if result is None:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Event log with {event_log_id} not found in the database. Returned None",
                }
            ),
            404,
        )

    filename, event_log_bytes = result["filename"], result["event_log"]
    if filename is None or event_log_bytes is None:
        return jsonify({"status": "error", "message": "Invalid event log data format"}), 500

    # Convert event_log_bytes to a BytesIO object
    event_log_bytes_io = BytesIO(event_log_bytes)

    # Return the event-log as a CSV file
    return send_file(
        event_log_bytes_io,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename if filename.endswith(".csv") else f"{filename}.csv",
    )


@event_log_bp.route("/storage/update-event-log", methods=["PUT"])
def update_event_log():
    """
    Update an event log in the backend.

    Args:
        user_id (query): ID of the user
        event_log_id (query): ID of the event log
        filename (query): Name of the event log

    Returns:
        json: Status message

    Curl example:
        curl -X PUT "http://localhost:8888/storage/update-event-log?user_id=cs_user&event_log_id=1&filename=new_event_log.csv"
    """
    user_id = request.args.get("user_id")
    event_log_id = request.args.get("event_log_id")
    filename = request.args.get("filename")

    if not user_id or not event_log_id or not filename:
        return jsonify({"status": "error", "message": "user_id, event_log_id, and filename are required"}), 400

    success = db_manager_event_log.update_event_log(user_id, event_log_id, filename)
    if not success:
        return jsonify({"status": "error", "message": "Failed to update event log."}), 500

    return jsonify({"status": "success", "message": "Event log updated successfully."}), 200


@event_log_bp.route("/storage/list-event-logs", methods=["GET"])
@event_log_bp.route("/api/get-all-event-logs-info", methods=["GET"])  # Deprecated
def list_event_logs():
    """
    Retrieve information about all event logs for a specific user.

    Args:
        user_id (query): ID of the user

    Returns:
        json: List of event log IDs and names

    Curl example:
        curl -X GET "http://localhost:8888/storage/list-event-logs?user_id=cs_user"
    """
    user_id = request.args.get("user_id")
    event_logs = db_manager_event_log.get_all_stored_event_log_information(user_id)

    if not event_logs:
        return "", 204
    else:
        return jsonify(event_logs), 200


@event_log_bp.route("/storage/delete-event-log", methods=["DELETE"])
@event_log_bp.route("/api/delete-event-log", methods=["DELETE"])  # Deprecated
def delete_event_log():
    """
    Delete an event log from the backend.

    Args:
        user_id (query): ID of the user
        event_log_id (query): ID of the event log

    Returns:
        json: Status and message

    Curl example:
        curl -X DELETE "http://localhost:8888/storage/delete-event-log?user_id=cs_user&event_log_id=1"
    """
    user_id = request.args.get("user_id")
    event_log_id = request.args.get("event_log_id")

    if not user_id or not event_log_id:
        return jsonify({"status": "error", "message": "user_id and event_log_id are required"}), 400

    db_manager_event_log.delete_event_log(user_id, event_log_id)

    return jsonify({"status": "success", "message": "Event log deleted successfully."}), 200


@event_log_bp.route("/storage/delete-all-event-logs", methods=["DELETE"])
@event_log_bp.route("/api/delete-all-event-logs", methods=["DELETE"])  # Deprecated
def delete_all_event_logs():
    """
    Delete all event logs for a specific user.

    Args:
        user_id (query): ID of the user

    Returns:
        json: Status and message

    Curl example:
        curl -X DELETE "http://localhost:8888/storage/delete-all-event-logs?user_id=cs_user"
    """
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    success = db_manager_event_log.delete_all_event_logs(user_id)

    if success:
        return jsonify({"status": "success", "message": "All event logs deleted successfully."}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to delete all event logs."}), 500


@event_log_bp.route("/api/xes-to-csv", methods=["POST"])
def xes_to_csv():
    """
    Returns a csv-version of an xes file.

    Limitations:
        Can only convert xes files with the same number of start and complete events
        and each start event must be directly followed by its complete event.

    Args:
        file (query): The xes file.

    Returns:
        Copy of the file in csv format.

    Curl example:
        curl -POST "http://localhost:8888/api/xes-to-csv" -F "file=@BPIC12.xes"
    """

    # Get file from form data
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    file = request.files["file"]
    filename = file.filename

    file.seek(0)
    file_content_bytes = file.read()

    try:
        file_content_bytes = convert_to_csv(file_content_bytes)
    except Exception:
        return jsonify({"status": "error", "message": "Convertion failed"}), 500

    file_content_bytes = BytesIO(file_content_bytes)

    return send_file(
        file_content_bytes,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename if filename.endswith(".csv") else f"{filename}.csv",
    )


@event_log_bp.route("/api/csv-to-xes", methods=["POST"])
def csv_to_xes():
    """
    Returns a xes-version of an csv file.

    Args:
        file (query): The csv file.

    Returns:
        Copy of the file in xes format.

    Curl example:
        curl -POST "http://localhost:8888/api/csv-to-xes" -F "file=@BPIC12.csv"
    """
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    file = request.files["file"]
    filename = file.filename

    file.seek(0)
    df = pd.read_csv(file)
    file_content_bytes = convert_to_xes(df)

    return (
        send_file(
            BytesIO(file_content_bytes),
            mimetype="application/xml",
            as_attachment=True,
            download_name=filename if filename.endswith(".xes") else f"{filename}.xes",
        ),
        200,
    )
