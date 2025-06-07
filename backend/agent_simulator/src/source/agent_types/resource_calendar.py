import datetime
from dataclasses import dataclass
from datetime import timedelta

import pandas as pd
from source.agent_types.calendar_discovery_parameters import conversion_table
from source.agent_types.calendar_discovery_parameters import int_week_days
from source.agent_types.calendar_discovery_parameters import str_week_days


class GranuleInfo:
    def __init__(self, week_day, index: int):
        self.week_day = week_day
        self.granule_index = index


class CalendarKPIInfoFactory:
    def __init__(self, minutes_x_granule=15):
        self.minutes_x_granule = minutes_x_granule
        self.total_granules = 1440 % self.minutes_x_granule

        self.g_discarded = {}

        # Fields to calculate Confidence and Support
        self.res_active_weekdays = {}
        self.res_active_granules_weekdays = {}
        self.res_enabled_task_granules = None
        self.res_granules_frequency = {}
        self.active_res_task_weekdays = {}
        self.active_res_task_weekdays_granules = {}
        self.res_task_weekdays_granules_freq = {}
        self.shared_task_granules = {}
        self.is_joint_resource = {}
        self.joint_to_task = {}
        self.observed_weekdays = {}

        # Fields to compute resource frequencies (needed for participation ratio)
        self.resource_freq = {}
        self.resource_task_freq = {}
        self.max_resource_freq = 0
        self.max_resource_task_freq = {}

        self.task_events_count = {}
        self.task_events_in_calendar = {}
        self.total_events_in_log = 0
        self.total_events_in_calendar = 0

        self.res_count_events_in_calendar = {}
        self.res_count_events_in_log = {}
        self.active_granules_in_calendar = {}
        self.active_weekdays_in_calendar = {}
        self.confidence_numerator_sum = {}
        self.confidence_denominator_sum = {}

        self.task_enabled_in_granule = {}

    def register_resource_timestamp(self, r_name, t_name, date_time, is_joint=False):
        str_date, g_index, weekday = self.split_datetime(date_time)

        if r_name not in self.resource_freq:
            self.resource_freq[r_name] = 0
            self.resource_task_freq[r_name] = {}
            self.res_active_weekdays[r_name] = {}
            self.res_active_granules_weekdays[r_name] = {}
            self.res_granules_frequency[r_name] = {}
            self.active_res_task_weekdays[r_name] = {}
            self.active_res_task_weekdays_granules[r_name] = {}
            self.shared_task_granules[r_name] = {}
            self.res_task_weekdays_granules_freq[r_name] = {}

            if is_joint:
                self.joint_to_task[r_name] = t_name

            self.g_discarded[r_name] = []

            self.res_count_events_in_calendar[r_name] = 0
            self.res_count_events_in_log[r_name] = 0
            self.active_granules_in_calendar[r_name] = set()
            self.active_weekdays_in_calendar[r_name] = set()
            self.confidence_numerator_sum[r_name] = 0
            self.confidence_denominator_sum[r_name] = 0
            self.is_joint_resource[r_name] = is_joint

        if t_name not in self.task_events_count:
            self.task_events_count[t_name] = 0
            self.task_events_in_calendar[t_name] = 0
            self.max_resource_task_freq[t_name] = 0
        if t_name not in self.resource_task_freq[r_name]:
            self.resource_task_freq[r_name][t_name] = 0
            self.active_res_task_weekdays[r_name][t_name] = {}
            self.active_res_task_weekdays_granules[r_name][t_name] = {}
            self.res_task_weekdays_granules_freq[r_name][t_name] = {}
        if weekday not in self.active_res_task_weekdays[r_name][t_name]:
            self.active_res_task_weekdays[r_name][t_name][weekday] = set()
            self.active_res_task_weekdays_granules[r_name][t_name][weekday] = {}
        if g_index not in self.active_res_task_weekdays_granules[r_name][t_name][weekday]:
            self.active_res_task_weekdays_granules[r_name][t_name][weekday][g_index] = set()
        if g_index not in self.res_task_weekdays_granules_freq[r_name][t_name]:
            self.res_task_weekdays_granules_freq[r_name][t_name][g_index] = {}
        if weekday not in self.res_task_weekdays_granules_freq[r_name][t_name][g_index]:
            self.res_task_weekdays_granules_freq[r_name][t_name][g_index][weekday] = 0
        if weekday not in self.res_active_weekdays[r_name]:
            self.res_active_weekdays[r_name][weekday] = set()
        if g_index not in self.res_active_granules_weekdays[r_name]:
            self.res_active_granules_weekdays[r_name][g_index] = {}
            self.res_granules_frequency[r_name][g_index] = {}
            self.shared_task_granules[r_name][g_index] = {}
        if weekday not in self.res_active_granules_weekdays[r_name][g_index]:
            self.res_active_granules_weekdays[r_name][g_index][weekday] = set()
            self.res_granules_frequency[r_name][g_index][weekday] = 0
            self.shared_task_granules[r_name][g_index][weekday] = set()
        if weekday not in self.observed_weekdays:
            self.observed_weekdays[weekday] = set()

        # Updating the weekdays and granules the resource was observed working
        self.res_active_weekdays[r_name][weekday].add(str_date)
        self.res_active_granules_weekdays[r_name][g_index][weekday].add(str_date)
        self.res_granules_frequency[r_name][g_index][weekday] += 1

        self.active_res_task_weekdays_granules[r_name][t_name][weekday][g_index].add(str_date)
        self.active_res_task_weekdays[r_name][t_name][weekday].add(str_date)

        self.resource_freq[r_name] += 1
        self.resource_task_freq[r_name][t_name] += 1
        self.res_count_events_in_log[r_name] += 1
        self.shared_task_granules[r_name][g_index][weekday].add(t_name)
        self.res_task_weekdays_granules_freq[r_name][t_name][g_index][weekday] += 1

        if not is_joint:
            self.max_resource_task_freq[t_name] = max(
                self.max_resource_task_freq[t_name],
                self.resource_task_freq[r_name][t_name],
            )
            self.observed_weekdays[weekday].add(str_date)
            self.max_resource_freq = max(self.max_resource_freq, self.resource_freq[r_name])
            self.task_events_count[t_name] += 1
            self.total_events_in_log += 1

    def register_task_enablement(self, trace_events):
        self.res_enabled_task_granules = None
        for e_info in trace_events:
            t_name = e_info.task_name
            if t_name not in self.task_enabled_in_granule:
                self.task_enabled_in_granule[t_name] = {}
            current_date = e_info.enabled_at
            str_date, g_index, weekday = self.split_datetime(current_date)
            while current_date < e_info.completed_at:
                if g_index not in self.task_enabled_in_granule[t_name]:
                    self.task_enabled_in_granule[t_name][g_index] = {}
                if weekday not in self.task_enabled_in_granule[t_name][g_index]:
                    self.task_enabled_in_granule[t_name][g_index][weekday] = set()
                self.task_enabled_in_granule[t_name][g_index][weekday].add(str_date)
                current_date += timedelta(minutes=self.minutes_x_granule)
                if g_index >= self.total_granules - 1:
                    str_date, g_index, weekday = self.split_datetime(current_date)
                else:
                    g_index += 1

    def compute_resource_task_granule_enablement(self):
        self.res_enabled_task_granules = {}
        for r_name in self.resource_task_freq:
            self.res_enabled_task_granules[r_name] = {}
            joint_granules = {}
            for t_name in self.resource_task_freq[r_name]:
                for g_index in self.task_enabled_in_granule[t_name]:
                    if g_index not in self.res_enabled_task_granules[r_name]:
                        joint_granules[g_index] = {}
                        self.res_enabled_task_granules[r_name][g_index] = {}
                    for weekday in self.task_enabled_in_granule[t_name][g_index]:
                        if weekday not in self.res_enabled_task_granules[r_name][g_index]:
                            self.res_enabled_task_granules[r_name][g_index][weekday] = set()
                            joint_granules[g_index][weekday] = set()
                        joint_granules[g_index][weekday] |= self.task_enabled_in_granule[t_name][g_index][weekday]
            for g_index in joint_granules:
                for weekday in joint_granules[g_index]:
                    self.res_enabled_task_granules[r_name][g_index][weekday] = len(joint_granules[g_index][weekday])

    def enablement_confidence(self, r_name, weekday, g_index):
        if self.res_enabled_task_granules is None:
            self.compute_resource_task_granule_enablement()
        return (
            len(self.res_active_granules_weekdays[r_name][g_index][weekday])
            / self.res_enabled_task_granules[r_name][g_index][weekday]
        )

    def task_cond_confidence(self, r_name, weekday, g_index):
        best_task = None
        max_conf_val = 0
        task_confidences = {}
        for t_name in self.shared_task_granules[r_name][g_index][weekday]:
            task_confidences[t_name] = len(
                self.active_res_task_weekdays_granules[r_name][t_name][weekday][g_index]
            ) / len(self.active_res_task_weekdays[r_name][t_name][weekday])
            if max_conf_val < task_confidences[t_name]:
                best_task = t_name
                max_conf_val = task_confidences[t_name]
        return best_task, task_confidences

    def resource_participation_ratio(self, r_name):
        total_res = 0
        total_max = 0
        for t_name in self.resource_task_freq[r_name]:
            total_res += self.resource_task_freq[r_name][t_name]
            total_max += self.max_resource_task_freq[t_name]
        return total_res / total_max if total_max > 0 else 0

    def resource_task_participation_ratio(self, r_name, t_name):
        if self.max_resource_task_freq[t_name] > 0:
            return self.resource_task_freq[r_name][t_name] / self.max_resource_task_freq[t_name]
        return 0

    # From all the WeekDays the resource was active, in which ration they were in the given granule
    def confidence(self, r_name, weekday, g_index):
        return len(self.res_active_granules_weekdays[r_name][g_index][weekday]) / len(
            self.res_active_weekdays[r_name][weekday]
        )

    def support(self, r_name, weekday, g_index):
        return len(self.res_active_granules_weekdays[r_name][g_index][weekday]) / len(self.observed_weekdays[weekday])

    def weekday_support(self, r_name, weekday):
        return len(self.res_active_weekdays[r_name][weekday]) / len(self.observed_weekdays[weekday])

    def task_coverage(self, t_name):
        return self.task_events_in_calendar[t_name] / self.task_events_count[t_name]

    def can_improve_support(self, r_name, weekday, g_index):
        best_task, confidence_values = self.task_cond_confidence(r_name, weekday, g_index)

        return best_task

    def reset_calendar_info(self):
        self.total_events_in_calendar = 0
        for t_name in self.task_events_count:
            self.task_events_in_calendar[t_name] = 0
        for r_name in self.shared_task_granules:
            self.res_count_events_in_calendar[r_name] = 0
            self.active_granules_in_calendar[r_name] = set()
            self.active_weekdays_in_calendar[r_name] = set()
            self.g_discarded[r_name] = []
            self.confidence_numerator_sum[r_name] = 0
            self.confidence_denominator_sum[r_name] = 0

    def check_accepted_granule(self, r_name, weekday, g_index, best_task):  # TODO: what does it check?
        self.res_count_events_in_calendar[r_name] += self.res_granules_frequency[r_name][g_index][weekday]
        self.total_events_in_calendar += self.res_granules_frequency[r_name][g_index][weekday]
        self.confidence_numerator_sum[r_name] += len(
            self.active_res_task_weekdays_granules[r_name][best_task][weekday][g_index]
        )
        self.confidence_denominator_sum[r_name] += len(self.active_res_task_weekdays[r_name][best_task][weekday])
        self.active_granules_in_calendar[r_name] |= self.active_res_task_weekdays_granules[r_name][best_task][weekday][
            g_index
        ]
        self.active_weekdays_in_calendar[r_name] |= self.active_res_task_weekdays[r_name][best_task][weekday]
        for t_name in self.shared_task_granules[r_name][g_index][weekday]:
            self.task_events_in_calendar[t_name] += self.res_task_weekdays_granules_freq[r_name][t_name][g_index][
                weekday
            ]

    def check_discarded_granule(self, r_name, weekday, g_index):
        if r_name not in self.g_discarded:
            self.g_discarded[r_name] = []
        self.g_discarded[r_name].append(GranuleInfo(weekday, g_index))

    def update_discarded_granules_list(self, r_name, accepted_indexes):
        if len(accepted_indexes) == 0:
            return
        new_discarded = []
        c_j = 0
        for i in range(0, len(self.g_discarded[r_name])):
            if c_j < len(accepted_indexes) and i == accepted_indexes[c_j]:
                c_j += 1
            else:
                new_discarded.append(self.g_discarded[r_name][i])
        self.g_discarded[r_name] = new_discarded

    def split_datetime(self, date_time):
        str_date = str(date_time.date())
        in_minutes = date_time.hour * 60 + date_time.minute

        g_index = in_minutes // self.minutes_x_granule
        week_day = date_time.weekday()
        return str_date, g_index, week_day

    def compute_confidence_support(self, r_name):
        if (
            r_name not in self.active_weekdays_in_calendar
            or len(self.active_weekdays_in_calendar[r_name]) == 0
            or self.res_count_events_in_log[r_name] == 0
        ):
            return 0, 0
        return (
            self.confidence_numerator_sum[r_name] / self.confidence_denominator_sum[r_name],
            self.res_count_events_in_calendar[r_name] / self.res_count_events_in_log[r_name],
        )


