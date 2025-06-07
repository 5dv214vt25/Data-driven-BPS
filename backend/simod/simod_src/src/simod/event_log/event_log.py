from pathlib import Path
from typing import Optional

import pandas as pd
import pendulum
from openxes_cli.lib import csv_to_xes
from pix_framework.io.event_log import DEFAULT_XES_IDS
from pix_framework.io.event_log import EventLogIDs
from pix_framework.io.event_log import read_csv_log
from pix_framework.io.event_log import split_log_training_validation_trace_wise as split_log

from ..settings.preprocessing_settings import PreprocessingSettings
from ..utilities import get_process_name_from_log_path
from .preprocessor import Preprocessor


class EventLog:
    """
    Represents an event log containing process execution data and its partitioned subsets.

    This class provides functionality for storing and managing an event log, including
    training, validation, and test partitions. It also supports exporting logs to XES format
    and loading event logs from files.

    Attributes
    ----------
    train_partition : :class:`pandas.DataFrame`
        DataFrame containing the training partition of the event log.
    validation_partition : :class:`pandas.DataFrame`
        DataFrame containing the validation partition of the event log.
    train_validation_partition : :class:`pandas.DataFrame`
        DataFrame containing both training and validation data.
    test_partition : :class:`pandas.DataFrame`
        DataFrame containing the test partition of the event log, if available.
    log_ids : :class:`EventLogIDs`
        Identifiers for mapping column names in the event log.
    process_name : str
        The name of the business process associated with the event log, primarily used for file naming.
    """

    train_partition: pd.DataFrame
    validation_partition: pd.DataFrame
    train_validation_partition: pd.DataFrame
    test_partition: pd.DataFrame
    log_ids: EventLogIDs
    process_name: str  # a name of the process that is used mainly for file names

    def __init__(
        self,
        log_train: pd.DataFrame,
        log_validation: pd.DataFrame,
        log_train_validation: pd.DataFrame,
        log_test: pd.DataFrame,
        log_ids: EventLogIDs,
        process_name: Optional[str] = None,
    ):
        self.train_partition = log_train
        self.validation_partition = log_validation
        self.train_validation_partition = log_train_validation
        self.test_partition = log_test
        self.log_ids = log_ids

        if process_name is not None:
            self.process_name = process_name
        else:
            self.process_name = "business_process"

    @staticmethod
    def from_path(
        train_log_path: Path,
        log_ids: EventLogIDs,
        preprocessing_settings: PreprocessingSettings = PreprocessingSettings(),
        need_test_partition: Optional[bool] = False,
        process_name: Optional[str] = None,
        test_log_path: Optional[Path] = None,
        split_ratio: float = 0.8,
    ) -> "EventLog":
        """
        Loads an event log from a file and performs partitioning into training, validation, and test subsets.

        Parameters
        ----------
        train_log_path : :class:`pathlib.Path`
            Path to the training event log file (CSV or CSV.GZ).
        log_ids : :class:`EventLogIDs`
            Identifiers for mapping column names in the event log.
        preprocessing_settings : :class:`PreprocessingSettings`, optional
            Settings for preprocessing the event log.
        need_test_partition : bool, optional
            Whether to create a test partition if a separate test log is not provided.
        process_name : str, optional
            Name of the business process. If not provided, it is inferred from the file name.
        test_log_path : :class:`pathlib.Path`, optional
            Path to the test event log file (CSV or CSV.GZ). If provided, the test log is loaded separately.
        split_ratio : float, default=0.8
            Ratio for splitting training and validation partitions.

        Returns
        -------
        :class:`EventLog`
            An instance of :class:`EventLog` with training, validation, and test partitions.

        Raises
        ------
        ValueError
            If the specified training or test log has an unsupported file extension.
        """
        # Check event log prerequisites
        if not train_log_path.name.endswith(".csv") and not train_log_path.name.endswith(".csv.gz"):
            raise ValueError(
                f"The specified training log has an unsupported extension ({train_log_path.name}). "
                f"Only 'csv' and 'csv.gz' supported."
            )
        if test_log_path is not None:
            if not test_log_path.name.endswith(".csv") and not test_log_path.name.endswith(".csv.gz"):
                raise ValueError(
                    f"The specified test log has an unsupported extension ({test_log_path.name}). "
                    f"Only 'csv' and 'csv.gz' supported."
                )

        # Read training event log
        event_log = read_csv_log(train_log_path, log_ids)

        # Preprocess training event log
        preprocessor = Preprocessor(event_log, log_ids)
        processed_event_log = preprocessor.run(
            multitasking=preprocessing_settings.multitasking,
            enable_time_concurrency_threshold=preprocessing_settings.enable_time_concurrency_threshold,
            concurrency_thresholds=preprocessing_settings.concurrency_thresholds,
        )

        # Get test if needed, and split train+validation
        if test_log_path is not None:
            # Test log provided, the input log is train+validation
            train_validation_df = processed_event_log
            test_df = read_csv_log(test_log_path, log_ids)
        elif need_test_partition:
            # Test log not provided but needed, split input into test and train+validation
            train_validation_df, test_df = split_log(processed_event_log, log_ids, training_percentage=split_ratio)
        else:
            # Test log not provided and not needed, the input log is train+validation
            train_validation_df = processed_event_log
            test_df = None
        train_df, validation_df = split_log(train_validation_df, log_ids, training_percentage=split_ratio)

        # Return EventLog instance with different partitions
        return EventLog(
            log_train=train_df,
            log_validation=validation_df,
            log_train_validation=train_validation_df,
            log_test=test_df,
            log_ids=log_ids,
            process_name=get_process_name_from_log_path(train_log_path) if process_name is None else process_name,
        )

    def train_to_xes(self, path: Path, only_complete_events: bool = False):
        """
        Saves the training log to an XES file.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Destination path for the XES file.
        only_complete_events : bool
            If true, generate XES file containing only events corresponding to
            the end of each activity instance.
        """
        write_xes(self.train_partition, self.log_ids, path, only_complete_events=only_complete_events)

    def validation_to_xes(self, path: Path, only_complete_events: bool = False):
        """
        Saves the validation log to an XES file.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Destination path for the XES file.
        only_complete_events : bool
            If true, generate XES file containing only events corresponding to
            the end of each activity instance.
        """
        write_xes(self.validation_partition, self.log_ids, path, only_complete_events=only_complete_events)

    def train_validation_to_xes(self, path: Path, only_complete_events: bool = False):
        """
        Saves the combined training and validation log to an XES file.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Destination path for the XES file.
        only_complete_events : bool
            If true, generate XES file containing only events corresponding to
            the end of each activity instance.
        """
        write_xes(self.train_validation_partition, self.log_ids, path, only_complete_events=only_complete_events)

    def test_to_xes(self, path: Path, only_complete_events: bool = False):
        """
        Saves the test log to an XES file.

        Parameters
        ----------
        path : :class:`pathlib.Path`
            Destination path for the XES file.
        only_complete_events : bool
            If true, generate XES file containing only events corresponding to
            the end of each activity instance.
        """
        write_xes(self.test_partition, self.log_ids, path, only_complete_events=only_complete_events)


