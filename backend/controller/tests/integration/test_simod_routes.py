"""
Endpoint tests for the simod routes.
"""

import zipfile
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from flask import Flask
from src.db_managers.db_manager_event_log import DBManagerEventLog
from src.db_managers.db_manager_simod_output import DBManagerSimodOutput
from src.db_managers.db_manager_simod_scenarios import DBManagerSimodScenario
from src.routes.simod.simod_routes import simod_bp

# import requests

# Create a Flask app for testing
app = Flask(__name__)
app.register_blueprint(simod_bp)


# Creates the client to curl towards
@pytest.fixture
def client():
    """Provide a Flask test client."""
    return app.test_client()


# Mocks databases
@pytest.fixture
def mock_db_managers(mocker):
    """Mock all database managers."""
    mock_event_log = mocker.patch.object(DBManagerEventLog, "get_event_log")
    mock_simod_scenario = mocker.patch.object(DBManagerSimodScenario, "get_simod_scenario")
    mock_create_scenario = mocker.patch.object(DBManagerSimodScenario, "create_simod_scenario")
    mock_simod_output = mocker.patch.object(DBManagerSimodOutput, "upload_simod_output")
    return {
        "event_log": mock_event_log,
        "simod_scenario": mock_simod_scenario,
        "create_scenario": mock_create_scenario,
        "simod_output": mock_simod_output,
    }


@pytest.fixture
def mock_requests_post(mocker):
    """Mock requests.post."""
    return mocker.patch("requests.post")


def test_start_simod_discovery_success(client, mock_db_managers, mock_requests_post):
    """Test successful Simod discovery with save_boolean=true."""
    # Arrange: Mock database and API responses
    mock_db_managers["event_log"].return_value = {
        "filename": "event_log.csv",
        "event_log": b"case_id,activity,timestamp\n1,Start,2023-01-01",
    }
    mock_db_managers["create_scenario"].return_value = 123

    # Create a mock ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("simod_model.bpmn", b"<bpmn>model</bpmn>")
        zip_file.writestr("parameters.json", b'{"param": "value"}')
    zip_buffer.seek(0)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = zip_buffer.getvalue()
    mock_requests_post.return_value = mock_response

    # Act: Send POST request
    response = client.post(
        "/api/start-simod-discovery?user_id=skib&event_log_id=1&save_boolean=true&name=test_scenario"
    )

    # Assert: Check response
    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    assert response.headers["X-Scenario-ID"] == "123"
    assert response.headers["Access-Control-Expose-Headers"] == "X-Scenario-ID"
    assert response.data == zip_buffer.getvalue()


def test_start_simod_discovery_missing_params(client):
    """Test Simod discovery with missing parameters."""
    # Act: Send POST request without user_id
    response = client.post("/api/start-simod-discovery?event_log_id=1")

    # Assert: Check error response
    assert response.json == {"status": "error", "message": "Missing user_id or event_log_id parameters"}


def test_start_simod_discovery_event_log_not_found(client, mock_db_managers):
    """Test Simod discovery when the event log does not exist"""
    # Arrange: Setup mock database to return None
    mock_db_managers["event_log"].return_value = None

    # Act: Send POST request with non-existing event log
    response = client.post("/api/start-simod-discovery?user_id=skib&event_log_id=2")

    # Assert: Check error message
    assert response.json == {"status": "error", "message": "Event log not found"}


def _test_start_simod_simulation_success(client, mock_db_managers, mock_requests_post):
    """Test succesful Simod Simulation"""

    mock_db_managers["simod_scenario"].return_value = {
        "file_bpmn": b"<bpmn>model</bpmn>",
        "param_json": b'{"param": "value"}',
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"case_id,activity,timestamp\n1,Start,2023-01-01"
    mock_requests_post.return_value = mock_response

    response = client.get("api/start-simod-simulation?user_id=skib&scenario_id=1&save_boolean=true")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.data == b"case_id,activity,timestamp\n1,Start,2023-01-01"


def test_start_simod_simulation_missing_params(client):
    """Test Simod simulation with missing parameters"""
    response = client.get("/api/start-simod-simulation?scenario_id=1")

    assert response.json == {"status": "error", "message": "Missing user_id or scenario_id parameters"}
