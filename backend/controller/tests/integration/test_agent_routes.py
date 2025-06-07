"""
Integration tests for the Agent routes.
"""

import zipfile
from io import BytesIO
from unittest.mock import MagicMock

import pytest
from flask import Flask
from src.db_managers.db_manager_agent_output import DBManagerAgentOutput
from src.db_managers.db_manager_agent_scenarios import DBManagerAgentScenarios
from src.db_managers.db_manager_event_log import DBManagerEventLog
from src.routes.agent.agent_routes import agent_bp

# import requests

# Create a Flask app for testing
app = Flask(__name__)
app.register_blueprint(agent_bp)


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
    mock_agent_scenario = mocker.patch.object(DBManagerAgentScenarios, "get_agent_scenario")
    mock_create_scenario = mocker.patch.object(DBManagerAgentScenarios, "upload_agent_scenario")
    mock_agent_output = mocker.patch.object(DBManagerAgentOutput, "upload_agent_output")
    return {
        "event_log": mock_event_log,
        "agent_scenario": mock_agent_scenario,
        "create_scenario": mock_create_scenario,
        "agent_output": mock_agent_output,
    }


@pytest.fixture
def mock_requests_post(mocker):
    """Mock requests.post."""
    return mocker.patch("requests.post")


def test_start_agent_discovery_success(client, mock_db_managers, mock_requests_post):
    """Test successful Agent discovery with save_boolean=true."""
    # Arrange: Mock database and API responses
    mock_db_managers["event_log"].return_value = {
        "filename": "event_log.csv",
        "event_log": b"case_id,activity,timestamp\n1,Start,2023-01-01",
    }
    mock_db_managers["create_scenario"].return_value = 123

    # Create a mock ZIP file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("model.pkl", b"<bpmn>model</bpmn>")
        zip_file.writestr("params.json", b'{"param": "value"}')
        zip_file.writestr("visualization.json", b'{"visual": "value"}')
    zip_buffer.seek(0)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = zip_buffer.getvalue()
    mock_requests_post.return_value = mock_response

    # Act: Send POST request
    response = client.post(
        "/api/start-agent-discovery?user_id=skib&event_log_id=1&save_boolean=true&name=test_scenario"
    )

    # Assert: Check response
    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    assert response.headers["X-Scenario-ID"] == "123"
    assert response.headers["Access-Control-Expose-Headers"] == "X-Scenario-ID"
    assert response.data == zip_buffer.getvalue()


def test_start_agent_discovery_missing_params(client):
    """Test Agent discovery with missing parameters."""
    # Act: Send POST request without user_id
    response = client.post("/api/start-agent-discovery?event_log_id=1")

    # Assert: Check error response
    assert response.json == {"status": "error", "message": "Missing user_id or event_log_id parameters"}


def test_start_agent_discovery_event_log_not_found(client, mock_db_managers):
    """Test Agent discovery when the event log does not exist"""
    # Arrange: Setup mock database to return None
    mock_db_managers["event_log"].return_value = None

    # Act: Send POST request with non-existing event log
    response = client.post("/api/start-agent-discovery?user_id=skib&event_log_id=2")

    # Assert: Check error message
    assert response.json == {"status": "error", "message": "Event log not found"}


def test_start_agent_simulation_missing_params(client):
    """Test Agent simulation with missing parameters"""
    response = client.get("/api/start-agent-simulation?scenario_id=1")

    assert response.json == {"status": "error", "message": "Missing user_id or scenario_id parameters"}
