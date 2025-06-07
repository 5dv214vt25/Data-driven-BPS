"""
Unit tests for the simulated database functionality.

This module contains tests for storing, retrieving, and clearing event logs
in the simulated database.
"""

import unittest

from src.simulated_db import clear_database
from src.simulated_db import get_all_stored_event_log_information
from src.simulated_db import get_event_log
from src.simulated_db import get_summary_of_database_as_string
from src.simulated_db import store_event_log


class TestSimulatedDB(unittest.TestCase):
    """Test cases for event log storage and retrieval functions."""

    def setUp(self):
        """Set up the test environment before each test.

        Clears the database to ensure each test runs with a clean state.
        """
        # Clear the store before each test
        clear_database()

    def test_successful_storage(self):
        """Test that an event log can be successfully stored.

        Verifies that the store_event_log function returns True when
        an event log is successfully stored.
        """
        user_id = 123
        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_1"

        event_log_id = store_event_log(user_id, event_log, filename)

        self.assertEqual(event_log_id, 1)

    def test_getting_event_log(self):
        """Test retrieval of a stored event log.

        Verifies that an event log can be retrieved correctly after
        being stored in the database.
        """
        # First insert data
        user_id = 123
        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_1"
        event_log_id = store_event_log(user_id, event_log, filename)

        # Now check if when getting a event log its valid
        result = get_event_log(user_id, event_log_id)

        self.assertEqual(event_log, result.get("event_log"))
        self.assertEqual(filename, result.get("filename"))

    def test_clearing_database(self):
        """Test that the database can be cleared successfully.

        Verifies that after clearing the database, previously stored
        event logs can no longer be retrieved.
        """
        # First insert data
        user_id = 123
        event_log_id = 321
        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_1"
        store_event_log(user_id, event_log, filename)

        # Clear database and check whether we get None when trying to get the eventlog
        clear_database()

        result = get_event_log(user_id, event_log_id)
        self.assertEqual(None, result)

    def test_summary_output(self):
        """Test that the summary output is correct.

        Verifies that after storing two eventlogs on the same user results in
        the correct summary output
        """
        # First insert two event logs on the same user_id
        user_id = 123
        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_1"
        store_event_log(user_id, event_log, filename)

        user_id = 123
        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_2"
        store_event_log(user_id, event_log, filename)

        # Get the summary and check if its correct
        output = get_summary_of_database_as_string()

        self.assertEqual(f"User_ID: {user_id} has: 2 event logs\n", output)

    def test_getting_all_event_log_information(self):
        """
        Test that the list of event log information is correct.

        Verifies that after storing two event logs and their file names
        then when getting all event logs it is listed correctly.
        """
        # First insert two event logs on the same user_id
        user_id = 123
        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_1"
        store_event_log(user_id, event_log, filename)

        event_log = [{"action": "login", "timestamp": "2024-01-01"}]
        filename = "event_log_2"
        store_event_log(user_id, event_log, filename)

        # Get informtion on all event logs with user_id = 123
        logs = get_all_stored_event_log_information(user_id)

        # Check that the number of logs is correct
        self.assertEqual(len(logs), 2, "The number of event logs should be 2.")

        # Check the content of each log
        log_1 = logs[0]
        self.assertEqual(log_1["event_log_id"], 1)
        self.assertEqual(log_1["filename"], "event_log_1")

        log_2 = logs[1]
        self.assertEqual(log_2["event_log_id"], 2)
        self.assertEqual(log_2["filename"], "event_log_2")


if __name__ == "__main__":
    unittest.main()
