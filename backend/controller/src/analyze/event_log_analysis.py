"""
Event Log Analysis Module

This module provides functionality for analyzing event logs from business processes.
It supports both Simod and Agent-based simulation parameters for resource allocation and cost analysis.

Input:
    - event_log (pd.DataFrame): A pandas DataFrame containing the event log with columns:
        - case_id: Unique identifier for each process instance.
        - activity: Name of the activity being performed
        - resource: Resource (person/machine) performing the activity
        - start_time: Timestamp when activity started
        - end_time: Timestamp when activity ended
        - enabled_time: (Optional) Timestamp when activity was enabled
    - simod_params (dict, optional): Parameters for Simod simulation including:
        - resource_profiles: Resource configurations
        - resource_calendars: Working hours and schedules
    - agent_param (dict, optional): Parameters for Agent-based simulation including:
        - simulation_parameters: Resource configurations and calendars

Output:
    The class provides various analysis methods that return metrics such as:
    - Cycle times (mean and median)
    - Resource utilization
    - Cost analysis
    - Waiting times
    - Activity-specific metrics
"""

import datetime
from typing import Tuple

import pandas as pd
import pm4py
from src.analyze.schedule import Schedule


class EventLogAnalysis:
    """
    A class for analyzing event logs from business processes.

    This class provides methods to calculate various process metrics including cycle times,
    resource utilization, costs, and waiting times. It supports both Simod and Agent-based
    simulation parameters for resource allocation and cost analysis.
    """

    def __init__(self, event_log: pd.DataFrame, simod_params: dict = None, agent_param: dict = None):
        """
        Initialize the EventLogAnalysis with an event log and optional simulation parameters.

        Args:
            event_log (pd.DataFrame): Process event log data
            simod_params (dict, optional): Simod simulation parameters
            agent_param (dict, optional): Agent-based simulation parameters
        """
        self._event_log = event_log
        self._setheaders()
        self.pm_event_log = self._get_pm4py_event_log()

        self._prep_df()
        self._salaries = None
        self._schedule = None
        self._resouce_hours_worked = None

        if simod_params:
            self._salaries = self._set_simod_salary(simod_params)
            self._schedule = Schedule(simod_params["resource_calendars"][0]["time_periods"], mode="simod")
            self._resouce_hours_worked = self._schedule.get_simod_resource_worked_hours(self._event_log)

        elif agent_param:
            self._salaries = self._set_agent_salary(agent_param)  # ?
            self._schedule = Schedule(agent_param["simulation_parameters"]["res_calendars"], mode="agent")  # ?
            self._resouce_hours_worked = self._schedule.get_agent_resource_worked_hours(self._event_log)

        self._simod_params: dict = simod_params
        self._agent_params: dict = agent_param

    def _prep_df(self):
        """
        Prepare the DataFrame by converting timestamps and sorting by case and start time.
        Converts start_time and end_time columns to datetime objects and sorts the data.
        """
        df = self._event_log
        df["start_time"] = pd.to_datetime(df["start_time"], format="ISO8601", utc=True)
        df["end_time"] = pd.to_datetime(df["end_time"], format="ISO8601", utc=True)

        self._event_log = df.sort_values(by=["case_id", "start_time"])

    def _setheaders(self):
        """
        Standardize column names in the event log.
        Renames common variations of column names to standardized versions.
        """
        if "activity_name" in self._event_log:
            self._event_log.rename(columns={"activity_name": "activity"}, inplace=True)
        if "start_timestamp" in self._event_log:
            self._event_log.rename(columns={"start_timestamp": "start_time"}, inplace=True)
        if "end_timestamp" in self._event_log:
            self._event_log.rename(columns={"end_timestamp": "end_time"}, inplace=True)

    def _get_pm4py_event_log(self):
        """
        Convert the event log to PM4Py format for process mining analysis.

        Returns:
            pm4py.event_log: Event log in PM4Py format
        """
        df = self._event_log.copy()
        df.rename(
            columns={
                "case_id": "case:concept:name",
                "activity": "concept:name",
                "resource": "org:resource",
                "start_time": "start_timestamp",
                "end_time": "time:timestamp",
            },
            inplace=True,
        )

        df = pm4py.format_dataframe(
            df, case_id="case:concept:name", activity_key="concept:name", timestamp_key="time:timestamp"
        )

        event_log = pm4py.convert_to_event_log(df)
        return event_log

    # Helper function to print all events for a specific case
    def _print_case(self, case: int):
        # Helper function to print all events for a specific case
        # Set pandas display options to show all columns and rows without truncation
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)

        df = self._event_log
        new_order = ["case_id", "activity", "resource", "start_time", "end_time", "enabled_time"]
        df = df[[col for col in new_order if col in df.columns]]

        clerc_rows = df[df["case_id"] == case]

        print(clerc_rows)
        print("\n")

    # Helper function to print all events for a specific resource
    def _print_resource(self, resource: str):
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)

        df = self._event_log
        new_order = ["case_id", "activity", "resource", "start_time", "end_time", "enabled_time"]
        df = df[[col for col in new_order if col in df.columns]]
        clerc_rows = df[df["resource"] == resource]
        print(clerc_rows)
        print("\n")

    def case_cycle_time(self) -> Tuple[float, float]:
        """
        Calculate the mean and median cycle time for all cases.

        Cycle time is the total duration from start to end of a case.

        Returns:
            Tuple[float, float]: (mean_cycle_time, median_cycle_time) in seconds
        """
        df = self._event_log

        cycle_times = [
            (case["end_time"].max() - case["start_time"].min()).total_seconds()
            for (case_id, case) in df.groupby(["case_id"])
        ]
        cycle_times.sort()

        median_cycle_time = cycle_times[len(cycle_times) // 2]
        mean_cycle_time = sum(cycle_times) / len(cycle_times)
        return (mean_cycle_time, median_cycle_time)

    def full_analysis(self) -> dict:
        """
        Perform a complete analysis of the event log.

        Calculates various metrics including:
        - Cost analysis (if salary information is available)
        - Cycle times
        - Resource utilization
        - Waiting times

        Returns:
            dict: Dictionary containing all calculated metrics
        """
        metrics = {}
        # Cost analysis - only available if simulation parameters are provided rounded to 2 decimal places
        if self._salaries and self._resouce_hours_worked:
            (total_cost, per_emp_cost) = self.cost(self._salaries)
            metrics["cost"] = round(total_cost, 2)
            metrics["employe_cost"] = per_emp_cost.update({k: round(v, 2) for k, v in per_emp_cost.items()})

        # Resource utilization - only available if simulation parameters are provided, in percentage
        if self._schedule:
            metrics["resource_utilization"] = self.resource_utilization_fixed_schedule()

        # Cycle times - always available as they only need event log, in hours
        (cycle_time_mean, cycle_time_median) = self.case_cycle_time()
        metrics["cycle_time_average"] = self._seconds_to_hours(cycle_time_mean)
        metrics["cycle_time_median"] = self._seconds_to_hours(cycle_time_median)

        # Activity cycle times - always available as they only need event log, in hours
        # Only provide mean cycletime per activity
        (act_mean, act_median, act_mean_procentages, act_median_procentages) = self.activity_cycle_time()
        metrics["cycle_time_per_activity"] = self._seconds_to_hours(act_mean)

        # Waiting times - always available as they only need event log, in hours
        case_average, activity_average_times = self.waiting_time()
        metrics["waiting_time"] = self._seconds_to_hours(case_average)
        metrics["per_activity_waiting_time"] = self._seconds_to_hours(activity_average_times)

        return metrics

    def _seconds_to_hours(self, seconds):
        """
        converting seconds to hours, rounding to 1 decimal place
        returns a float or a dictionary of floats depending on the input
        """
        if isinstance(seconds, dict):
            return {k: round((s / 3600), 1) for k, s in seconds.items()}
        elif isinstance(seconds, (int, float)):
            return round((seconds / 3600), 1)
        else:
            raise TypeError("Input must be a float, int, or a dictionary of floats.")

    def _set_simod_salary(self, params: dict) -> dict:
        # Helper function to extract salary information from Simod parameters
        salaries = {}
        resource_profiles = params["resource_profiles"]
        resource_profiles = resource_profiles[0]
        resource_list = resource_profiles["resource_list"]

        for resource in resource_list:
            salaries[resource["id"]] = int(resource["cost_per_hour"])
        return salaries

    def _set_agent_salary(self, params: dict) -> dict:
        # Helper function to extract salary information from Agent parameters
        salaries = {}
        sim_params = params["simulation_parameters"]
        if "res_salaries" in sim_params:
            resource_list = sim_params["res_salaries"]
            for resource in resource_list:
                salaries[resource["id"]] = int(resource["cost_per_hour"])
        return salaries

    def cost(self, sals: dict) -> float:
        """
        Calculate the total cost and per-employee cost based on working hours.

        Args:
            sals (dict): Dictionary mapping resource names to their hourly rates

        Returns:
            Tuple[float, dict]: (total_cost, per_employee_cost)
            If no simulation parameters are provided (simod or agent), returns {} to indicate error
        """

        if not self._salaries or not self._resouce_hours_worked:
            return {}

        worker_payment = {}
        for name, seconds in self._resouce_hours_worked.items():
            hours = seconds / 3600
            pay = sals[name] * hours
            if name in worker_payment:
                worker_payment[name] += pay
            else:
                worker_payment[name] = pay

        return sum(worker_payment.values()), worker_payment

    def resource_utilization(self) -> float:
        """
        Calculate resource utilization metrics.

        Returns:
            float: Resource utilization percentage
            Returns -1 if no simulation parameters are provided (simod or agent) to indicate error
        """
        if not self._schedule:
            return -1

        worked = self._resouce_hours_worked
        scheduled = {}
        dates_worked = {}

        for i, row in self._event_log.iterrows():
            worker = row["resource"] if self._schedule.mode == "simod" else int(row["agent"])
            start_time = row["start_time"]
            end_time = row["end_time"]

            intervals = self._schedule._split_into_daily_intervals(start_time, end_time)

            total_schedule = 0
            for start, end in intervals:
                date = start.date()
                weekday = start.weekday()
                try:
                    time_periods = self._schedule._daily_schedules[0 if self._schedule.mode == "simod" else worker][
                        weekday
                    ]
                except (KeyError, IndexError):
                    continue

                for schedule_start, schedule_end in time_periods:
                    schedule_duration = (
                        datetime.datetime.combine(datetime.datetime.min, schedule_end.time())
                        - datetime.datetime.combine(datetime.datetime.min, schedule_start.time())
                    ).total_seconds()

                    total_schedule += schedule_duration

            if worker not in dates_worked:
                dates_worked[worker] = set()

            if date not in dates_worked[worker]:
                if worker in scheduled:
                    scheduled[worker] += total_schedule
                else:
                    scheduled[worker] = total_schedule

                dates_worked[worker].add(date)

        total_active_time = 0
        total_scheduled_time = 0

        for resource, active_time in worked.items():
            scheduled_time = scheduled.get(resource if self._schedule.mode == "simod" else int(resource), 0)
            if scheduled_time > 0:
                total_active_time += active_time
                total_scheduled_time += scheduled_time

        return total_active_time * 100 / total_scheduled_time if total_scheduled_time > 0 else 0

    def resource_utilization_fixed_schedule(self):
        """
        Calculates resource utilization assuming every resource is available during their calendar hours
        from the start of the first case to the end of the last case.

        Returns:
            float: Resource utilization as a percentage.
        """
        df = self._event_log

        active_time_per_resource = self._resouce_hours_worked
        total_active_time = 0
        for _, time in active_time_per_resource.items():
            total_active_time += time

        start_date = df.iloc[0]["start_time"]
        end_date = df.iloc[-1]["end_time"]
        start_date = start_date.to_pydatetime()
        end_date = end_date.to_pydatetime()

        if self._simod_params is not None:
            resource_count = len(self._simod_params["resource_profiles"][0]["resource_list"])
            available_time = self._schedule.get_available_time(start_date, end_date, resource_count)
        else:
            available_time = self._schedule.get_available_time(start_date, end_date)

        return (total_active_time / available_time) * 100

    def activity_cycle_time(self) -> Tuple[dict, dict]:
        """
        Calculate cycle times for each activity.

        Returns:
            Tuple[dict, dict]: (mean_times, median_times, mean_percentages, median_percentages)
            where each dictionary maps activity names to their respective metrics. Returns in seconds and percentages.
        """
        event_log = self.pm_event_log

        meadian = pm4py.get_service_time(
            event_log,
            start_timestamp_key="start_timestamp",
            timestamp_key="time:timestamp",
            activity_key="concept:name",
            case_id_key="case:concept:name",
            aggregation_measure="median",
        )
        mean = pm4py.get_service_time(
            event_log,
            start_timestamp_key="start_timestamp",
            timestamp_key="time:timestamp",
            activity_key="concept:name",
            case_id_key="case:concept:name",
            aggregation_measure="mean",
        )
        mean_procentages = self.__get_activity_percentages(mean)
        meadian_procentages = self.__get_activity_percentages(meadian)
        return (mean, meadian, mean_procentages, meadian_procentages)

    def __get_activity_percentages(self, activity_sums: dict):
        # Helper function to calculate percentage distribution of time across activities
        sum = 0
        percentage_dict = {}

        for activity in activity_sums:
            sum += activity_sums[activity]

        for activity in activity_sums:
            time = activity_sums[activity]
            percentage_dict[activity] = time / sum

        return percentage_dict

    def waiting_time(self):
        """
        Calculate waiting times between activities.

        Returns:
            Tuple[float, dict]: (average_case_waiting_time, per_activity_waiting_times) in seconds
        """
        df = self._event_log
        cases = []
        case_index = -1
        activity_counts = {}
        previous_case_id = None
        previous_end_time = None

        for row_index, row in df.iterrows():
            case_id = row["case_id"]
            start_time = row["start_time"]
            end_time = row["end_time"]
            activity = row["activity"]

            activity_counts[activity] = activity_counts.get(activity, 0) + 1

            if case_id != previous_case_id:
                case_index += 1
                cases.append({})
                cases[case_index][activity] = pd.Timedelta(0)
            else:
                waiting_time = start_time - previous_end_time
                if activity not in cases[case_index]:
                    cases[case_index][activity] = max(pd.Timedelta(0), waiting_time)
                else:
                    cases[case_index][activity] += max(pd.Timedelta(0), waiting_time)

            previous_case_id = case_id
            previous_end_time = end_time

        activity_average_times = self._get_average_activity_waiting_time(cases, activity_counts)
        total_waiting_time = self._get_average_case_waiting_time(cases)
        return total_waiting_time, activity_average_times

    # Helper function to calculate average waiting time across all cases
    def _get_average_case_waiting_time(self, cases: list) -> float:
        waiting_sum = 0
        for case in cases:
            for activity in case:
                waiting_sum += case[activity].total_seconds()

        return waiting_sum / float(len(cases))

    def _get_average_activity_waiting_time(self, cases: list, activity_counts: dict) -> dict:
        # Helper function to calculate average waiting time per activity
        average_activity_waiting_time = {}
        for case in cases:
            for activity in case:
                if activity not in average_activity_waiting_time:
                    average_activity_waiting_time[activity] = case[activity].total_seconds()
                else:
                    average_activity_waiting_time[activity] += case[activity].total_seconds()

        for activity in average_activity_waiting_time:
            average_activity_waiting_time[activity] /= float(activity_counts[activity])

        return average_activity_waiting_time
