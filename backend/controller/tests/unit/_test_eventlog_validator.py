"""
Unit tests for the eventlog_validator.py file.
"""

import pandas as pd
from src.eventlog_validator import validate_eventlog_format


def test_validate_correct_eventlog():
    """
    Test the validate_eventlog_format function with a correct event log.
    """
    data = {
        "activity": [
            "Check application form completeness",
            "Check application form completeness",
            "Check credit history",
            "Check credit history",
        ],
        "case_id": [0, 0, 1, 1],
        "start_time": [
            "2023-02-09T09:04:40.802",
            "2023-02-09T09:04:40.802",
            "2023-02-09T09:04:40.802",
            "2023-02-09T09:04:40.802",
        ],
        "resource": ["Clerk-000001", "Clerk-000001", "Clerk-000002", "Clerk-000002"],
        "end_time": [
            "2023-02-09T09:04:40.802",
            "2023-02-09T09:04:40.802",
            "2023-02-09T09:04:40.802",
            "2023-02-09T09:04:40.802",
        ],
    }
    df = pd.DataFrame(data)

    assert validate_eventlog_format(df) is True
