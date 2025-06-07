"""
This script is the main entry point for the controller, responsible for starting the Flask
application and defining the API endpoints between the frontend and backend.
"""

import os

from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

# Import route blueprints
from src.routes.agent.agent_output_routes import agent_output_bp
from src.routes.agent.agent_routes import agent_bp
from src.routes.agent.agent_scenarios_routes import agent_scenarios_bp
from src.routes.analysis.analyze_routes import analyze_bp
from src.routes.event_log.event_log_route import event_log_bp
from src.routes.general.demo_route import demo_bp
from src.routes.simod.simod_output_routes import simod_output_bp
from src.routes.simod.simod_routes import simod_bp
from src.routes.simod.simod_scenarios_routes import simod_scenarios_bp

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Configure Swagger documentation UI
SWAGGER_URL = "/api/docs"
API_URL = "/static/openapi.yaml"

# Only expose Swagger UI in non-production environments
if os.environ.get("FLASK_ENV") != "production":
    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "Controller API Documentation", "docExpansion": "none"},  # Collapse all sections by default
    )
    # Register the Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Register the blueprint
app.register_blueprint(agent_bp)
app.register_blueprint(demo_bp)
app.register_blueprint(event_log_bp)
app.register_blueprint(simod_bp)
app.register_blueprint(simod_scenarios_bp)
app.register_blueprint(simod_output_bp)
app.register_blueprint(agent_output_bp)
app.register_blueprint(agent_scenarios_bp)
app.register_blueprint(analyze_bp)


@app.route("/api/health-check", methods=["GET"])
def health_check():
    """
    Health check endpoint to ensure the controller is running.
    """
    return jsonify({"status": "OK", "message": "Controller is running."}), 200


@app.route("/static/openapi.yaml")
def serve_openapi_spec():
    """Serve the OpenAPI specification file."""
    # Only serve the OpenAPI spec in non-production environments
    if os.environ.get("FLASK_ENV") == "production":
        return jsonify({"error": "Not available in production"}), 403
    try:
        return app.send_static_file("main.yaml")
    except Exception as e:
        app.logger.error(f"Error serving openapi.yaml: {str(e)}")
        return jsonify({"error": "Could not serve OpenAPI specification"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
