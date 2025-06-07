from typing import List

import pandas as pd
import pytz
from source.agent_types.resource_calendar import Interval
from source.agent_types.resource_calendar import RCalendar


def get_last_available_timestamp(start: pd.Timestamp, end: pd.Timestamp, schedule: RCalendar) -> pd.Timestamp:
    """
    Get the timestamp [last_available] within the interval from [start] to [end] (i.e. [start] <= [last_available] <= [end]) such that
    the interval from [last_available] to [end] is the largest and all of it is in the working hours in the calendar [schedule].

    For example, for [start] = 09:30, [end] = 14:00, and a [schedule] of every week day from 06:00 to 09:00, and from 10:00 to 16:00. The
    [last_available] would be 10:00.

    :param start:       start of the interval where to search for the point since when all time is part of the working schedule.
    :param end:         end of the interval where to search for the point since when all time is part of the working schedule.
    :param schedule:    RCalendar with the weekly working schedule.

    :return: The earliest point within the interval from [start] to [end] since which all the time is part of working hours defined in the
             resource calendar [schedule].
    """
    # Get the latest working period previous to the end of the interval
    last_available = end
    found = False
    while not found:
        day_intervals = schedule.work_intervals[last_available.weekday()]
        for interval in reversed(day_intervals):
            # Move interval to current day
            interval_start = interval.start.replace(
                day=last_available.day,
                month=last_available.month,
                year=last_available.year,
                tzinfo=pytz.timezone("UTC"),
            )
            interval_end = interval.end.replace(
                day=last_available.day,
                month=last_available.month,
                year=last_available.year,
                tzinfo=pytz.timezone("UTC"),
            )
            if interval_end < last_available:
                # The last available is later than the end of the current working interval
                if (last_available - interval_end) > pd.Timedelta(seconds=2):
                    # Non-working time gap previous to last_available, search finished
                    found = True
                    # Correct jump to previous day if needed
                    if (
                        last_available.hour == 23
                        and last_available.minute == 59
                        and last_available.second == 59
                        and last_available.microsecond == 999999
                    ):
                        last_available = last_available + pd.Timedelta(microseconds=1)
                else:
                    # No non-working time gap, move to the start of this working interval and continue
                    last_available = last_available.replace(
                        hour=interval_start.hour,
                        minute=interval_start.minute,
                        second=interval_start.second,
                        microsecond=interval_start.microsecond,
                    )
            elif interval_start <= last_available <= interval_end:
                # The last available timestamp is within the current interval
                last_available = last_available.replace(
                    hour=interval_start.hour,
                    minute=interval_start.minute,
                    second=interval_start.second,
                    microsecond=interval_start.microsecond,
                )
        if not found:
            start_of_day = last_available.replace(hour=00, minute=00, second=00, microsecond=0)
            if (last_available - start_of_day) > pd.Timedelta(seconds=2):
                # Non-working interval between last_available and the start of the day
                found = True
            else:
                # Move to previous day at 23:59:59.999999
                last_available = (last_available - pd.Timedelta(days=1)).replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
        # If last_available moved previously to the start of the queried interval
        if last_available <= start:
            # Stop and set to the start of the queried interval
            found = True
            last_available = start
    # Return last available timestamp
    return last_available


def absolute_unavailability_intervals_within(
    start: pd.Timestamp, end: pd.Timestamp, schedule: RCalendar
) -> List[Interval]:
    """
    Compute the list of intervals (in absolute timestamps) from [start] to [end] where, based on the working intervals in [schedule], the
    resource is not working.

    :param start:       Start of the interval to get the non-working periods from.
    :param end:         End of the interval to get the non-working periods from.
    :param schedule:    Working calendar with the working periods of each weekday.

    :return: a list with the non-working intervals from [start] to [end].
    """
    non_working_intervals = []
    if start < end:
        # Begin search with [start] and go over until reaching the end
        current_instant = start
        while current_instant < end:
            # Go over the working intervals of the current weekday, storing the non-working periods
            day_intervals = schedule.work_intervals[current_instant.weekday()]
            for interval in day_intervals:
                # Move interval to current day
                interval_start = interval.start.replace(
                    day=current_instant.day,
                    month=current_instant.month,
                    year=current_instant.year,
                    tzinfo=pytz.timezone("UTC"),
                )
                interval_end = interval.end.replace(
                    day=current_instant.day,
                    month=current_instant.month,
                    year=current_instant.year,
                    tzinfo=pytz.timezone("UTC"),
                )
                if current_instant < interval_end:
                    if current_instant < interval_start:
                        # Non-working time gap between [current_instant] and the start of the current working interval, save it
                        non_working_intervals += [Interval(current_instant, min(interval_start, end))]
                    # Advance [current_instant] to the end of the working interval
                    current_instant = min(interval_end, end)
            # Current day finished, add non-working interval from current instant to end of day and advance
            end_of_day = current_instant.replace(hour=23, minute=59, second=59, microsecond=0) + pd.Timedelta(
                microseconds=999999
            )
            if current_instant < end:
                non_working_intervals += [Interval(current_instant, min(end_of_day, end))]
                current_instant = (current_instant + pd.Timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
    # Return found non-working intervals
    return non_working_intervals
