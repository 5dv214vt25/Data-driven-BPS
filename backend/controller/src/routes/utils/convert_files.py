"""
This file contains the functions for converting files to different formats.
It is used to convert XES files to CSV files and vice versa.
"""

import tempfile
from io import BytesIO
from io import StringIO

import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils


def convert_to_csv(xes_bytes):
    """
    Convert a XES file to a CSV file.

    Limitations:
        Can only convert xes files with the same number of start and complete events
        and each start event must be directly followed by its complete event.

    Args:
        xes_bytes (bytes): The XES file to convert.

    Returns:
        bytes: The file in CSV format.
    """

    # Create a temporary file to store the XES bytes
    with tempfile.NamedTemporaryFile(suffix=".xes", delete=False) as temp_file:
        temp_file.write(xes_bytes)
        temp_file_path = temp_file.name

    # Parse XES from bytes
    log = pm4py.read_xes(temp_file_path)

    # Convert the event log to a DataFrame
    df = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    # Ensure correct timestamp format
    df = dataframe_utils.convert_timestamp_columns_in_df(df)

    # Rename XES-specific column names
    df.rename(
        columns={"case:concept:name": "case_id", "concept:name": "activity", "org:resource": "resource"}, inplace=True
    )

    # Sort by case_id and timestamp to maintain order
    df_sorted = df.sort_values(by=["case_id", "time:timestamp"])

    # Filter start and complete events
    starts = df_sorted[df_sorted["lifecycle:transition"] == "start"].copy()
    completes = df_sorted[df_sorted["lifecycle:transition"] == "complete"].copy()

    # Reset index to align rows
    starts.reset_index(drop=True, inplace=True)
    completes.reset_index(drop=True, inplace=True)

    # Check that starts and completes match in number
    if len(starts) != len(completes):
        raise Exception()

    # Combine start and complete rows
    paired_df = starts[["case_id", "activity", "resource", "time:timestamp"]].copy()
    paired_df.rename(columns={"time:timestamp": "start_time"}, inplace=True)
    paired_df["end_time"] = completes["time:timestamp"]

    # Fill any empty resources
    paired_df["resource"] = paired_df["resource"].fillna("NOT_SET")

    # Convert DataFrame to CSV in memory
    csv_buffer = StringIO()
    paired_df.to_csv(csv_buffer, index=False)

    # Get the CSV as bytes
    return csv_buffer.getvalue().encode("utf-8")


def convert_to_xes(df):
    """
    Convert a CSV file to a XES file.

    Args:
        df (DataFrame): The CSV file to convert.

    Returns:
        bytes: The file in XES format.
    """
    event_log = df
    event_log = pm4py.format_dataframe(
        event_log,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="end_time",
        start_timestamp_key="start_time",
    )
    log = pm4py.convert_to_event_log(event_log)

    # Export the log to a temporary XES file
    pm4py.write_xes(log, "temp.xes")

    # Read the file as bytes
    with open("temp.xes", "rb") as xes_file:
        xes_bytes = BytesIO(xes_file.read())

    return xes_bytes.getvalue()
