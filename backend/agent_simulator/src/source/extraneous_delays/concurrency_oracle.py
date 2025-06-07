import enum
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from dataclasses import field

import pandas as pd
import polars as pl
from source.extraneous_delays.event_log import DEFAULT_CSV_IDS
from source.extraneous_delays.event_log import EventLogIDs


class ReEstimationMethod(enum.Enum):
    SET_INSTANT = 1
    MODE = 2
    MEDIAN = 3
    MEAN = 4


class OutlierStatistic(enum.Enum):
    MODE = 1
    MEDIAN = 2
    MEAN = 3


class ConcurrencyOracleType(enum.Enum):
    DEACTIVATED = 1
    DF = 2
    ALPHA = 3
    HEURISTICS = 4
    OVERLAPPING = 5


class ResourceAvailabilityType(enum.Enum):
    SIMPLE = 1  # Consider all the events that each resource performs
    WITH_CALENDAR = 2  # Future possibility considering also the resource calendars and non-working days


@dataclass
class ConcurrencyThresholds:
    df: float = 0.9
    l2l: float = 0.9
    l1l: float = 0.9


@dataclass
class Configuration:
    """Class storing the configuration parameters for the start time estimation.

    Attributes:
        log_ids                     Identifiers for each key element (e.g. executed activity or resource).
        concurrency_oracle_type     Concurrency oracle to use (e.g. heuristics miner's concurrency oracle).
        resource_availability_type  Resource availability engine to use (e.g. using resource calendars).
        missing_resource            String to identify the events with missing resource (it is avoided in
                                    the resource availability calculation).
        re_estimation_method        Method (e.g. median) to re-estimate the start times that couldn't be
                                    estimated due to lack of resource availability and causal predecessors.
        bot_resources               Set of resource IDs corresponding bots, in order to set their events as
                                    instant.
        instant_activities          Set of instantaneous activities, in order to set their events as instant.
        concurrency_thresholds      Thresholds for the concurrency oracle. The three thresholds [df], [l1l],
                                    and [l2l] are used in the Heuristics oracle. In the overlapping oracle,
                                    only [df] is used.
        reuse_current_start_times   Do not estimate the start times of those activities with already recorded
                                    start time (caution, the instant activities and bot resources will still
                                    be set as instant).
        consider_start_times        Consider start times when checking for the enabled time of an activity in
                                    the concurrency oracle, if 'true', do not consider the events which end
                                    time is after the start time of the current activity instance, they overlap
                                    so no causality between them. In the case of the resource availability, if
                                    'true', search the availability as the previous end before the start of the
                                    current activity, not its end.
        outlier_statistic           Statistic (e.g. median) to calculate the most typical duration from the
                                    distribution of each activity durations to consider and re-estimate the
                                    outlier events which estimated duration is higher.
        outlier_threshold           Threshold to control outliers, those events with estimated durations over
        working_schedules           Dictionary with the resources as key and the working calendars (RCalendar)
                                    as value.
    """

    log_ids: EventLogIDs = field(default_factory=lambda: DEFAULT_CSV_IDS)
    concurrency_oracle_type: ConcurrencyOracleType = ConcurrencyOracleType.HEURISTICS
    resource_availability_type: ResourceAvailabilityType = ResourceAvailabilityType.SIMPLE
    missing_resource: str = "NOT_SET"
    re_estimation_method: ReEstimationMethod = ReEstimationMethod.MEDIAN
    bot_resources: set = field(default_factory=set)
    instant_activities: set = field(default_factory=set)
    concurrency_thresholds: ConcurrencyThresholds = field(default_factory=lambda: ConcurrencyThresholds())
    reuse_current_start_times: bool = False
    consider_start_times: bool = False
    outlier_statistic: OutlierStatistic = OutlierStatistic.MEDIAN
    outlier_threshold: float = float("nan")
    working_schedules: dict = field(default_factory=dict)


