"""
Unit tests for the DBManagerAgentOutput class.
"""

import pytest
from src.db_managers.db_manager_agent_output import DBManagerAgentOutput


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
    return DBManagerAgentOutput()


def test_list_agent_outputs_returns_correct_information(monkeypatch, db_mgr):
    """
    Test that list_agent_outputs returns a list of dicts
    containing agent_scenario_id, output_filename, scenario_name,
    event_log_id, and event_log_name.
    """
    rows = [
        {
            "agent_scenario_id": 10,
            "filename": "outA.txt",
            "scenario_name": "Scenario A",
            "event_log_id": 5,
            "event_log_name": "logA",
        },
        {
            "agent_scenario_id": 11,
            "filename": "outB.txt",
            "scenario_name": "Scenario B",
            "event_log_id": 6,
            "event_log_name": "logB",
        },
    ]
    dummy_cursor = DummyCursor(rows=rows)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.list_agent_outputs(user_id=1)
    expected = [
        {
            "agent_scenario_id": 10,
            "output_filename": "outA.txt",
            "scenario_name": "Scenario A",
            "event_log_id": 5,
            "event_log_name": "logA",
        },
        {
            "agent_scenario_id": 11,
            "output_filename": "outB.txt",
            "scenario_name": "Scenario B",
            "event_log_id": 6,
            "event_log_name": "logB",
        },
    ]
    assert result == expected
    assert not dummy_conn.committed


def test_get_agent_output_not_found_prints_and_returns_none(monkeypatch, capsys, db_mgr):
    """
    Test that get_agent_output returns None and prints a not-found message when absent.
    """
    dummy_cursor = DummyCursor(row=None)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.get_agent_output(agent_scenario_id=999)
    captured = capsys.readouterr()
    assert result is None
    assert "Agent output 999 not found." in captured.out
    assert not dummy_conn.committed


def test_get_agent_output_returns_filename_and_bytes(monkeypatch, db_mgr):
    """
    Test that get_agent_output returns the filename and raw bytes exactly as stored.
    """
    row = {"agent_scenario_id": 3, "filename": "c.csv", "output_data": b"hello,world\n42,24\n"}
    dummy_cursor = DummyCursor(row=row)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.get_agent_output(agent_scenario_id=3)
    assert isinstance(result, tuple) and len(result) == 2
    filename, data = result
    assert filename == "c.csv"
    assert isinstance(data, (bytes, bytearray))
    assert data == b"hello,world\n42,24\n"
    assert not dummy_conn.committed


def test_upload_agent_output_commits_and_returns_true(monkeypatch, db_mgr):
    """
    Test that the create_agent_output method commits the transaction and returns true.
    """
    dummy_cursor = DummyCursor(row=(42,))
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.upload_agent_output(10, "c.csv", b"data")
    assert result is True
    assert dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_update_agent_output_rowcount_and_commits(monkeypatch, db_mgr):
    """
    Test that the update_agent_output method returns the correct rowcount.
    """
    dummy_cursor = DummyCursor(row=(None,))
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    count = db_mgr.update_agent_output(10, "c.csv", b"data")
    assert count == 1
    assert dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_delete_commits(monkeypatch, db_mgr):
    """
    Test that the delete_specific_agent_output method commits the transaction.
    """
    dummy_cursor = DummyCursor(row=(None,))
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.delete_agent_output(10)
    assert result is True
    assert dummy_conn.committed
    assert not dummy_conn.rolled_back


def test_delete_handles_exceptions(monkeypatch, db_mgr):
    """
    Test that the delete_specific_agent_output method handles exceptions correctly.
    """
    dummy_cursor = DummyCursor(raise_on_execute=True)
    dummy_conn = DummyConn(dummy_cursor)
    monkeypatch.setattr(db_mgr, "get_connection", lambda: dummy_conn)

    result = db_mgr.delete_agent_output(10)
    assert result is False
    assert dummy_conn.rolled_back
    assert not dummy_conn.committed
