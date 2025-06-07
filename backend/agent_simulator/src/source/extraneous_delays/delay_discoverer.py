from typing import Callable
from typing import Tuple
from typing import Union

import pandas as pd
from source.arrival_distribution import get_best_fitting_distribution
from source.extraneous_delays.availability import absolute_unavailability_intervals_within
from source.extraneous_delays.concurrency_oracle import Configuration as StartTimeConfiguration
from source.extraneous_delays.concurrency_oracle import OverlappingConcurrencyOracle
from source.extraneous_delays.config import Configuration
from source.extraneous_delays.config import TimerPlacement
from source.extraneous_delays.event_log import EventLogIDs
from source.extraneous_delays.resource_availability import CalendarResourceAvailability


def compute_naive_extraneous_activity_delays(
    event_log: pd.DataFrame,
    config: Configuration,
    should_consider_timer: Callable[[list], bool] = lambda delays: sum(delays) > 0.0,
    experimentation: bool = False,
) -> Union[dict, pd.DataFrame]:
    """
    Compute, for each activity, the distribution of its extraneous delays. I.e., the distribution of the time passed
    since the activity is both enabled and its resource available, and the recorded start of the activity.

    :param event_log:               Event log storing the information of the process.
    :param config:                  Configuration of the estimation search.
    :param should_consider_timer:   Lambda function that, given a list of floats representing all the delays registered,
                                    returns a boolean denoting if a timer should be considered or not. By default, no
                                    consider timer if all delays are 0.
    :param experimentation:         Experimentation option, if true, returns the event log enhanced with the detected
                                    extraneous delay for each activity instance.

    :return: a dictionary with the activity name as key and the time distribution of its delay.
    """
    log_ids = config.log_ids
    # Compute both enablement and resource availability times
    start_time_config = StartTimeConfiguration(
        log_ids=log_ids,
        concurrency_thresholds=config.concurrency_thresholds,
        working_schedules=config.working_schedules,
        consider_start_times=True,
    )
    if _should_compute_enabled_times(event_log, config):
        concurrency_oracle = OverlappingConcurrencyOracle(event_log, start_time_config)
        concurrency_oracle.add_enabled_times(event_log, set_nat_to_first_event=True, include_enabling_activity=True)
    if log_ids.available_time not in event_log.columns:
        resource_availability = CalendarResourceAvailability(event_log, start_time_config)
        resource_availability.add_resource_availability_times(event_log)
    # Who to impute the extraneous delay to: the executed activity (timer before), the enabling activity (timer after)
    impute_to = log_ids.activity if config.timer_placement == TimerPlacement.BEFORE else log_ids.enabling_activity
    # Discover the time distribution of each activity's delay
    if experimentation:
        enhanced_event_log = event_log.copy(deep=True)
        enhanced_event_log["estimated_extraneous_delay"] = 0.0
        indexes, delays = [], []
        for index, event in enhanced_event_log[(~pd.isna(enhanced_event_log[log_ids.enabled_time]))].iterrows():
            indexes += [index]
            delays += [
                (
                    event[log_ids.start_time] - max(event[log_ids.enabled_time], event[log_ids.available_time])
                ).total_seconds()
            ]
        enhanced_event_log.loc[indexes, "estimated_extraneous_delay"] = delays
        return enhanced_event_log
    else:
        timers = {}
        for activity, instances in event_log.groupby(impute_to):
            # Get the activity instances with enabled time
            filtered_instances = instances[(~pd.isna(instances[log_ids.enabled_time]))]
            # Compute the extraneous delays in seconds
            delays = [
                delay.total_seconds()
                for delay in filtered_instances[log_ids.start_time]
                - filtered_instances[[log_ids.enabled_time, log_ids.available_time]].max(
                    axis=1, skipna=True, numeric_only=False
                )
            ]
            # If the delay should be considered, add it
            if should_consider_timer(delays):
                timers[activity] = get_best_fitting_distribution(delays)
        # Return the delays
        return timers


