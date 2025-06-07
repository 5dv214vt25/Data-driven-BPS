"""
Unit tests for the DBManagerAgentScenarios class.
"""

import pytest
from src.db_managers.db_manager_agent_scenarios import DBManagerAgentScenarios


class DummyCursor:
    """
    A dummy cursor class to simulate
    database operations for testing purposes.
    """

    def __init__(self, rows=None, row=None, raise_on_execute=False):
        self._rows = rows
        self._row = row
        self._raise = raise_on_execute
        self.rowcount = len(rows) if rows is not None else (1 if row is not None else 0)

    def execute(self, query, params):
        if self._raise:
            raise RuntimeError("simulated failure")

    def fetchall(self):
        return self._rows or []

    def fetchone(self):
        return self._row

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def close(self):
        pass


class DummyConn:
    """
    A dummy connection class to simulate
    database connection for testing purposes.
    """

    def __init__(self, cursor: DummyCursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self, cursor_factory=None):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


@pytest.fixture
def db_mgr():
    return DBManagerAgentScenarios()


def test_upload_agent_scenario_success(monkeypatch, db_mgr):
    """
    Test that upload_agent_scenario returns correct id on success.
    """
    dummy_cursor = DummyCursor(row=(5,))
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    data = {
        "event_log_id": 1,
        "name": "scenario1",
        "model_pkl": b"mp",
        "param_json": b"pj",
        "visualization_json": b"vj",
    }
    result = db_mgr.upload_agent_scenario(data)
    assert result == 5
    assert dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_upload_agent_scenario_no_return(monkeypatch, db_mgr):
    """
    Test that upload_agent_scenario returns an error dict
    if no ID is returned.
    """
    dummy_cursor = DummyCursor(row=None)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    data = {
        "event_log_id": 2,
        "name": "scenario2",
        "model_pkl": b"",
        "param_json": b"",
        "visualization_json": b"",
    }
    result = db_mgr.upload_agent_scenario(data)
    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "Scenario not uploaded" in result["message"]


def test_list_agent_scenarios_returns_correct_information(monkeypatch, db_mgr):
    """
    Test that list_agent_scenarios returns a list of dicts
    containing id, event_log_id, name, and event_log_name.
    """
    rows = [
        (10, 5, "A", "logA"),
        (11, 5, "B", "logB"),
    ]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.list_agent_scenarios(user_id=1)
    expected = [
        {"id": 10, "event_log_id": 5, "name": "A", "event_log_name": "logA"},
        {"id": 11, "event_log_id": 5, "name": "B", "event_log_name": "logB"},
    ]
    assert result == expected
    assert not dummy_conn.committed


def test_get_agent_scenario_found(monkeypatch, db_mgr):
    """
    Test that get_agent_scenario returns a full dict
    when the scenario is found.
    """
    row = (2, 3, "X", b"mp", b"pj", b"vj")
    dummy_cursor = DummyCursor(row=row)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.get_agent_scenario(id=2)
    expected = {
        "id": 2,
        "event_log_id": 3,
        "name": "X",
        "model_pkl": b"mp",
        "param_json": b"pj",
        "visualization_json": b"vj",
    }
    assert result == expected
    assert not dummy_conn.committed


def test_get_agent_scenario_not_found(monkeypatch, db_mgr):
    """
    Test that get_agent_scenario returns an error tuple
    when no scenario matches the given ID.
    """
    dummy_cursor = DummyCursor(row=None)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.get_agent_scenario(id=8)
    assert isinstance(result, tuple)
    error, status = result
    assert status == 404
    assert error.get("status") == "error"
    assert "Scenario not found" in error.get("message", "")


def test_update_agent_scenario_success(monkeypatch, db_mgr):
    """
    Test that update_agent_scenario commits and returns the ID
    when updating name and/or param_json succeeds.
    """
    dummy_cursor = DummyCursor(row=(20,))
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.update_agent_scenario(20, name="both", param_json=b"pj")
    assert result == 20
    assert dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_update_agent_scenario_no_params(monkeypatch, db_mgr):
    """
    Test that update_agent_scenario returns a 400 error tuple
    when no update parameters are provided.
    """
    dummy_cursor = DummyCursor()
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    response = db_mgr.update_agent_scenario(10)
    assert isinstance(response, tuple)
    error, status = response
    assert status == 400
    assert "No update parameters provided" in error.get("message", "")
    assert not dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_update_agent_scenario_not_found(monkeypatch, db_mgr):
    """
    Test that update_agent_scenario rolls back and returns a 404 error tuple
    when the scenario ID does not exist.
    """
    dummy_cursor = DummyCursor(row=None)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    response = db_mgr.update_agent_scenario(42, name="nope")
    assert isinstance(response, tuple)
    error, status = response
    assert status == 404
    assert "Scenario not found" in error.get("message", "")
    assert dummy_conn.rolled_back
    assert not dummy_conn.committed


def test_delete_agent_scenario_success(monkeypatch, db_mgr):
    """
    Test that delete_agent_scenario commits and returns a success dict
    when deletion succeeds.
    """
    dummy_cursor = DummyCursor(row=(5,))
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.delete_agent_scenario(id=5)
    assert isinstance(result, dict)
    assert result.get("status") == "success"
    assert dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_delete_agent_scenario_not_found(monkeypatch, db_mgr):
    """
    Test that delete_agent_scenario returns an error dict
    when no scenario matches the given ID.
    """
    dummy_cursor = DummyCursor(row=None)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.delete_agent_scenario(id=5)
    assert isinstance(result, dict)
    assert result.get("status") == "error"
    assert "not found" in result.get("message", "").lower()
