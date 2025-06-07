import datetime
from typing import Dict

import pytz
from source.agent_types.resource_calendar import CalendarKPIInfoFactory
from source.agent_types.resource_calendar import GranuleInfo
from source.agent_types.resource_calendar import RCalendar
from source.agent_types.resource_calendar import int_week_days


class CalendarFactory:
    def __init__(self, minutes_x_granule=15):
        if 1440 % minutes_x_granule != 0:
            raise ValueError(
                "The number of minutes per granule must be a divisor of the total minutes in one day (1440)."
            )

        self.kpi_calendar = CalendarKPIInfoFactory(minutes_x_granule)
        self.minutes_x_granule = minutes_x_granule

        self.from_datetime = datetime.datetime(9999, 12, 31, tzinfo=pytz.UTC)
        self.to_datetime = datetime.datetime(1, 1, 1, tzinfo=pytz.UTC)

    def check_date_time(self, resource_name, activity_name, timestamp, is_joint=False):
        self.kpi_calendar.register_resource_timestamp(resource_name, activity_name, timestamp, is_joint)

        self.from_datetime = min(self.from_datetime, timestamp)
        self.to_datetime = max(self.to_datetime, timestamp)

    def build_weekly_calendars(self, min_confidence, desired_support, min_participation) -> Dict[str, RCalendar]:
        """
        Builds a calendar for each resource in the KPI calendar, using the given parameters.
        Returns a dictionary with the resource name as key and its calendar as value.
        """

        self.kpi_calendar.reset_calendar_info()

        r_calendars = {}

        for r_name in self.kpi_calendar.shared_task_granules:
            if self.kpi_calendar.resource_participation_ratio(r_name) >= min_participation:
                r_calendars[r_name] = self._build_resource_calendar(r_name, min_confidence, desired_support)
            else:
                r_calendars[r_name] = None

        return r_calendars

    def _build_resource_calendar(self, r_name, min_confidence, desired_support) -> RCalendar:
        kpi_c = self.kpi_calendar
        r_calendar = RCalendar("%s_Schedule" % r_name)

        count = 0
        for g_index in kpi_c.shared_task_granules[r_name]:
            for weekday in kpi_c.shared_task_granules[r_name][g_index]:
                best_task, conf_values = kpi_c.task_cond_confidence(r_name, weekday, g_index)
                if min_confidence <= conf_values[best_task]:
                    kpi_c.check_accepted_granule(r_name, weekday, g_index, best_task)
                    self._add_calendar_item(weekday, g_index, r_calendar)
                else:
                    count += 1
                    kpi_c.g_discarded[r_name].append(GranuleInfo(weekday, g_index))

        confidence, support = kpi_c.compute_confidence_support(r_name)

        if confidence > 0 and support < desired_support:
            kpi_c.g_discarded[r_name].sort(
                key=lambda x: kpi_c.res_granules_frequency[r_name][x.granule_index][x.week_day],
                reverse=True,
            )

            accepted_indexes = []
            i = 0
            for g_info in kpi_c.g_discarded[r_name]:
                best_task = kpi_c.can_improve_support(r_name, g_info.week_day, g_info.granule_index)

                if best_task is not None:
                    self._add_calendar_item(g_info.week_day, g_info.granule_index, r_calendar)
                    kpi_c.check_accepted_granule(r_name, g_info.week_day, g_info.granule_index, best_task)
                    accepted_indexes.append(i)
                _, support = kpi_c.compute_confidence_support(r_name)

                if support >= desired_support:
                    break

                i += 1

            kpi_c.update_discarded_granules_list(r_name, accepted_indexes)

        return r_calendar

    def _add_calendar_item(self, week_day: int, g_index: int, r_calendar: RCalendar):
        str_wday = int_week_days[week_day]
        hour = (g_index * self.minutes_x_granule) // 60
        from_min = (g_index * self.minutes_x_granule) % 60
        to_min = from_min + self.minutes_x_granule

        if to_min >= 60:
            if hour == 23:
                r_calendar.add_calendar_item(str_wday, str_wday, "%d:%d:%d" % (hour, from_min, 0), "23:59:59.999")
            else:
                r_calendar.add_calendar_item(
                    str_wday,
                    str_wday,
                    "%d:%d:%d" % (hour, from_min, 0),
                    "%d:%d:%d" % (hour + 1, 0, 0),
                )
        else:
            r_calendar.add_calendar_item(
                str_wday,
                str_wday,
                "%d:%d:%d" % (hour, from_min, 0),
                "%d:%d:%d" % (hour, to_min, 0),
            )

    def build_unrestricted_resource_calendar(self, r_name, t_name) -> RCalendar:
        r_kpi = self.kpi_calendar
        r_calendar = RCalendar("%s_Schedule" % r_name)

        for g_index in r_kpi.res_active_granules_weekdays[r_name]:
            for week_day in r_kpi.res_active_granules_weekdays[r_name][g_index]:
                r_kpi.check_accepted_granule(r_name, week_day, g_index, t_name)
                self._add_calendar_item(week_day, g_index, r_calendar)

        return r_calendar

    def task_coverage(self, t_name):
        return self.kpi_calendar.task_coverage(t_name)

    def register_task_enablement(self, trace_events):
        self.kpi_calendar.register_task_enablement(trace_events)
