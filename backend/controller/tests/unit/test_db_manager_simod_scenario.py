"""
Unit tests for the DBManagerSimodScenario class.
"""

import unittest
from unittest.mock import MagicMock

import psycopg2
from src.db_managers.db_manager_simod_scenarios import DBManagerSimodScenario


class TestDBManagerSimosScenario(unittest.TestCase):
    """
    Unit tests for the DBManagerSimodScenario class.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.db_manager = DBManagerSimodScenario()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.db_manager.get_connection = MagicMock(return_value=self.mock_conn)

    def test_list_simod_scenarios_error(self):
        """
        Test the list_simod_scenarios method when an error occurs.
        """
        user_id = "user"
        self.mock_cursor.execute.side_effect = psycopg2.Error("DB error")
        result = self.db_manager.list_simod_scenarios(user_id)
        self.assertEqual(result, [])
        self.mock_conn.close.assert_called_once()

    def test_get_simod_scenario_success(self):
        """
        Test the get_simod_scenario method when the scenario is found.
        """
        scenario_id = 1
        mock_data = (1, "Scenario1", 101, b"bpmn_data", b"param_data")
        self.mock_cursor.fetchone.return_value = mock_data

        result = self.db_manager.get_simod_scenario(scenario_id)

        expected = {
            "id": 1,
            "name": "Scenario1",
            "event_log_id": 101,
            "file_bpmn": b"bpmn_data",
            "param_json": b"param_data",
        }
        self.assertEqual(result, expected)
        self.mock_cursor.execute.assert_called_with(
            "SELECT id, name, event_log_id, file_bpmn, param_json FROM simod_scenarios WHERE id = %s;",
            (scenario_id,),
        )

    def test_get_simod_scenario_not_found(self):
        """
        Test the get_simod_scenario method when the scenario is not found.
        """
        scenario_id = 1
        self.mock_cursor.fetchone.return_value = None

        result = self.db_manager.get_simod_scenario(scenario_id)

        self.assertEqual(result, ({"error": "Scenario not found"}, 404))

    def test_create_simod_scenario_success(self):
        """
        Test the create_simod_scenario method when the creation is successful.
        """
        data = {"event_log_id": 1, "name": "scenario", "file_bpmn": b"bpmn_data", "param_json": b"param_data"}
        self.mock_cursor.fetchone.return_value = (1,)

        result = self.db_manager.create_simod_scenario(data)

        self.assertEqual(result, 1)

    def test_update_simod_scenario_success(self):
        """
        Test the update_simod_scenario method when the update is successful.
        """
        scenario_id = 1
        name = "updated_scenario"
        self.mock_cursor.fetchone.return_value = (1,)

        result = self.db_manager.update_simod_scenario(scenario_id, name)
        self.assertEqual(result, 1)
        self.mock_cursor.execute.assert_called_with(
            "UPDATE simod_scenarios SET name = %s WHERE id = %s RETURNING id", (name, scenario_id)
        )

    def test_delete_simod_scenario_success(self):
        """
        Test the delete_simod_scenario method when the deletion is successful.
        """
        scenario_id = 1
        self.mock_cursor.fetchone.return_value = (0,)

        result = self.db_manager.delete_simod_scenario(scenario_id)

        self.assertEqual(result, {"message": "Scenario deleted successfully"})
        self.mock_cursor.execute.assert_any_call("DELETE FROM simod_scenarios WHERE id = %s", (scenario_id,))

    def test_delete_simod_scenario_fail(self):
        """
        Test the delete_simod_scenario method when the deletion fails.
        """
        scenario_id = 1
        self.mock_cursor.fetchone.return_value = (1,)

        result = self.db_manager.delete_simod_scenario(scenario_id)

        self.assertEqual(result, {"message": "Scenario deletion failed", "error": "Record still exists"})
