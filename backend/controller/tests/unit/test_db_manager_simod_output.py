"""
Unit tests for the DBManagerSimodOutput class.
"""

import unittest
from unittest.mock import MagicMock

from src.db_managers.db_manager_simod_output import DBManagerSimodOutput


class TestDBManagerSimodOutput(unittest.TestCase):
    """
    Unit tests for the DBManagerSimodOutput class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.db_manager = DBManagerSimodOutput()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.db_manager.get_connection = MagicMock(return_value=self.mock_conn)

    def test_upload_simod_output_success(self):
        """
        Test the upload_simod_output method when the upload is successful.
        """
        scenario_id = 1
        filename = "output.csv"
        output_data = b"data"
        self.mock_cursor.fetchone.return_value = (1,)
        result = self.db_manager.upload_simod_output(scenario_id, filename, output_data)

        self.assertTrue(result)

    def test_get_simod_output_success(self):
        """
        Test the get_simod_output method when the output is found.
        """
        scenario_id = 1
        mock_data = {"simod_scenario_id": scenario_id, "filename": "output.csv", "output_data": b"data"}
        self.mock_cursor.fetchone.return_value = mock_data

        self.mock_cursor.__enter__.return_value = self.mock_cursor

        result = self.db_manager.get_simod_output(scenario_id)
        expected = ("output.csv", b"data")
        self.assertEqual(result, expected)
        self.mock_cursor.execute.assert_called_with(
            """
                    SELECT simod_scenario_id, filename, output_data
                    FROM simod_outputs
                    WHERE simod_scenario_id = %s
                    """,
            (scenario_id,),
        )
        self.mock_conn.close.assert_called_once()

    def test_update_simod_output(self):
        """
        Test the update_simod_output method when the update is successful.
        """
        scenario_id = 1
        filename = "output"
        output_data = b"data"
        self.mock_cursor.rowcount = 1

        self.mock_cursor.__enter__.return_value = self.mock_cursor
        result = self.db_manager.update_simod_output(scenario_id, filename, output_data)
        self.assertEqual(result, 1)
        self.mock_cursor.execute.assert_called_with(
            """
                    UPDATE simod_outputs
                    SET filename = %s, output_data = %s
                    WHERE simod_scenario_id = %s
                    """,
            (
                filename,
                output_data,
                scenario_id,
            ),
        )
        self.mock_conn.close.assert_called_once()

    def test_delete_simod_output_success(self):
        """
        Test the delete_simod_output method when the deletion is successful.
        """
        scenario_id = 1
        self.mock_cursor.rowcount = 1
        self.mock_cursor.__enter__.return_value = self.mock_cursor
        result = self.db_manager.delete_simod_output(scenario_id)
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_with(
            """
                    DELETE FROM simod_outputs
                    WHERE simod_scenario_id = %s
                    """,
            (scenario_id,),
        )
        self.mock_conn.close.assert_called_once()

    def test_delete_simod_output_fail(self):
        """
        Test the delete_simod_output method when the deletion fails.
        """
        scenario_id = 1
        self.mock_cursor.rowcount = 0
        self.mock_cursor.__enter__.return_value = self.mock_cursor
        result = self.db_manager.delete_simod_output(scenario_id)
        self.assertFalse(result)
        self.mock_cursor.execute.assert_called_with(
            """
                    DELETE FROM simod_outputs
                    WHERE simod_scenario_id = %s
                    """,
            (scenario_id,),
        )
        self.mock_conn.close.assert_called_once()
