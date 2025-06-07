# taken from https://github.com/AutomatedProcessImprovement/Prosimos/blob/main/bpdfr_discovery/log_parser.py#L331

import datetime

import pytz
from source.agent_types.calendar_discovery_parameters import CalendarDiscoveryParameters
from source.agent_types.factory import CalendarFactory


def discover_calendar_per_agent(df):
    params = CalendarDiscoveryParameters
    calendar_factory = CalendarFactory(params.granularity)
    min_confidence, min_support, min_participation = params.confidence, params.support, params.participation

    resource_cases = dict()
    resource_freq = dict()
    max_resource_freq = 0
    task_resource_freq = dict()
    task_resource_events = dict()
    task_events = dict()
    observed_task_resources = dict()
    min_max_task_duration = dict()
    total_events = 0
    removed_traces = 0
    removed_events = 0

    df = df.sort_values(by="start_timestamp")

    for case_id, group in df.groupby("case_id"):
        # print(f"Case ID: {case_id}")
        # print(group)
        started_events = dict()
        trace_info = Trace(case_id)
        for index, event in group.iterrows():
            # print(f"event: {event}")
            resource = event["agent"]
            task_name = event["activity_name"]
            start_timestamp = event["start_timestamp"]
            end_timestamp = event["end_timestamp"]

            if task_name not in task_resource_freq:
                task_resource_events[task_name] = dict()
                task_resource_freq[task_name] = [0, dict()]
                task_events[task_name] = list()
                observed_task_resources[task_name] = set()
                # min_max_task_duration[task_name] = [sys.float_info.max, 0]
            if resource not in task_resource_freq[task_name][1]:
                task_resource_freq[task_name][1][resource] = 0
                task_resource_events[task_name][resource] = list()
            task_resource_freq[task_name][1][resource] += 1
            task_resource_freq[task_name][0] = max(
                task_resource_freq[task_name][0], task_resource_freq[task_name][1][resource]
            )

            calendar_factory.check_date_time(resource, task_name, end_timestamp)

            started_events[task_name] = trace_info.start_event(task_name, task_name, start_timestamp, resource)
            if task_name in started_events:
                c_event = trace_info.complete_event(started_events.pop(task_name), end_timestamp)
                task_events[task_name].append(c_event)
                task_resource_events[task_name][resource].append(c_event)

    return discover_resource_calendars(
        calendar_factory, task_resource_events, min_confidence, min_support, min_participation
    )


def discover_resource_calendars(calendar_factory, task_resource_events, min_confidence, min_support, min_participation):
    # print("Discovering Resource Calendars ...")
    calendar_candidates = calendar_factory.build_weekly_calendars(min_confidence, min_support, min_participation)

    joint_event_candidates = dict()
    joint_task_resources = dict()
    pools_json = dict()

    task_event_freq = dict()
    task_event_covered_freq = dict()
    joint_resource_freq = dict()
    coverage_map = dict()

    for task_name in task_resource_events:
        unfit_resource_events = list()
        joint_task_resources[task_name] = list()

        task_event_freq[task_name] = 0
        task_event_covered_freq[task_name] = 0

        # my code
        agent_name = []

        for r_name in task_resource_events[task_name]:
            joint_task_resources[task_name].append(r_name)
            if (
                r_name not in calendar_candidates
                or calendar_candidates[r_name] is None
                or calendar_candidates[r_name].total_weekly_work == 0
            ):
                unfit_resource_events += task_resource_events[task_name][r_name]
                agent_name.append(r_name)
            else:
                task_event_covered_freq[task_name] += 2 * len(task_resource_events[task_name][r_name])
            task_event_freq[task_name] += 2 * len(task_resource_events[task_name][r_name])
        # print(f"unfit resources: {agent_name}")
        if len(unfit_resource_events) > 0:
            joint_events = _max_disjoint_intervals(unfit_resource_events)
            for i in range(0, len(joint_events)):
                j_name = f"Joint_{task_name}_{i}"
                # j_name = agent_name[i]
                joint_resource_freq[j_name] = 2 * len(joint_events[i])
                joint_event_candidates[j_name] = joint_events[i]
                joint_task_resources[task_name].append(j_name)
                for ev_info in joint_events[i]:
                    calendar_factory.check_date_time(j_name, task_name, ev_info.started_at, True)
                    calendar_factory.check_date_time(j_name, task_name, ev_info.completed_at, True)

    calendar_candidates = calendar_factory.build_weekly_calendars(min_confidence, min_support, min_participation)

    resource_calendars = dict()
    task_resources = dict()
    joint_resource_events = dict()

    discarded_joint = dict()
    for task_name in joint_task_resources:
        discarded_joint[task_name] = list()
        pools_json[task_name] = {"name": task_name, "resource_list": list()}
        resource_list = list()
        task_resources[task_name] = list()
        for r_name in joint_task_resources[task_name]:
            if (
                r_name in calendar_candidates
                and calendar_candidates[r_name] is not None
                and calendar_candidates[r_name].total_weekly_work > 0
            ):
                resource_list.append(_create_resource_profile_entry(r_name, r_name))
                resource_calendars[r_name] = calendar_candidates[r_name]
                task_resources[task_name].append(r_name)
                if r_name in joint_event_candidates:
                    task_event_covered_freq[task_name] += joint_resource_freq[r_name]
                    joint_resource_events[r_name] = joint_event_candidates[r_name]
            elif r_name in joint_event_candidates:
                discarded_joint[task_name].append([r_name, joint_resource_freq[r_name]])

        if calendar_factory.task_coverage(task_name) < min_support:
            discarded_joint[task_name].sort(key=lambda x: x[1], reverse=True)
            for d_info in discarded_joint[task_name]:
                resource_calendars[d_info[0]] = calendar_factory.build_unrestricted_resource_calendar(
                    d_info[0], task_name
                )
                task_event_covered_freq[task_name] += joint_resource_freq[d_info[0]]
                resource_list.append(_create_resource_profile_entry(d_info[0], d_info[0]))
                task_resources[task_name].append(d_info[0])
                joint_resource_events[d_info[0]] = joint_event_candidates[d_info[0]]
                if calendar_factory.task_coverage(task_name) >= min_support:
                    break

        if task_event_covered_freq[task_name] != 0 and task_event_freq[task_name] != 0:
            coverage_map[task_name] = task_event_covered_freq[task_name] / task_event_freq[task_name]
        else:
            coverage_map[task_name] = 0
        pools_json[task_name]["resource_list"] = resource_list

    return resource_calendars, task_resources, joint_resource_events, pools_json, coverage_map


