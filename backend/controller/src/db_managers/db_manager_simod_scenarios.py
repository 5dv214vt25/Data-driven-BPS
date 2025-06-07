"""
This file contains the DBManagerSimodScenarios class, which
is used to manage the database operations related to Simod scenarios.
"""

import psycopg2
from src.db_managers.url_builder import build_database_url


class DBManagerSimodScenario:
    """
    This class manages the database operations related to Simod scenarios.
    It provides methods to store, retrieve, update and delete scenarios
    in the PostgreSQL database. It manages event log specific scenarios and
    handles database connections.
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
        Create and return a database connection.

        Returns:
            psycopg2.extensions.connection: An active connection to the PostgreSQL database.
        """
        return psycopg2.connect(self.db_url)

    def list_simod_scenarios(self, user_id, event_log_id=None):
        """
        Fetches scenarios for a specific user, optionally filtered by event log ID.

        Args:
            user_id (str): The ID of the user.
            event_log_id (int, optional): The ID of the event log to filter by.

        Returns:
            list: A list of dictionaries containing information about the scenarios.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT s.id, s.event_log_id, s.name, e.filename as event_log_name
                FROM simod_scenarios s
                JOIN event_logs e ON s.event_log_id = e.id
                WHERE e.user_id = %s
            """

            params = [user_id]

            if event_log_id:
                query += " AND e.id = %s"
                params.append(event_log_id)

            query += " ORDER BY s.id"

            cursor.execute(query, tuple(params))
            scenarios = cursor.fetchall()
            cursor.close()
            conn.close()

            if not scenarios:
                return []

            response_data = [
                {"scenario_id": s[0], "event_log_id": s[1], "scenario_name": s[2], "event_log_name": s[3]}
                for s in scenarios
            ]

            return response_data

        except psycopg2.Error as e:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            print(f"Database error: {str(e)}", flush=True)
            return []

    def get_simod_scenario(self, id):
        """
        Fetches a specific scenarios for an event log made from simod.

        Args:
            id (int): The ID of the simod scenario.

        Returns:
            dict: Simod Scenario entity with all the variables
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, event_log_id, file_bpmn, param_json FROM simod_scenarios WHERE id = %s;",
            (id,),
        )
        scenario = cursor.fetchone()
        cursor.close()
        conn.close()
        if scenario:
            return {
                "id": scenario[0],
                "name": scenario[1],
                "event_log_id": scenario[2],
                "file_bpmn": scenario[3],  # Return bytes directly
                "param_json": scenario[4],  # Return bytes directly
            }
        else:
            return {"error": "Scenario not found"}, 404

    def create_simod_scenario(self, data):
        """
        Stores a simod scenario.

        Args:
            data (json): a json with the name, event_log_id, file_bpmn

        Returns:
            int: id of scenario
            str: name of the scenario
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO simod_scenarios (event_log_id, name, file_bpmn, param_json) VALUES (%s, %s, %s, %s) RETURNING id;",
            (data["event_log_id"], data["name"], data["file_bpmn"], data["param_json"]),
        )
        new_scenario = cursor.fetchone()
        if new_scenario:
            conn.commit()
            cursor.close()
            conn.close()
            return new_scenario[0]
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            return {"error": "Scenario not created"}

    def update_simod_scenario(self, scenario_id, name=None, param_json=None):
        """
        Updates a simod scenario with optional parameters

        Args:
            scenario_id (int): The ID of the scenario to update
            name (str, optional): New name for the scenario
            param_json (bytes, optional): New parameters JSON content

        Returns:
            int: The ID of the updated scenario if successful
            dict: Error message if update fails
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Build the update query dynamically based on provided parameters
            update_parts = []
            params = []

            if name is not None:
                update_parts.append("name = %s")
                params.append(name)

            if param_json is not None:
                update_parts.append("param_json = %s")
                params.append(param_json)

            # If no parameters were provided to update
            if not update_parts:
                return {"error": "No update parameters provided"}, 400

            query = f"UPDATE simod_scenarios SET {', '.join(update_parts)} WHERE id = %s RETURNING id"
            params.append(scenario_id)

            cursor.execute(query, tuple(params))
            updated_scenario = cursor.fetchone()

            if not updated_scenario:
                conn.rollback()
                return {"error": "Scenario not found"}, 404

            conn.commit()
            return updated_scenario[0]

        except Exception as e:
            conn.rollback()
            return {"error": f"Failed to update scenario: {str(e)}"}, 500
        finally:
            cursor.close()
            conn.close()

    def delete_simod_scenario(self, id):
        """
        Deletes a simod scenario

        Args:
            id (int): The ID of the Scenario to delete

        Returns:
            json: Message if it deleted successfully or not
        """
        conn = self.get_connection()

        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM simod_scenarios WHERE id = %s",
                (id,),
            )
            conn.commit()

            # Verify deletion by checking if the record still exists
            cursor.execute(
                "SELECT COUNT(*) FROM simod_scenarios WHERE id = %s",
                (id,),
            )
            count = cursor.fetchone()[0]

            if count == 0:
                return {"message": "Scenario deleted successfully"}
            else:
                return {"message": "Scenario deletion failed", "error": "Record still exists"}
        except Exception as e:
            conn.rollback()  # Rollback in case of error
            return {"message": "Scenario deletion failed", "error": str(e)}
        finally:
            cursor.close()
            conn.close()
