"""
This file contains the demo endpoints that calls
the Simod API and the Agent Simulator API.

The endpoints are:
- /api/get-test-message-from-controller
- /api/simod-demo-request
- /api/agent-simulator-demo-request

Example curl commands:
- Get a test message from the controller
    curl http://localhost:8888/api/get-test-message-from-controller
- Get a test message from the simod
    curl http://localhost:8888/api/simod-demo-request
- Get a test message from the agent simulator
    curl http://localhost:8888/api/agent-simulator-demo-request
"""

import requests
from flask import Blueprint
from flask import jsonify

demo_bp = Blueprint("demo", __name__)


@demo_bp.route("/api/get-test-message-from-controller", methods=["GET"])
def get_test_message_controller():
    """
    Demo request to get a test message from the controller.

    Args:
        None

    Returns:
        json: A JSON object with a message.

    Curl example:
        curl http://localhost:8888/api/get-test-message-from-controller
    """

    return jsonify({"message": "Hello World From Controller!"})


@demo_bp.route("/api/simod-demo-request", methods=["GET"])
def simod_demo_request():
    """
    Demo request to get a test message from the simod.

    Args:
        None

    Returns:
        json: A JSON object with a message or an error.

    Curl example:
        curl http://localhost:8888/api/simod-demo-request
    """

    url = "http://simod:6001/api/get-test-message-from-simod-api"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data, flush=True)
    else:
        return jsonify({"error": "Failed to get message from simod"})

    return jsonify(data)


@demo_bp.route("/api/agent-simulator-demo-request", methods=["GET"])
def agent_simulator_demo_request():
    """
    Demo request to get a test message from the agent simulator.

    Args:
        None

    Returns:
        json: A JSON object with a message or an error.

    Curl example:
        curl http://localhost:8888/api/agent-simulator-demo-request
    """

    url = "http://agent_simulator:6002/api/get-test-message-from-agent-simulator-api"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data, flush=True)
    else:
        return jsonify({"error": "Failed to get message from agent simulator"})

    return jsonify(data)