class ConcurrencyOracle:
    def __init__(self, concurrency: dict, config: Configuration):
        # Dict with the concurrency: self.concurrency[A] = set of activities concurrent with A
        self.concurrency = concurrency

        self.config = config
        self.log_ids = config.log_ids

    def enabled_since(self, trace: pd.DataFrame, event: pd.Series) -> pd.Timestamp:
        # Get enabling activity instance or NA if none
        enabling_activity_instance = self.enabling_activity_instance(trace, event)
        return enabling_activity_instance[self.log_ids.end_time] if not enabling_activity_instance.empty else pd.NaT

    def enabling_activity_instance(self, trace: pd.DataFrame, event: pd.Series):
        # Get properties of the current event
        event_end_time = event[self.log_ids.end_time]
        event_start_time = event[self.log_ids.start_time]
        event_activity = event[self.log_ids.activity]
        # Get the list of previous end times
        previous_end_times = trace[
            (trace[self.log_ids.end_time] < event_end_time)  # i) previous to the current one; and
            & (
                (not self.config.consider_start_times)  # ii) if parallel check is activated,
                or (trace[self.log_ids.end_time] <= event_start_time)  # not overlapping; and
            )
            & (~trace[self.log_ids.activity].isin(self.concurrency[event_activity]))  # iii) with no concurrency;
        ][self.log_ids.end_time]
        # Get enabling activity instance or empty pd.Series if none
        if not previous_end_times.empty:
            enabling_activity_instance = trace.loc[previous_end_times.idxmax()]
        else:
            enabling_activity_instance = pd.Series()
        # Return the enabling activity instance
        return enabling_activity_instance

    def _get_enabling_info_of_trace(
        self,
        trace: pd.DataFrame,
        log_ids: EventLogIDs,
        set_nat_to_first_event: bool = False,
    ):
        # Initialize lists for indexes, enabled times, and enabling activities of each event in the trace
        indexes, enabled_times, enabling_activities = [], [], []
        # Compute trace start time
        if log_ids.start_time in trace:
            trace_start_time = min(trace[log_ids.start_time].min(), trace[log_ids.end_time].min())
        else:
            trace_start_time = trace[log_ids.end_time].min()
        # Get the enabling activity and enabled time of each event
        for index, event in trace.iterrows():
            indexes += [index]
            enabling_activity_instance = self.enabling_activity_instance(trace, event)
            # Store enabled time
            if enabling_activity_instance.empty:
                # No enabling activity, use trace start or NA
                enabled_times += [pd.NaT] if set_nat_to_first_event else [trace_start_time]
                enabling_activities += [pd.NA]
            else:
                # Use computed value
                enabled_times += [enabling_activity_instance[log_ids.end_time]]
                enabling_activities += [enabling_activity_instance[log_ids.activity]]
        # Return values of all events in trace
        return indexes, enabled_times, enabling_activities

    def add_enabled_times(
        self,
        event_log: pd.DataFrame,
        set_nat_to_first_event: bool = False,
        include_enabling_activity: bool = False,
    ):
        """
        Add the enabled time of each activity instance to the received event log based on the concurrency relations
        established in the class instance (extracted from the event log passed to the instantiation). For the first
        event on each trace, set the start of the trace as value.

        :param event_log:                   event log to add the enabled time information to.
        :param set_nat_to_first_event:      if False, use the start of the trace as enabled time for the activity
                                            instances with no previous activity enabling them, otherwise use pd.NaT.
        :param include_enabling_activity:   if True, add a column with the label of the activity enabling the current
                                            one.
        """
        # Initialize needed columns to 'obj'
        event_log[self.log_ids.enabled_time] = None
        if include_enabling_activity:
            event_log[self.log_ids.enabling_activity] = None
        # Initialize lists to write all enabled times in the log at once
        indexes, enabled_times, enabling_activities = [], [], []
        # Parallelize enabling information extraction by trace
        with ProcessPoolExecutor() as executor:
            # For each trace in the log, estimate the enabled time/activity of its events
            handles = [
                executor.submit(
                    self._get_enabling_info_of_trace,
                    trace=trace,
                    log_ids=self.log_ids,
                    set_nat_to_first_event=set_nat_to_first_event,
                )
                for _, trace in event_log.groupby(self.log_ids.case)
            ]
            # Recover all results
            for handle in handles:
                indexes_, enabled_times_, enabling_activities_ = handle.result()
                indexes += indexes_
                enabled_times += enabled_times_
                enabling_activities += enabling_activities_
        # Update all trace enabled times (and enabling activities if necessary) at once
        if include_enabling_activity:
            event_log.loc[indexes, self.log_ids.enabling_activity] = enabling_activities
        event_log.loc[indexes, self.log_ids.enabled_time] = enabled_times
        event_log[self.log_ids.enabled_time] = pd.to_datetime(event_log[self.log_ids.enabled_time], utc=True)


