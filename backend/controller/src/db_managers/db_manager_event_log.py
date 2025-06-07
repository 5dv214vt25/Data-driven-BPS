"""
This file contains the DBManagerEventLog class, which
is used to manage the database operations related to event logs.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from src.db_managers.url_builder import build_database_url


class DBManagerEventLog:
    """
    This class manages the database operations related to event logs.
    It provides methods to store, retrieve, and delete event-logs
    in the PostgreSQL database. It manages user-specific event-logs and
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

    def store_event_log(self, user_id, event_log, filename):
        """
        Store an event log for a specific user.

        Args:
            user_id (str): The ID of the user.
            event_log (bytes): The event log data as binary.
            filename (str): The name of the file.

        Returns:
            int: The ID of the stored event log or None if an error occurred.

        Raises:
            Exception: If there is an error during database operation.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO event_logs (user_id, event_log, filename) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, event_log, filename),
                )
                event_log_id = cursor.fetchone()[0]
                conn.commit()
                return event_log_id
        except Exception as e:
            conn.rollback()
            print(f"Error storing event log: {e}", flush=True)
            return None
        finally:
            conn.close()

    def get_event_log(self, user_id, event_log_id):
        """
        Retrieve an event log for a specific user and event log ID.

        Args:
            user_id (str): The ID of the user.
            event_log_id (int): The ID of the event log to retrieve.

        Returns:
            dict or None: A dictionary containing 'filename' and 'event_log' keys if found,
                         or None if not found or an error occurred.

        Raises:
            Exception: If there is an error during database operation.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT filename, event_log FROM event_logs WHERE user_id = %s AND id = %s", (user_id, event_log_id)
                )
                result = cursor.fetchone()

                if result:
                    return {"filename": result["filename"], "event_log": result["event_log"]}
                else:
                    print(f"Event log {event_log_id} not found for user {user_id}.", flush=True)
                    return None
        finally:
            conn.close()

    def update_event_log(self, user_id, event_log_id, filename):
        """
        Update an event log in the database.

        Args:
            user_id (str): The ID of the user.
            event_log_id (int): The ID of the event log to update.
            filename (str): The new name of the event log.

        Returns:
            bool: True if the event log was updated successfully, False otherwise.
        """

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE event_logs SET filename = %s WHERE user_id = %s AND id = %s",
                    (filename, user_id, event_log_id),
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating event log: {e}", flush=True)
            return False
        finally:
            conn.close()

    def get_all_stored_event_log_information(self, user_id):
        """
        Get all stored event logs under the specified user_id.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list: A list of dictionaries containing 'event_log_id' and 'filename'
                 for each event log. Returns an empty list if no event logs are found.

        Raises:
            Exception: If there is an error during database operation.
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, filename FROM event_logs WHERE user_id = %s ORDER BY id", (user_id,))
                results = cursor.fetchall()

                return [{"event_log_id": result["id"], "filename": result["filename"]} for result in results]
        finally:
            conn.close()

    def delete_event_log(self, user_id, event_log_id):
        """
        Delete an event log from the database.

        Args:
            user_id (str): The ID of the user.
            event_log_id (int): The ID of the event log to delete.

        Returns:
            bool: True if the event log was deleted successfully, False otherwise.

        Raises:
            Exception: If there is an error during database operation.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM event_logs WHERE user_id = %s AND id = %s", (user_id, event_log_id))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error deleting event log: {e}", flush=True)
            return False
        finally:
            conn.close()

    def delete_all_event_logs(self, user_id):
        """
        Delete all event logs for a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if all event logs were deleted successfully, False otherwise.

        Raises:
            Exception: If there is an error during database operation.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM event_logs WHERE user_id = %s", (user_id,))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error deleting all event logs: {e}", flush=True)
            return False
        finally:
            conn.close()