def write_xes(
    event_log: pd.DataFrame,
    log_ids: EventLogIDs,
    output_path: Path,
    only_complete_events: bool = False,
):
    """
    Writes the log to a file in XES format.
    """
    # Copy event log to modify
    df = event_log.copy()
    # Transform timestamps to expected format
    xes_datetime_format = "YYYY-MM-DDTHH:mm:ss.SSSZ"
    # Start time
    if only_complete_events:
        df[log_ids.start_time] = ""
    else:
        df[log_ids.start_time] = df[log_ids.start_time].apply(
            lambda x: pendulum.parse(x.isoformat()).format(xes_datetime_format)
        )
    # End time
    df[log_ids.end_time] = df[log_ids.end_time].apply(
        lambda x: pendulum.parse(x.isoformat()).format(xes_datetime_format)
    )
    # Rename columns to XES expected
    df = df.rename(
        columns={
            log_ids.activity: "concept:name",
            log_ids.case: "case:concept:name",
            log_ids.resource: "org:resource",
            log_ids.start_time: "start_timestamp",
            log_ids.end_time: "time:timestamp",
        }
    )[
        [
            "case:concept:name",
            "concept:name",
            "org:resource",
            "start_timestamp",
            "time:timestamp",
        ]
    ]
    # Fill null values
    df.fillna("UNDEFINED", inplace=True)
    # Write and convert
    df.to_csv(output_path, index=False)
    csv_to_xes(output_path, output_path)
