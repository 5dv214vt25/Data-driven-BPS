"""
This file contains the DBManagerAgentScenarios class, which
is used to manage the database operations related to AgentSimulator scenarios.
"""

import psycopg2
from src.db_managers.url_builder import build_database_url


class DBManagerAgentScenarios:
    """
    This class manages the database operations related to AgentSimulator scenarios.
    It includes methods to upload, list, get, update, and delete AgentSimulator scenarios in the database.
    Also includes a method to get a database connection.
    """

    def __init__(self):
        """
        Initialize the database manager with the database connection URL.

        The connection URL is retrieved from the DATABASE_URL environment
        variable or uses a default connection string if not set.
        """
        self.db_url = build_database_url()

    def get_connection(self):
        """
        Open and return a new psycopg2 connection using the configured URL.

        Returns:
            psycopg2.connection: Active database connection; caller must close it.
        """
        return psycopg2.connect(self.db_url)

    def upload_agent_scenario(self, data):
        """
        Uploads an AgentSimulator scenario to the database.

        Args:
            data (dict): A dictionary containing the scenario details:
                - event_log_id (int)
                - name (str)
                - model_pkl (bytes)
                - param_json (bytes)
                - visualization_json (bytes)

        Returns:
            int: The new scenario database ID on success.
            dict: {"status": "error", "message": "..."} on failure.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO agent_scenarios
                (event_log_id, name, model_pkl, param_json, visualization_json)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (data["event_log_id"], data["name"], data["model_pkl"], data["param_json"], data["visualization_json"]),
        )
        new_scenario = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if new_scenario:
            return new_scenario[0]
        else:
            return {"status": "error", "message": "Scenario not uploaded"}

    def list_agent_scenarios(self, user_id, event_log_id=None):
        """
        Retrieve all AgentSimulator scenarios for a given user, optionally filtered by event log.

        Args:
            user_id (int): Users ID.
            event_log_id (int, optional): If provided, only scenarios for this log.

        Returns:
            list[dict]: Each with keys:
                - id (int), event_log_id (int), name (str), event_log_name (str)
            Returns [] if none found or on DB error.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT a.id, a.event_log_id, a.name, el.filename as event_log_name
                FROM agent_scenarios AS a
                JOIN event_logs AS el ON a.event_log_id = el.id
                WHERE el.user_id = %s
            """
            params = [user_id]

            if event_log_id is not None:
                query += " AND el.id = %s"
                params.append(event_log_id)

            query += " ORDER BY a.id"

            cursor.execute(query, tuple(params))
            scenarios = cursor.fetchall()
            cursor.close()
            conn.close()

            if not scenarios:
                return []

            response_data = [
                {"id": s[0], "event_log_id": s[1], "name": s[2], "event_log_name": s[3]} for s in scenarios
            ]

            return response_data
        except psycopg2.Error as e:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            print(f"Database error: {str(e)}", flush=True)
            return []

    def get_agent_scenario(self, id):
        """
        Fetch one AgentSimulator scenario by its ID.

        Args:
            id (int): Scenario database ID.

        Returns:
            dict: On success, keys:
                - id, event_log_id, name, model_pkl (bytes),
                  param_json (bytes), visualization_json (bytes)
            tuple: ({"status": "error", "message": "Scenario not found"}, 404)
                    if no matching record.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, event_log_id, name, model_pkl, param_json, visualization_json FROM agent_scenarios WHERE id = %s",
            (id,),
        )
        scenario = cursor.fetchone()
        cursor.close()
        conn.close()

        if scenario:
            return {
                "id": scenario[0],
                "event_log_id": scenario[1],
                "name": scenario[2],
                "model_pkl": scenario[3],
                "param_json": scenario[4],
                "visualization_json": scenario[5],
            }
        else:
            return {"status": "error", "message": "Scenario not found"}, 404

    def update_agent_scenario(self, id, name=None, param_json=None):
        """
        Change a AgentSimulator scenario's name and/or parameter JSON.

        Args:
            id (int): Scenario ID to update.
            name (str, optional): New scenario name.
            param_json (bytes, optional): New JSON bytes.

        Returns:
            int: The scenario ID on successful update.
            tuple: ({"status": "error", "message": "..."}, code)
                    if update fails.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            update_parts = []
            params = []

            if name is not None:
                update_parts.append("name = %s")
                params.append(name)

            if param_json is not None:
                update_parts.append("param_json = %s")
                params.append(param_json)

            if not update_parts:
                return {"status": "error", "message": "No update parameters provided."}, 400

            query = f"UPDATE agent_scenarios SET {', '.join(update_parts)} WHERE id = %s RETURNING id"
            params.append(id)

            cursor.execute(query, tuple(params))

            updated_scenario = cursor.fetchone()
            if not updated_scenario:
                conn.rollback()
                return {"status": "error", "message": "Scenario not found"}, 404

            conn.commit()
            return updated_scenario[0]
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": f"Failed to update scenario: {str(e)}"}, 500
        finally:
            cursor.close()
            conn.close()

    def delete_agent_scenario(self, id):
        """
        Remove a AgentSimulator scenario by its ID.

        Args:
            id (int): Scenario ID.

        Returns:
            dict: success or error message.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM agent_scenarios WHERE id = %s RETURNING id",
                (id,),
            )
            deleted = cursor.fetchone()
            if deleted is None:
                conn.commit()
                return {"status": "error", "message": "Scenario not found"}

            conn.commit()
            return {"status": "success", "message": "Scenario deleted successfully"}
        except Exception as e:
            conn.rollback()
            return {"status": "error", "message": "Scenario deletion failed", "error": str(e)}
        finally:
            cursor.close()
            conn.close()