class IntervalPoint:
    def __init__(self, date_time, week_day, index, to_start_dist, to_end_dist):
        self.date_time = date_time
        self.week_day = week_day
        self.index = index
        self.to_start_dist = to_start_dist
        self.to_end_dist = to_end_dist

    def in_same_interval(self, another_point):
        return self.week_day == another_point.week_day and self.index == another_point.index


@dataclass
class Interval:
    start: datetime.datetime
    end: datetime.datetime
    duration: float

    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start
        if end < start and end.hour == 0 and end.minute == 0:
            end.replace(hour=23, minute=59, second=59, microsecond=999)
        self.end = end
        self.duration = (end - start).total_seconds()

    def __eq__(self, other):
        if isinstance(other, Interval):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def merge_interval(self, n_interval: "Interval"):
        self.start = min(n_interval.start, self.start)
        self.end = max(n_interval.end, self.end)
        self.duration = (self.end - self.start).total_seconds()

    def is_before(self, c_date):
        return self.end <= c_date

    def contains(self, c_date):
        return self.start < c_date < self.end

    def contains_inclusive(self, c_date):
        return self.start <= c_date <= self.end

    def is_after(self, c_date):
        return c_date <= self.start

    def intersection(self, interval):
        if interval is None:
            return None
        [first_i, second_i] = [self, interval] if self.start <= interval.start else [interval, self]
        if second_i.start < first_i.end:
            return Interval(max(first_i.start, second_i.start), min(first_i.end, second_i.end))
        return None