def _max_disjoint_intervals(interval_list):
    if len(interval_list) == 1:
        return [interval_list]
    interval_list.sort(key=lambda ev_info: ev_info.completed_at)
    disjoint_intervals = list()
    while True:
        max_set = list()
        discarded_list = list()
        max_set.append(interval_list[0])
        current_last = interval_list[0].completed_at
        for i in range(1, len(interval_list)):
            if interval_list[i].started_at >= current_last:
                max_set.append(interval_list[i])
                current_last = interval_list[i].completed_at
            else:
                discarded_list.append(interval_list[i])
        if len(max_set) > 1:
            disjoint_intervals.append(max_set)
        if len(max_set) == 1 or len(discarded_list) == 0:
            break
        interval_list = discarded_list
    return disjoint_intervals


def _create_resource_profile_entry(r_id, r_name, amount=1, cost_per_hour=1):
    return {"id": r_id, "name": r_name, "cost_per_hour": cost_per_hour, "amount": amount}


# class EnabledEvent:
#     def __init__(self, p_case, p_state, task_id, enabled_at, enabled_datetime,
#         batch_info_exec: BatchInfoForExecution = None, duration_sec = None, is_inter_event = False):
#         self.p_case = p_case
#         self.p_state = p_state
#         self.task_id = task_id
#         self.enabled_datetime = enabled_datetime
#         self.enabled_at = enabled_at
#         self.batch_info_exec = batch_info_exec
#         self.duration_sec = duration_sec        # filled only in case of event-based gateway
#         self.is_inter_event = is_inter_event    # whether the enabled event is the intermediate event


class ProcessInfo:
    def __init__(self):
        self.traces = dict()
        self.resource_profiles = dict()