def compute_complex_extraneous_activity_delays(
    event_log: pd.DataFrame,
    config: Configuration,
    should_consider_timer: Callable[[list], bool] = lambda delays: sum(delays) > 0.0,
    experimentation: bool = False,
) -> Union[dict, pd.DataFrame]:
    """
    Compute, for each activity, the distribution of its extraneous delays. To compute the extraneous delay of an
    activity instance, detect the first and lasts instants in time in which the activity was enabled and the resource
    available for processing it (taking into account both the resource contention and availability calendars). The
    extraneous delay is the interval between these two instants, no matter if the resource became unavailable in the
    middle.

    :param event_log:               Event log storing the information of the process.
    :param config:                  Configuration of the estimation search.
    :param should_consider_timer:   Lambda function that, given a list of floats representing all the delays registered,
                                    returns a boolean denoting if a timer should be considered or not. By default, no
                                    consider timer if all delays are 0.
    :param experimentation:         Experimentation option, if true, returns the event log enhanced with the detected
                                    extraneous delay for each activity instance.

    :return: a dictionary with the activity name as key and the time distribution of its delay.
    """
    # Compute enabled time of each activity instance
    log_ids = config.log_ids
    start_time_config = StartTimeConfiguration(
        log_ids=log_ids,
        concurrency_thresholds=config.concurrency_thresholds,
        working_schedules=config.working_schedules,
        consider_start_times=True,
    )
    if _should_compute_enabled_times(event_log, config):
        concurrency_oracle = OverlappingConcurrencyOracle(event_log, start_time_config)
        concurrency_oracle.add_enabled_times(event_log, set_nat_to_first_event=True, include_enabling_activity=True)
    # Compute first and last instants where the resource was available
    _extend_log_with_first_last_available(event_log, log_ids, config)
    # Who to impute the extraneous delay to: the executed activity (timer before), the enabling activity (timer after)
    impute_to = log_ids.activity if config.timer_placement == TimerPlacement.BEFORE else log_ids.enabling_activity
    # Discover the time distribution of each activity's delay
    if experimentation:
        enhanced_event_log = event_log.copy(deep=True)
        enhanced_event_log["estimated_extraneous_delay"] = 0.0
        indexes, delays = [], []
        for index, event in enhanced_event_log[(~pd.isna(enhanced_event_log[log_ids.enabled_time]))].iterrows():
            indexes += [index]
            delays += [(event["last_available"] - event["first_available"]).total_seconds()]
        enhanced_event_log.loc[indexes, "estimated_extraneous_delay"] = delays
        return enhanced_event_log
    else:
        timers = {}
        for activity, instances in event_log.groupby(impute_to):
            # Get the activity instances with enabled time
            filtered_instances = instances[(~pd.isna(instances[log_ids.enabled_time]))]
            # Transform the delay to seconds
            delays = [
                delay.total_seconds()
                for delay in (filtered_instances["last_available"] - filtered_instances["first_available"])
                if not pd.isna(delay)
            ]
            # If the delay should be considered, add it
            if should_consider_timer(delays):
                timers[activity] = get_best_fitting_distribution(delays)
        # Remove extra columns
        event_log.drop(["last_available", "first_available"], axis=1, inplace=True)
        # print(event_log)
        # Return discovered delays
        # print(f"timers: {timers}")
        return timers


def _extend_log_with_first_last_available(event_log: pd.DataFrame, log_ids: EventLogIDs, config: Configuration):
    """
    Add, to [event_log], two columns with the first and last timestamps in which the resource that performed that
    activity was available.

    :param event_log:   Event log storing the information of the process.
    :param log_ids:     Mapping for the columns in the event log.
    :param config:      Configuration of the estimation search.
    """
    # Initiate both first and last available columns to NaT
    event_log["first_available"] = None
    event_log["last_available"] = None
    for resource, events in event_log.groupby(log_ids.resource):
        # Initialize resource working calendar if existing
        calendar = config.working_schedules[resource] if resource in config.working_schedules else None
        indexes, first_available, last_available = [], [], []
        for index, event in events.iterrows():
            # Get activity instances performed by the same resource happening in its waiting time
            performed_events = events[
                (
                    (event[log_ids.enabled_time] < events[log_ids.end_time])
                    & (events[log_ids.end_time] <= event[log_ids.start_time])
                )
                | (
                    (event[log_ids.enabled_time] <= events[log_ids.start_time])
                    & (events[log_ids.start_time] < event[log_ids.start_time])
                )
            ]
            # If the resource has a calendar associated, get off-duty intervals happening in its waiting time
            if calendar:
                resource_off_duty = absolute_unavailability_intervals_within(
                    start=event[log_ids.enabled_time],
                    end=event[log_ids.start_time],
                    schedule=calendar,
                )
            else:
                resource_off_duty = []
            # Get first and last availability instants
            indexes += [index]
            first_instant, last_instant = _get_first_and_last_available(
                beginning=event[log_ids.enabled_time],
                end=event[log_ids.start_time],
                starts=list(performed_events[log_ids.start_time]) + [interval.start for interval in resource_off_duty],
                ends=list(performed_events[log_ids.end_time]) + [interval.end for interval in resource_off_duty],
                time_gap=config.time_gap,
                extrapolate=config.extrapolate_complex_delays_estimation,
            )
            if first_instant:
                # Available instants found
                first_available += [first_instant]
                last_available += [last_instant]
            else:
                # Busy during all the waiting time, set start time as availability
                first_available += [event[log_ids.start_time]]
                last_available += [event[log_ids.start_time]]
        # Set first and last available times for all events of this resource
        event_log.loc[indexes, "first_available"] = first_available
        event_log.loc[indexes, "last_available"] = last_available
    # Convert columns to Timestamp
    event_log["first_available"] = pd.to_datetime(event_log["first_available"], utc=True)
    event_log["last_available"] = pd.to_datetime(event_log["last_available"], utc=True)


