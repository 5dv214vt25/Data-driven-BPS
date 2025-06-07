"""
Unit tests for the database manager functionality.
"""

import unittest
from io import BytesIO
from unittest.mock import MagicMock
from unittest.mock import patch

from src.db_manager import clear_database
from src.db_manager import get_all_stored_event_log_information
from src.db_manager import get_event_log
from src.db_manager import store_event_log


class TestDBManager(unittest.TestCase):
    """Test cases for database manager functions."""

    @patch("src.simulated_db.clear_database")
    def setUp(self, mock_clear):
        """Set up the test environment before each test.

        Clears the database to ensure each test runs with a clean state.
        """
        # Clear the database before each test
        clear_database()
        mock_clear.assert_called_once()

    @patch("src.simulated_db.store_event_log")
    def test_store_event_log(self, mock_store):
        """Test storing an event log file.

        Verifies that store_event_log correctly reads from a file-like object
        and passes the content to the simulated database.
        """
        # Create a mock file-like object
        csv_content = "timestamp,action\n2024-01-01,login"
        mock_file = MagicMock()
        mock_file.read.return_value = csv_content.encode("utf-8")
        filename = "event_log_1"

        # Set up the mock to return True
        mock_store.return_value = 1

        # Call the function
        result = store_event_log(123, mock_file, filename)

        # Verify the result and that the mock was called correctly
        mock_file.read.assert_called_once()
        mock_store.assert_called_once_with(123, csv_content, filename)
        self.assertEqual(result, 1)

    @patch("src.simulated_db.get_event_log")
    def test_get_event_log_success(self, mock_get):
        """Test successful retrieval of an event log.

        Verifies that get_event_log correctly retrieves data from the simulated database
        and returns it as a BytesIO object.
        """
        # Set up the mock to return sample data
        csv_content = "timestamp,action\n2024-01-01,login"
        mock_get.return_value = {
            "event_log": csv_content,
            "filename": "event_log.csv",
        }

        # Call the function
        filename, result = get_event_log(123, 321)

        # Verify the result
        self.assertEqual(filename, "event_log.csv")
        self.assertIsInstance(result, BytesIO)
        self.assertEqual(result.read().decode("utf-8"), csv_content)
        mock_get.assert_called_once_with(123, 321)

    @patch("src.simulated_db.get_event_log")
    def test_get_event_log_not_found(self, mock_get):
        """Test retrieval of a non-existent event log.

        Verifies that get_event_log returns None when the requested log
        is not found in the database.
        """
        # Set up the mock to return None (log not found)
        mock_get.return_value = None

        # Call the function
        result = get_event_log(123, 321)

        # Verify the result
        self.assertIsNone(result)
        mock_get.assert_called_once_with(123, 321)

    @patch("src.simulated_db.clear_database")
    def test_clear_database(self, mock_clear):
        """Test clearing the database.

        Verifies that clear_database correctly calls the underlying
        database clearing function and returns a success message.
        """
        # Call the function
        result = clear_database()

        # Verify the result
        self.assertEqual(result, "Database cleared successfully.")
        mock_clear.assert_called_once()

    @patch("src.simulated_db.get_all_stored_event_log_information")
    def test_get_all_stored_event_log_information(self, mock_get_all):
        """Tests getting all information in given a user id.

        Verifies that get_all_stored_event_log_information() retuns correct information
        regarding what is stored in the database
        """
        # Setup test data
        test_user_id = "123"
        mock_data = [
            {
                "event_log_id": 1,
                "filename": "log1.csv",
            },
            {
                "event_log_id": 2,
                "filename": "log2.csv",
            },
        ]

        # Configure mock to return our test data
        mock_get_all.return_value = mock_data

        # Call the function
        result = get_all_stored_event_log_information(test_user_id)

        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["event_log_id"], 1)
        self.assertEqual(result[0]["filename"], "log1.csv")
        self.assertEqual(result[1]["event_log_id"], 2)
        self.assertEqual(result[1]["filename"], "log2.csv")

        # Verify mock was called correctly
        mock_get_all.assert_called_once_with(test_user_id)


if __name__ == "__main__":
    unittest.main()
