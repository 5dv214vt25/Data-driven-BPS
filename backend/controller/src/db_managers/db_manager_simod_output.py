"""
This file contains the DBManagerSimodOutput class, which
is used to manage the database operations related to Simod simulation outputs.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from src.db_managers.url_builder import build_database_url


class DBManagerSimodOutput:
    """
    This class manages the database operations related to Simod simulation outputs.
    It includes methods to upload, list, get, update, and delete Simod simulation outputs in the database.
    Also includes a method to get a database connection.
    """

    def __init__(self):
        self.db_url = build_database_url()

    def get_connection(self):
        """Create and return a database connection"""
        return psycopg2.connect(self.db_url)

    def upload_simod_output(self, simod_scenario_id, filename, output_data):
        """
        Create a new simod output entry in the database.

        Args:
            simod_scenario_id (int): The ID of the simod scenario.
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
                    INSERT INTO simod_outputs (simod_scenario_id, filename, output_data)
                    VALUES (%s, %s, %s)
                    """,
                    (simod_scenario_id, filename, output_data),
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error uploading simod output: {e}", flush=True)
            raise
        finally:
            conn.close()

    def list_simod_outputs(self, user_id, scenario_id=None):
        """
        List all simod outputs metadata for a specific user, optionally filtered by event log ID.

        Args:
            user_id (str): The ID of the user.
            scenario_id (int, optional): The ID of the scenario to filter by.

        Returns:
            list: A list of dictionaries containing output information.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT so.simod_scenario_id, so.filename, s.name as scenario_name,
                    s.event_log_id, e.filename as event_log_name
                    FROM simod_outputs so
                    JOIN simod_scenarios s ON so.simod_scenario_id = s.id
                    JOIN event_logs e ON s.event_log_id = e.id
                    WHERE e.user_id = %s
                """

                params = [user_id]

                if scenario_id:
                    query += " AND s.id = %s"
                    params.append(scenario_id)

                query += " ORDER BY so.simod_scenario_id"

                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()

                return [
                    {
                        "simod_scenario_id": row["simod_scenario_id"],
                        "output_filename": row["filename"],
                        "scenario_name": row["scenario_name"],
                        "event_log_id": row["event_log_id"],
                        "event_log_name": row["event_log_name"],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Database error when listing simod outputs: {e}", flush=True)
            return None
        finally:
            conn.close()

    def get_simod_output(self, simod_scenario_id):
        """
        Get a specific simod output by its ID.

        Args:
            simod_scenario_id (int): The ID of the simod scenario.

        Returns:
            tuple(str, bytes): The filename and the raw output_data bytes, or None if not found.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT simod_scenario_id, filename, output_data
                    FROM simod_outputs
                    WHERE simod_scenario_id = %s
                    """,
                    (simod_scenario_id,),
                )
                row = cursor.fetchone()
                if not row:
                    print(f"simod output {simod_scenario_id} not found.", flush=True)
                    return None

                data = bytes(row["output_data"])
                return row["filename"], data
        finally:
            conn.close()

    def update_simod_output(self, simod_scenario_id, filename, output_data):
        """
        Update an existing simod output entry in the database.

        Args:
            simod_scenario_id (int): The ID of the simod scenario.
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
                    UPDATE simod_outputs
                    SET filename = %s, output_data = %s
                    WHERE simod_scenario_id = %s
                    """,
                    (filename, output_data, simod_scenario_id),
                )
                rowcount = cursor.rowcount
                conn.commit()
                return rowcount
        except Exception as e:
            conn.rollback()
            print(f"Error updating simod output {simod_scenario_id}: {e}", flush=True)
            raise
        finally:
            conn.close()

    def delete_simod_output(self, simod_scenario_id):
        """
        Delete a specific simod output by its ID.

        Args:
            simod_scenario_id (int): The ID of the simod scenario.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM simod_outputs
                    WHERE simod_scenario_id = %s
                    """,
                    (simod_scenario_id,),
                )
                deleted = cursor.rowcount
            conn.commit()
            return deleted > 0
        except Exception as e:
            conn.rollback()
            print(f"Error deleting simod output {simod_scenario_id}: {e}", flush=True)
            return False
        finally:
            conn.close()


if __name__ == "__main__":
    db_manager = DBManagerSimodOutput()