class CalendarIterator:
    def __init__(self, start_date: datetime, calendar_info):
        self.start_date = start_date

        self.calendar = calendar_info

        self.c_day = start_date.date().weekday()

        c_date = datetime.datetime.combine(calendar_info.default_date, start_date.time())
        c_interval = calendar_info.work_intervals[self.c_day][0]
        self.c_index = -1
        while c_interval.end < c_date and self.c_index < len(calendar_info.work_intervals[self.c_day]) - 1:
            self.c_index += 1
            c_interval = calendar_info.work_intervals[self.c_day][self.c_index]

        self.c_interval = Interval(
            self.start_date,
            self.start_date + timedelta(seconds=(c_interval.end - c_date).total_seconds()),
        )

    def next_working_interval(self):
        res_interval = self.c_interval
        day_intervals = self.calendar.work_intervals[self.c_day]
        p_duration = 0

        self.c_index += 1
        if self.c_index >= len(day_intervals):
            p_duration += 86400 - (day_intervals[self.c_index - 1].end - self.calendar.new_day).total_seconds()
            while True:
                self.c_day = (self.c_day + 1) % 7
                day_intervals = self.calendar.work_intervals[self.c_day]
                if len(day_intervals) > 0:
                    p_duration += (day_intervals[0].start - self.calendar.new_day).total_seconds()
                    break
                else:
                    p_duration += 86400
            self.c_index = 0
        elif self.c_index > 0:
            p_duration += (day_intervals[self.c_index].start - day_intervals[self.c_index - 1].end).total_seconds()
        self.c_interval = Interval(
            res_interval.end + timedelta(seconds=p_duration),
            res_interval.end + timedelta(seconds=p_duration + day_intervals[self.c_index].duration),
        )
        return res_interval


