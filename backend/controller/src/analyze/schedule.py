from datetime import datetime
from datetime import timedelta

import pandas as pd


class Schedule:
    def __init__(self, schedule_file, mode):
        """
        Initialize the schedule with time periods and daily schedules.
        Mode = agent or simod
        """
        self.mode = mode
        self.time_periods = schedule_file
        if mode == "simod":
            self._daily_schedules = self._daily_simod_schedules()
        elif mode == "agent":
            self._daily_schedules = self._daily_agent_schedules()
        else:
            raise NotImplementedError("Schedule has to be in mode simod or agent")

    def _daily_simod_schedules(self):
        """Convert simod time periods into a list of schedules per weekday (Monday=0 to Sunday=6)."""
        daily_schedules = [[] for _ in range(7)]

        for work_shift in self.time_periods:
            start_day = work_shift["from"]
            begin_time = pd.to_datetime(work_shift["beginTime"])
            end_time = pd.to_datetime(work_shift["endTime"])
            daily_schedules[self._day_to_int(start_day)].append((begin_time, end_time))
        return [daily_schedules]

    def _daily_agent_schedules(self):
        """Convert agent simulator time periods into a list of schedules per weekday (Monday=0 to Sunday=6)."""
        personal_schedules = [[[] for _ in range(7)] for _ in range(len(self.time_periods))]
        # ["0"]["data"]["timer_periods"]
        for key, value in self.time_periods.items():

            data = value["data"]
            work_shifts = data["time_periods"]

            for work_shift in work_shifts:
                start_day = work_shift["from"]
                begin_time = pd.to_datetime(work_shift["beginTime"])
                end_time = pd.to_datetime(work_shift["endTime"])
                personal_schedules[int(key)][self._day_to_int(start_day)].append((begin_time, end_time))
        return personal_schedules

    def _day_to_int(self, day: str):
        """Convert weekday string to integer index."""
        days = {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2, "THURSDAY": 3, "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}
        return days[day.upper()]

    def _int_to_day(self, day: int) -> str:
        """Convert weekday index to string name."""
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        if 0 <= day <= 6:
            return days[day]
        else:
            raise ValueError("Day must be an integer between 0 (Monday) and 6 (Sunday)")

    def _get_overlap_seconds(self, intervals, query_start, query_end):
        """Calculate overlap in seconds between given time interval and scheduled intervals."""
        total_overlap = timedelta(0)
        query_start_t = query_start.time()
        query_end_t = query_end.time()

        for start, end in intervals:
            start_t = start.time()
            end_t = end.time()
            latest_start = max(query_start_t, start_t)
            earliest_end = min(query_end_t, end_t)

            if latest_start < earliest_end:
                t1 = datetime.combine(datetime.min, latest_start)
                t2 = datetime.combine(datetime.min, earliest_end)
                total_overlap += t2 - t1

        return total_overlap.total_seconds()

    def _split_into_daily_intervals(self, start_time: pd.Timestamp, end_time: pd.Timestamp):
        """Split a multi-day interval into separate day-based intervals."""
        intervals = []
        aktivity_day_count = (end_time.date() - start_time.date()).days

        for i in range(aktivity_day_count + 1):
            if i == 0:
                sub_start = start_time
                sub_end = pd.Timestamp.combine(start_time.date(), pd.Timestamp.max.time())
            elif i == aktivity_day_count:
                sub_start = pd.Timestamp.combine(end_time.date(), pd.Timestamp.min.time())
                sub_end = end_time
            else:
                sub_date = (start_time + pd.Timedelta(days=i)).date()
                sub_start = pd.Timestamp.combine(sub_date, pd.Timestamp.min.time())
                sub_end = pd.Timestamp.combine(sub_date, pd.Timestamp.max.time())

            intervals.append((sub_start, sub_end))

        return intervals

    def _get_active_hours(self, start_time: pd.Timestamp, end_time: pd.Timestamp, agent_number: int = 0):
        """Calculate total active working hours between start and end timestamps."""
        aktivity_day_count = (end_time.date() - start_time.date()).days
        total_overlap = 0

        if aktivity_day_count > 0:
            for sub_start, sub_end in self._split_into_daily_intervals(start_time, end_time):
                weekday_index = sub_start.weekday()
                daily_overlap = self._get_overlap_seconds(
                    self._daily_schedules[agent_number][weekday_index], sub_start, sub_end
                )
                total_overlap += daily_overlap
        else:
            weekday_index = start_time.weekday()
            total_overlap = self._get_overlap_seconds(
                self._daily_schedules[agent_number][weekday_index], start_time, end_time
            )
        return total_overlap

    def get_available_time(self, start_time, end_time, resource_count=1):
        """
        Calculates the available time for all the resources from the start_time to the end_time
        based on their schedules. resource_count should only be provided for simod.

        Returns:
            float: The available time in seconds for every resource.
        """
        delta = end_time.date() - start_time.date()
        day_count = delta.days + 1
        start_day = start_time.weekday()
        resource_hours = []

        for resource in self._daily_schedules:
            week = []
            for day in resource:
                shift_total = 0
                for shift in day:
                    current_delta = shift[1] - shift[0]
                    shift_total += current_delta.total_seconds()

                week.append(shift_total)

            resource_hours.append(week)

        total_length = 0
        for resource in resource_hours:
            for i in range(start_day, (day_count + start_day)):
                day_index = i % 7
                total_length += resource[day_index]

        return total_length * resource_count

    def get_simod_resource_worked_hours(self, event_log: pd.DataFrame):
        workers = {}
        for i, row in event_log.iterrows():
            worker = row["resource"]
            start_time = pd.to_datetime(row["start_time"])
            end_time = pd.to_datetime(row["end_time"])
            akt_time = self._get_active_hours(start_time, end_time)
            if worker in workers:
                workers[worker] += akt_time
            else:
                workers[worker] = akt_time
        return workers

    def get_agent_resource_worked_hours(self, event_log: pd.DataFrame):
        workers = {}
        for i, row in event_log.iterrows():
            worker = str(row["agent"])

            start_time = pd.to_datetime(row["start_time"])
            end_time = pd.to_datetime(row["end_time"])
            akt_time = self._get_active_hours(start_time, end_time, int(worker))

            if worker in workers:
                workers[worker] += akt_time
            else:
                workers[worker] = akt_time
        return workers