class OverlappingConcurrencyOracle(ConcurrencyOracle):
    def __init__(self, event_log: pd.DataFrame, config: Configuration):
        # Get the activity labels
        activities = set(event_log[config.log_ids.activity])
        # Get matrix with the frequency of each activity overlapping with the rest and in directly-follows order
        overlapping_relations = _get_overlapping_matrix(event_log, activities, config)
        # Create concurrency if the overlapping relations is higher than the threshold specifies
        concurrency = {activity: set() for activity in activities}
        already_checked = set()
        for act_a in activities:
            # Store as already checked to avoid redundant checks
            already_checked.add(act_a)
            # Get the number of occurrences of A per case
            occurrences_a = Counter(event_log[event_log[config.log_ids.activity] == act_a][config.log_ids.case])
            for act_b in activities - already_checked:
                # Get the number of occurrences of B per case
                occurrences_b = Counter(event_log[event_log[config.log_ids.activity] == act_b][config.log_ids.case])
                # Compute number of times they co-occur
                co_occurrences = sum(
                    [
                        occurrences_a[case_id] * occurrences_b[case_id]
                        for case_id in set(list(occurrences_a.keys()) + list(occurrences_b.keys()))
                    ]
                )
                # Check if the proportion of overlapping occurrences is higher than the established threshold
                if co_occurrences > 0:
                    overlapping_ratio = overlapping_relations[act_a].get(act_b, 0) / co_occurrences
                    if overlapping_ratio >= config.concurrency_thresholds.df:
                        # Concurrency relation AB, add it
                        concurrency[act_a].add(act_b)
                        concurrency[act_b].add(act_a)
        # Set flag to consider start times also when individually checking enabled time
        config.consider_start_times = True
        # Super
        super(OverlappingConcurrencyOracle, self).__init__(concurrency=concurrency, config=config)


def _get_overlapping_matrix(event_log: pd.DataFrame, activities: set, config: Configuration) -> dict:
    """
    Optimized version of _get_overlapping_matrix using Polars.
    """

    ####
    def most_frequent_dtype(column):
        # Count the occurrences of each data type
        dtype_counts = column.apply(type).value_counts()
        # Get the most frequent data type
        most_frequent_dtype = dtype_counts.idxmax()
        return most_frequent_dtype

    # Loop through each column and convert values to the most frequent data type
    for column in event_log.columns:
        # print(column)
        most_common_dtype = most_frequent_dtype(event_log[column])
        # print(most_common_dtype)
        if most_common_dtype != pd.Timestamp:
            event_log[column] = event_log[column].astype(most_common_dtype)
    ####

    # Translate pandas DataFrame to polars DataFrame
    event_log_rs = pl.from_pandas(event_log)
    # Initialize dictionary for overlapping relations df_count[A][B] = number of times B overlaps with A
    overlapping_relations = {activity: {} for activity in activities}
    # Count overlapping relations
    for _, trace in event_log_rs.groupby(config.log_ids.case):
        # For each event in the trace
        for event in trace.iter_rows(named=True):
            event_start_time = event[config.log_ids.start_time]
            event_end_time = event[config.log_ids.end_time]
            event_activity = event[config.log_ids.activity]
            current_activity = event_activity
            # Get labels of overlapping activity instances
            overlapping_labels = trace.filter(
                (
                    (pl.col(config.log_ids.start_time) < event_start_time)  # The current event starts while the other
                    & (event_start_time < pl.col(config.log_ids.end_time))
                )  # is being executed; OR
                | (
                    (pl.col(config.log_ids.start_time) < event_end_time)  # the current event ends while the other
                    & (event_end_time < pl.col(config.log_ids.end_time))
                )  # is being executed; OR
                | (
                    (event_start_time <= pl.col(config.log_ids.start_time))  # the other event starts and
                    & (pl.col(config.log_ids.end_time) <= event_end_time)  # ends within the current one, and
                    & (pl.col(config.log_ids.activity) != event_activity)
                )  # it's not the current one.
            )[config.log_ids.activity].to_list()
            for overlapping_activity in overlapping_labels:
                overlapping_relations[current_activity][overlapping_activity] = (
                    overlapping_relations[current_activity].get(overlapping_activity, 0) + 1
                )
    # Return matrix with dependency values
    return overlapping_relations
