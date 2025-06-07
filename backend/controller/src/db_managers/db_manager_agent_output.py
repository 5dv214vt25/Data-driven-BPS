"""
This file contains the DBManagerAgentOutput class, which
is used to manage the database operations related to AgentSimulator simulation outputs.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from src.db_managers.url_builder import build_database_url


class DBManagerAgentOutput:
    """
    This class manages the database operations related to AgentSimulator simulation outputs.
    It includes methods to upload, list, get, update, and delete AgentSimulator simulation outputs in the database.
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

    def upload_agent_output(self, agent_scenario_id, filename, output_data):
        """
        Create a new AgentSimulator output entry in the database.

        Args:
            agent_scenario_id (int): The ID of the agent scenario.
            filename (str): The name of the output file.
            output_data (bytes): The output data to be stored.

        Returns:
            bool: True if the entry was created successfully, False otherwise.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO agent_outputs (agent_scenario_id, filename, output_data)
                    VALUES (%s, %s, %s)
                    """,
                    (agent_scenario_id, filename, output_data),
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error uploading agent output: {e}", flush=True)
            raise
        finally:
            conn.close()

    def list_agent_outputs(self, user_id, agent_scenario_id=None):
        """
        Lists all AgentSimulator outputs metadata for a given user ID and optional agent scenario ID.
        If agent_scenario_id is provided, it filters the results by that ID.

        Args:
            user_id (str): The ID of the user.
            agent_scenario_id (int, optional): The ID of the agent scenario. If provided, only return scenarios for that id.

        Returns:
            list: A list of dictionaries containing output information.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT ao.agent_scenario_id, ao.filename, s.name as scenario_name,
                    s.event_log_id, el.filename as event_log_name
                    FROM agent_outputs ao
                    JOIN agent_scenarios s ON ao.agent_scenario_id = s.id
                    JOIN event_logs el ON s.event_log_id = el.id
                    WHERE el.user_id = %s
                """
                params = [user_id]

                if agent_scenario_id is not None:
                    query += " AND s.id = %s"
                    params.append(agent_scenario_id)

                query += " ORDER BY ao.agent_scenario_id"

                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                if not rows:
                    return []

                return [
                    {
                        "agent_scenario_id": row["agent_scenario_id"],
                        "output_filename": row["filename"],
                        "scenario_name": row["scenario_name"],
                        "event_log_id": row["event_log_id"],
                        "event_log_name": row["event_log_name"],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Database error when listing agent outputs: {e}", flush=True)
            return None
        finally:
            conn.close()

    def get_agent_output(self, agent_scenario_id):
        """
        Get a specific AgentSimulator output by its scenario ID.

        Args:
            agent_scenario_id (int): The ID of the agent scenario.

        Returns:
            tuple(str, bytes): The filename and the raw output_data bytes, or None if not found.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT agent_scenario_id, filename, output_data
                    FROM agent_outputs
                    WHERE agent_scenario_id = %s
                    """,
                    (agent_scenario_id,),
                )
                row = cursor.fetchone()
                if not row:
                    print(f"Agent output {agent_scenario_id} not found.", flush=True)
                    return None

                data = bytes(row["output_data"])
                return row["filename"], data
        finally:
            conn.close()

    def update_agent_output(self, agent_scenario_id, filename, output_data):
        """
        Update an existing AgentSimulator output entry in the database.

        Args:
            agent_scenario_id (int): The ID of the agent scenario.
            filename (str): The name of the output file.
            output_data (bytes): The new output data to be stored.

        Returns:
            int: The number of rows affected by the update.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE agent_outputs
                    SET filename = %s, output_data = %s
                    WHERE agent_scenario_id = %s
                    """,
                    (filename, output_data, agent_scenario_id),
                )
                rowcount = cursor.rowcount
                conn.commit()
                return rowcount
        except Exception as e:
            conn.rollback()
            print(f"Error updating agent output {agent_scenario_id}: {e}", flush=True)
            raise
        finally:
            conn.close()

    def delete_agent_output(self, agent_scenario_id):
        """
        Delete a AgentSimulator output by its ID.

        Args:
            agent_scenario_id (int): The ID of the agent scenario.

        Returns:
            bool: Returns True if the deletion was succesful and at least one row was deleted, False otherwise.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM agent_outputs
                    WHERE agent_scenario_id = %s
                    """,
                    (agent_scenario_id,),
                )
                deleted = cursor.rowcount
            conn.commit()
            return deleted > 0
        except Exception as e:
            conn.rollback()
            print(f"Error deleting agent output {agent_scenario_id}: {e}", flush=True)
            return False
        finally:
            conn.close()