def _get_first_and_last_available(
    beginning: pd.Timestamp,
    end: pd.Timestamp,
    starts: list,
    ends: list,
    time_gap: pd.Timedelta,
    extrapolate: bool = False,
) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Get the first instant from the period [from]-[to] where the resource was available for a [time_gap] amount of time.

    :param beginning:   Start of the interval where to search.
    :param end:         End of the interval where to search.
    :param starts:      List of instants where either a non-working period or an activity instance started.
    :param ends:        List of instants where either an activity instance or a non-working period finished.
    :param time_gap:    Minimum time gap required for a non-working period to be considered as such.
    :param extrapolate: If 'True', instead of getting the first available time as such, move it to half its distance
                        between itself and the beginning of the interval. For example, if the beginning is at 1, and
                        the discovered first available time is at 5, the extrapolated one is 3 (the middle point). The
                        same is done with the last available and the end of the interval. The objective is to reduce
                        potential mis-estimations as the real first available time is unknown.

    :return: A tuple with the first and last timestamps within all [start] and [end] timestamps where the
    resource was available for a [time_gap] amount of time.
    """
    # Add beginning and end of interval as artificial instant activities
    starts += [beginning, end]
    ends += [beginning, end]
    # Store the start and ends in a list of dicts
    times = (
        pd.DataFrame(
            {
                "time": starts + ends,
                "type": ["start"] * len(starts) + ["end"] * len(ends),
            }
        )
        .sort_values(["time", "type"], ascending=[True, False])
        .values.tolist()
    )
    first_available = None
    last_available = None
    # Go over them start->end, until a moment with no active unavailable intervals is reached
    i = 0
    active = 0  # Number of active unavailable intervals
    while not first_available and i < len(times):
        # Increase active unavailable intervals if current timestamps is 'start', or decrease otherwise
        active += 1 if times[i][1] == "start" else -1
        # Check if no active unavailable intervals
        if active == 0 and (  # No active unavailable intervals at this point, and
            i + 1 == len(times)  # either this is the last point, or
            or times[i + 1][0] - times[i][0] >= time_gap  # there is an available time gap with enough duration
        ):
            # Resource available at this point, check time gap until next event
            first_available = times[i][0]
        i += 1
    # If time gap found, search for last available, not necessary otherwise
    if not pd.isna(first_available):
        # Go over them end->start, until a moment with no active unavailable intervals is reached
        i = len(times) - 1  # Index to go over the timestamps
        active = 0  # Number of active unavailable intervals
        while not last_available and i > 0:
            if times[i][0] <= first_available:
                # If the search reached [first_available], set to it and finish
                last_available = first_available
            else:
                # Increase active unavailable intervals if current timestamps is 'end', or decrease otherwise
                active += 1 if times[i][1] == "end" else -1
                # Check if no active unavailable intervals
                if active == 0 and (  # No active unavailable intervals at this point, and
                    i == 0
                    or times[i][0] - times[i - 1][0] >= time_gap  # either this is the last point in the search, or
                ):  # there is an available time gap with enough duration
                    # Resource available at this point, check time gap until next event
                    last_available = times[i][0]
            i -= 1
    # If we are extrapolating the timestamps AND both timestamps were found
    if extrapolate and not pd.isna(first_available) and not pd.isna(last_available):
        # And there is a extraneous delay discovered
        if first_available != end and last_available != end:
            first_available = first_available - ((first_available - beginning) / 2)
            last_available = last_available + ((end - last_available) / 2)
    # Return first and last available timestamps
    return first_available, last_available


def _should_compute_enabled_times(event_log: pd.DataFrame, config: Configuration):
    return config.log_ids.enabled_time not in event_log.columns or (
        config.timer_placement == TimerPlacement.AFTER and config.log_ids.enabling_activity not in event_log.columns
    )
