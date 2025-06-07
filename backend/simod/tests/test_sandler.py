import pandas as pd
import pytest
from src.sandler import Sandler


@pytest.fixture
def mock_event_log():
    """
    Returns a short mocked eventlog as a pandas dataframe.
    """
    data = {
        "case_id": ["Case1", "Case1", "Case2"],
        "resource": ["res1", "res2", "res1"],
        "activity": ["act1", "act2", "act1"],
        "start_time": ["2012/01/01 00:00:00", "2012/02/02 00:00:00", "2012/03/03 00:00:00"],
        "end_time": ["2012/01/01 00:01:00", "2012/02/02 00:01:00", "2012/03/03 00:01:00"],
    }
    mock_dataframe = pd.DataFrame(data)

    return mock_dataframe


def test_create_sandler():
    """
    Test the creation of a sandler object.
    """
    test_sandler = Sandler()
    assert test_sandler is not None


def test_sandler_creates_folder():
    """
    Test the creation of a sandler object's folder.
    """
    test_sandler = Sandler()
    assert test_sandler._Sandler__output_path.exists()


def test_sandler_cleanup():
    """
    Test that the cleanup method removes the output directory.
    """
    test_sandler = Sandler()
    assert test_sandler._Sandler__output_path.exists()
    test_sandler.cleanup()
    assert not test_sandler._Sandler__output_path.exists()