class RCalendar:  # AvailabilityCalendar
    def __init__(self, calendar_id):
        self.calendar_id = calendar_id
        self.default_date = None
        self.work_intervals = {}
        self.new_day = None
        self.cumulative_work_durations = {}
        self.work_rest_count = {}
        self.total_weekly_work = 0
        self.total_weekly_rest = to_seconds(1, "WEEKS")
        for i in range(0, 7):
            self.work_intervals[i] = []
            self.cumulative_work_durations[i] = []
            self.work_rest_count[i] = [0, to_seconds(1, "DAYS")]

    def update_day_schedule(self, day_str: str, new_periods: list[tuple[str, str]]):
        """
        Replace the schedule for one weekday with a new list of (begin, end) times.

        day_str:  name of the day, e.g. "MONDAY", "tuesday", etc.
        new_periods: list of (begin_time, end_time) strings, e.g.
                     [("09:00:00", "12:00:00"), ("13:00:00", "17:00:00")]
        """
        # 1) Map the day name to an index 0–6
        upper = day_str.upper()
        if upper not in str_week_days:
            raise ValueError(f"Unknown weekday: {day_str}")
        w_day = str_week_days[upper]  # e.g. "MONDAY" → 0

        # 2) Subtract out all the old durations (so our weekly totals stay correct)
        old_total = sum(iv.duration for iv in self.work_intervals[w_day])
        self.total_weekly_work -= old_total
        self.total_weekly_rest += old_total
        self.work_rest_count[w_day][0] -= old_total
        self.work_rest_count[w_day][1] += old_total

        # 2b) Clear existing intervals & cumulative trackers
        self.work_intervals[w_day].clear()
        self.cumulative_work_durations[w_day].clear()

        # 3) Add each new period
        for begin, end in new_periods:
            # print(f"Changed: start:{begin}, END: {end}")
            # Since from_day == to_day, we just reuse day_str
            self.add_calendar_item(day_str, day_str, begin, end)

        # 4) (Re)compute cumulative for that day only
        cum = 0
        for iv in self.work_intervals[w_day]:
            cum += iv.duration
            self.cumulative_work_durations[w_day].append(cum)

    def to_dict(self):
        return {
            "id": self.calendar_id,
            "name": self.calendar_id,
            "time_periods": self.intervals_to_json(),
        }

    def intervals_to_json(self):
        items = []

        for i in range(0, 7):
            if len(self.work_intervals[i]) > 0:
                for interval in self.work_intervals[i]:
                    items.append(
                        {
                            "from": int_week_days[i],
                            "to": int_week_days[i],
                            "beginTime": str(interval.start.time()),
                            "endTime": str(interval.end.time()),
                        }
                    )

        return items

    @staticmethod
    def from_dict(calendar_dict):
        calendar = RCalendar(calendar_dict["id"])
        for time_period in calendar_dict["time_periods"]:
            calendar.add_calendar_item(
                time_period["from"],
                time_period["to"],
                time_period["beginTime"],
                time_period["endTime"],
            )
        return calendar

    def is_empty(self):
        # Return false (no empty) if any interval in a week day
        for i in range(0, 7):
            if len(self.work_intervals[i]) > 0:
                return False
        # Return true (empty) if no interval found
        return True

    def is_working_datetime(self, date_time):
        c_day = date_time.date().weekday()
        c_date = datetime.datetime.combine(self.default_date, date_time.time())
        i_index = 0
        for interval in self.work_intervals[c_day]:
            if interval.contains_inclusive(c_date):
                return True, IntervalPoint(
                    date_time,
                    i_index,
                    c_day,
                    (c_date - interval.start).total_seconds(),
                    (interval.end - c_date).total_seconds(),
                )
            i_index += 1
        return False, None

    def combine_calendar(self, new_calendar):
        for i in range(0, 7):
            if len(new_calendar.work_intervals[i]) > 0:
                for interval in new_calendar.work_intervals[i]:
                    self.add_calendar_item(
                        int_week_days[i],
                        int_week_days[i],
                        str(interval.start.time()),
                        str(interval.end.time()),
                    )

    def add_calendar_item(self, from_day: str, to_day: str, begin_time: str, end_time: str):
        if from_day.upper() in str_week_days and to_day.upper() in str_week_days:
            try:
                t_interval = Interval(
                    start=pd.Timestamp(begin_time).to_pydatetime(),
                    end=pd.Timestamp(end_time).to_pydatetime(),
                )
                if self.default_date is None:
                    self.default_date = t_interval.start.date()
                    self.new_day = datetime.datetime.combine(self.default_date, datetime.time())
                d_s = str_week_days[from_day]
                d_e = str_week_days[to_day]
                while True:
                    self._add_interval(d_s % 7, t_interval)
                    if d_s % 7 == d_e:
                        break
                    d_s += 1
            except ValueError:
                return

    def _add_interval(self, w_day, interval):
        i = 0
        for to_merge in self.work_intervals[w_day]:
            if to_merge.end < interval.start:
                i += 1
                continue
            if interval.end < to_merge.start:
                break
            merged_duration = to_merge.duration
            to_merge.merge_interval(interval)
            merged_duration = to_merge.duration - merged_duration
            i += 1
            while i < len(self.work_intervals[w_day]):
                next_i = self.work_intervals[w_day][i]
                if to_merge.end < next_i.start:
                    break
                if next_i.end <= to_merge.end:
                    merged_duration -= next_i.duration
                elif next_i.start <= to_merge.end:
                    merged_duration -= (to_merge.end - next_i.start).total_seconds()
                    to_merge.merge_interval(next_i)
                del self.work_intervals[w_day][i]
            if merged_duration > 0:
                self._update_calendar_durations(w_day, merged_duration)
            return
        self.work_intervals[w_day].insert(i, interval)
        self._update_calendar_durations(w_day, interval.duration)

    def compute_cumulative_durations(self):
        for w_day in self.work_intervals:
            cumulative = 0
            for interval in self.work_intervals[w_day]:
                cumulative += interval.duration
                self.cumulative_work_durations[w_day].append(cumulative)

    def _update_calendar_durations(self, w_day, duration):
        self.work_rest_count[w_day][0] += duration
        self.work_rest_count[w_day][1] -= duration
        self.total_weekly_work += duration
        self.total_weekly_rest -= duration

    def remove_idle_times(self, from_date, to_date, out_intervals: list):
        calendar_it = CalendarIterator(from_date, self)
        while True:
            c_interval = calendar_it.next_working_interval()
            if c_interval.end < to_date:
                out_intervals.append(c_interval)
            else:
                if c_interval.start <= to_date <= c_interval.end:
                    out_intervals.append(Interval(c_interval.start, to_date))
                break

    def find_idle_time(self, requested_date, duration):
        if duration == 0:
            return 0
        real_duration = 0
        pending_duration = duration
        if duration > self.total_weekly_work:
            real_duration += to_seconds(int(duration / self.total_weekly_work), "WEEKS")
            pending_duration %= self.total_weekly_work
        # Addressing the first day as an special case
        c_day = requested_date.date().weekday()
        c_date = datetime.datetime.combine(self.default_date, requested_date.time())

        worked_time, total_time = self._find_time_starting(pending_duration, c_day, c_date)
        if worked_time > total_time and worked_time - total_time < 0.001:
            total_time = worked_time
        pending_duration -= worked_time
        real_duration += total_time
        c_date = self.new_day
        while pending_duration > 0:
            c_day += 1
            r_d = c_day % 7
            if pending_duration > self.work_rest_count[r_d][0]:
                pending_duration -= self.work_rest_count[r_d][0]
                real_duration += 86400
            else:
                real_duration += self._find_time_completion(pending_duration, self.work_rest_count[r_d][0], r_d, c_date)
                break
        return real_duration

    def next_available_time(self, requested_date):
        """
        Validates whether the 'requested_date' is located in the arrival time calendar.
        Valid = complies with the provided time periods of the arrival calendar.
        If the 'requested_date' is valid, 0 is being returned (no waiting time).
        If not, the number of seconds we need to wait till the time the datetime will
        become eligible and comply with the time periods of the calendar.
        """
        c_day = requested_date.date().weekday()
        c_date = datetime.datetime.combine(self.default_date, requested_date.time())

        for interval in self.work_intervals[c_day]:
            if interval.end == c_day:
                continue
            if interval.is_after(c_date):
                return (interval.start - c_date).total_seconds()
            if interval.contains(c_date):
                return 0
        duration = 86400 - (c_date - self.new_day).total_seconds()
        for i in range(c_day + 1, c_day + 8):
            r_day = i % 7
            if self.work_rest_count[r_day][0] > 0:
                return duration + (self.work_intervals[r_day][0].start - self.new_day).total_seconds()
            duration += 86400
        return duration

    def find_working_time(self, start_date, end_date):
        pending_duration = (end_date - start_date).total_seconds()
        worked_hours = 0

        c_day = start_date.date().weekday()
        c_date = datetime.datetime.combine(self.default_date, start_date.time())

        to_complete_day = 86400 - (c_date - self.new_day).total_seconds()
        available_work = self._calculate_available_duration(c_day, c_date)

        previous_date = c_date
        while pending_duration > to_complete_day:
            pending_duration -= to_complete_day
            worked_hours += available_work
            c_day = (c_day + 1) % 7
            available_work = self.work_rest_count[c_day][0]
            to_complete_day = 86400
            previous_date = self.new_day

        for interval in self.work_intervals[c_day]:
            if interval.is_before(previous_date):
                continue
            interval_duration = interval.duration
            if interval.contains(previous_date):
                interval_duration -= (previous_date - interval.start).total_seconds()
            else:
                pending_duration -= (interval.start - previous_date).total_seconds()
            if pending_duration >= interval_duration:
                worked_hours += interval_duration
            elif pending_duration > 0:
                worked_hours += pending_duration
            pending_duration -= interval_duration
            if pending_duration <= 0:
                break
            previous_date = interval.end
        return worked_hours

    def _find_time_starting(self, pending_duration, c_day, from_date):
        available_duration = self._calculate_available_duration(c_day, from_date)
        if available_duration <= pending_duration:
            return (
                available_duration,
                86400 - (from_date - self.new_day).total_seconds(),
            )
        else:
            return pending_duration, self._find_time_completion(pending_duration, available_duration, c_day, from_date)

    def _calculate_available_duration(self, c_day, from_date):
        i = -1
        passed_duration = 0
        for t_interval in self.work_intervals[c_day]:
            i += 1
            if t_interval.is_before(from_date):
                passed_duration += t_interval.duration
                continue
            if t_interval.is_after(from_date):
                break
            if t_interval.contains(from_date):
                passed_duration += (from_date - self.work_intervals[c_day][i].start).total_seconds()
                break

        return self.work_rest_count[c_day][0] - passed_duration

    def _find_time_completion(self, pending_duration, total_duration, c_day, from_datetime):
        i = len(self.work_intervals[c_day]) - 1
        while total_duration > pending_duration:
            total_duration -= self.work_intervals[c_day][i].duration
            i -= 1
        if total_duration < pending_duration:
            to_datetime = self.work_intervals[c_day][i + 1].start + timedelta(
                seconds=(pending_duration - total_duration)
            )
            return (to_datetime - from_datetime).total_seconds()
        else:
            return (self.work_intervals[c_day][i].end - from_datetime).total_seconds()

    def print_calendar_info(self):
        print("Calendar ID: %s" % self.calendar_id)
        print("Total Weekly Work: %.2f Hours" % (self.total_weekly_work / 3600))
        for i in range(0, 7):
            if len(self.work_intervals[i]) > 0:
                print(int_week_days[i])
                for interval in self.work_intervals[i]:
                    print(
                        "    from %02d:%02d - to %02d:%02d"
                        % (
                            interval.start.hour,
                            interval.start.minute,
                            interval.end.hour,
                            interval.end.minute,
                        )
                    )


def build_full_time_calendar(calendar_id) -> RCalendar:
    r_calendar = RCalendar(calendar_id)
    for i in range(0, 7):
        str_weekday = int_week_days[i]
        r_calendar.add_calendar_item(str_weekday, str_weekday, "00:00:00.000", "23:59:59.999")
    return r_calendar


def to_seconds(value, from_unit):
    u_from = from_unit.upper()
    return value * conversion_table[u_from] if u_from in conversion_table else value