class TaskEvent:
    def __init__(
        self,
        p_case,
        task_id,
        resource_id,
        resource_available_at=None,
        enabled_at=None,
        enabled_datetime=None,
        bpm_env=None,
        num_tasks_in_batch=0,
    ):
        self.p_case = p_case  # ID of the current trace, i.e., index of the trace in log_info list
        self.task_id = task_id  # Name of the task related to the current event
        # self.type = BPMN.TASK # showing whether it's task or event
        self.resource_id = resource_id  # ID of the resource performing to the event
        self.waiting_time = None
        self.processing_time = None
        self.normalized_waiting = None
        self.normalized_processing = None
        self.worked_intervals = []

        if resource_available_at is not None:
            # Time moment in seconds from beginning, i.e., first event has time = 0
            self.enabled_at = enabled_at
            # Datetime of the time-moment calculated from the starting simulation datetime
            self.enabled_datetime = enabled_datetime

            # Time moment in seconds from beginning, i.e., first event has time = 0
            self.started_at = max(resource_available_at, enabled_at)
            # Datetime of the time-moment calculated from the starting simulation datetime
            self.started_datetime = bpm_env.simulation_datetime_from(self.started_at)

            # Ideal duration from the distribution-function if allocate resource doesn't rest
            self.ideal_duration = bpm_env.sim_setup.ideal_task_duration(task_id, resource_id, num_tasks_in_batch)
            # Actual duration adding the resource resting-time according to their calendar
            self.real_duration = bpm_env.sim_setup.real_task_duration(
                self.ideal_duration, self.resource_id, self.started_datetime, self.worked_intervals
            )

            # Time moment in seconds from beginning, i.e., first event has time = 0
            self.completed_at = self.started_at + self.real_duration
            # Datetime of the time-moment calculated from the starting simulation datetime
            self.completed_datetime = bpm_env.simulation_datetime_from(self.completed_at)

            # Time of a resource was resting while performing a task (in seconds)
            self.idle_time = self.real_duration - self.ideal_duration
            # Time from an event is enabled until it is started by any resource
            self.waiting_time = self.started_at - self.enabled_at
            self.idle_cycle_time = self.completed_at - self.enabled_at
            self.idle_processing_time = self.completed_at - self.started_at
            self.cycle_time = self.idle_cycle_time - self.idle_time
            self.processing_time = self.idle_processing_time - self.idle_time
        else:
            self.task_name = None
            self.enabled_at = enabled_at
            self.enabled_by = None
            self.started_at = None
            self.completed_at = None
            self.idle_time = None

    # @classmethod
    # def create_event_entity(cls, c_event: EnabledEvent, ended_at, ended_datetime):
    #     cls.p_case = c_event.p_case  # ID of the current trace, i.e., index of the trace in log_info list
    #     cls.task_id = c_event.task_id  # Name of the task related to the current event
    #     cls.type = BPMN.INTERMEDIATE_EVENT
    #     cls.enabled_at = c_event.enabled_at
    #     cls.enabled_datetime = c_event.enabled_datetime
    #     cls.started_at = c_event.enabled_at
    #     cls.started_datetime = c_event.enabled_datetime
    #     cls.completed_at = ended_at
    #     cls.completed_datetime = ended_datetime
    #     cls.idle_time = 0.0
    #     cls.waiting_time = 0.0
    #     cls.idle_cycle_time = 0.0
    #     cls.idle_processing_time = 0.0
    #     cls.cycle_time = 0.0
    #     cls.processing_time = 0.0

    # return cls

    def update_enabling_times(self, enabled_at):
        # what's the use case ?
        if self.started_at is None or enabled_at > self.started_at:
            # print(self.task_id)
            # print(str(enabled_at))
            # print(str(self.started_at))
            # print("--------------------------------------------")
            enabled_at = self.started_at
            # raise Exception("Task ENABLED after STARTED")
        self.enabled_at = enabled_at
        self.waiting_time = (self.started_at - self.enabled_at).total_seconds()
        self.processing_time = (self.completed_at - self.started_at).total_seconds()


class LogEvent:
    def __int__(self, task_id, started_datetime, resource_id):
        self.task_id = task_id
        self.started_datetime = started_datetime
        self.resource_id = resource_id
        self.completed_datetime = None


class Trace:
    def __init__(self, p_case, started_at=datetime.datetime(9999, 12, 31, 23, 59, 59, 999999, pytz.utc)):
        self.p_case = p_case
        self.started_at = started_at
        self.completed_at = started_at
        self.event_list = list()

        self.cycle_time = None
        self.idle_cycle_time = None
        self.processing_time = None
        self.idle_processing_time = None
        self.waiting_time = None
        self.idle_time = None

    def start_event(self, task_id, task_name, started_at, resource_name):
        event_info = TaskEvent(self.p_case, task_id, resource_name)
        event_info.task_name = task_name
        event_info.started_at = started_at
        event_index = len(self.event_list)
        self.event_list.append(event_info)
        self.started_at = min(self.started_at, started_at)
        return event_index

    def complete_event(self, event_index, completed_at, idle_time=0):
        self.event_list[event_index].completed_at = completed_at
        self.event_list[event_index].idle_time = idle_time
        self.completed_at = max(self.completed_at, self.event_list[event_index].completed_at)
        return self.event_list[event_index]

    def sort_by_completion_date(self, completed_at=False):
        if completed_at:
            self.event_list.sort(key=lambda e_info: e_info.completed_at)
        else:
            self.event_list.sort(key=lambda e_info: e_info.started_at)
        self.started_at = self.event_list[0].started_at
        self.completed_at = self.event_list[len(self.event_list) - 1].completed_at

    def filter_incomplete_events(self):
        filtered_list = list()
        filtered_events = 0
        for ev_info in self.event_list:
            if ev_info.started_at is not None and ev_info.completed_at is not None:
                filtered_list.append(ev_info)
            else:
                filtered_events += 2
        self.event_list = filtered_list
        return filtered_events
