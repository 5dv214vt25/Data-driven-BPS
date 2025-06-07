"""
This file contains the function for validating the eventlog format.
It is used to validate the eventlog format before it is uploaded to the database.
"""

# Imported modules from packages
from datetime import datetime

# Helper function for validating if a csv file is correct format.
# Function needs a csv file that is converted into a dataframe using pd.read_csv


def validate_eventlog_format(df):
    """Validates headers and format of column values in the eventlog

    Keyword arguments:
    df -- The eventlog converted to a DataFrame object

    Returns:
        Response: Boolean if the eventlog is valid or not
    """
    current_headers = list(df)

    # Check that the headers are valid
    correct_headers = ["case_id", "resource", "activity", "start_time", "end_time"]
    if not all(header in current_headers for header in correct_headers):
        return "Matching Headers: FAIL"

    # Check that all columns has correct formated values
    failed_columns = list()

    list_1 = df["case_id"].tolist()
    for val in list_1:
        if (isinstance(val, str) or isinstance(val, int)) is not True:
            failed_columns.append("case_id")
            break

    list_2 = df["resource"].tolist()
    for val in list_2:
        if isinstance(val, str) is not True:
            failed_columns.append("resource")
            break

    list_3 = df["activity"].tolist()
    for val in list_3:
        if isinstance(val, str) is not True:
            failed_columns.append("activity")
            break

    list_4 = df["start_time"].tolist()
    for val in list_4:
        if isinstance(val, str) is not True:
            failed_columns.append("start_time")
            break

    list_5 = df["end_time"].tolist()
    for val in list_5:
        if isinstance(val, str) is not True:
            failed_columns.append("end_time")
            break
    if len(failed_columns) > 0:
        message = ("Failed Columns: ", failed_columns)
        print("from funciton")
        print(message)
        return message
    else:
        print("Eventlog is valid!")
        return True


def datetime_valid(dt_str):
    """Validates if a date is in ISO format

    Keyword arguments:
    dt_str -- The date as a string

    Returns:
        Response: Boolean if the date is in ISO format
    """
    try:
        datetime.fromisoformat(dt_str)
    except ValueError:
        return False
    return True
