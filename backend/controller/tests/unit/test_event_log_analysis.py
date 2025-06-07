"""
Unit tests for the EventLogAnalysis class.
"""

import pandas as pd
import pytest
from src.analyze.event_log_analysis import EventLogAnalysis


def mock_event_log():
    """
    Returns a short mocked eventlog as a pandas dataframe.
    """
    columns = ["case_id", "resource", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "res1", "Act1", "2025-01-01 00:00:00", "2025-01-01 00:00:05"],
        ["Case1", "res2", "Act2", "2025-01-01 00:00:10", "2025-01-01 00:00:20"],
        ["Case1", "res3", "Act3", "2025-01-01 00:00:20", "2025-01-01 00:00:30"],
        ["Case1", "res1", "Act4", "2025-01-01 00:00:35", "2025-01-01 00:00:40"],
        ["Case2", "res1", "Act1", "2025-01-01 00:01:00", "2025-01-01 00:01:05"],
        ["Case2", "res2", "Act2", "2025-01-01 00:01:10", "2025-01-01 00:01:15"],
        ["Case2", "res3", "Act3", "2025-01-01 00:01:15", "2025-01-01 00:01:18"],
        ["Case2", "res3", "Act5", "2025-01-01 00:01:25", "2025-01-01 00:01:30"],
        ["Case2", "res1", "Act4", "2025-01-01 00:01:35", "2025-01-01 00:01:36"],
    ]

    return pd.DataFrame(data, columns=columns)


def mock_event_log_overlapping_cases():  # SIMOD
    """
    Returns a short mocked eventlog as a pandas dataframe.
    """
    columns = ["case_id", "resource", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "res1", "Act1", "2025-01-01 09:00:00", "2025-01-01 09:30:00"],  # 30 min
        ["Case1", "res2", "Act2", "2025-01-01 09:30:00", "2025-01-01 10:00:00"],  # 30 min
        ["Case1", "res1", "Act3", "2025-01-01 10:00:00", "2025-01-01 10:30:00"],  # 30 min
        ["Case2", "res3", "Act1", "2025-01-01 09:30:00", "2025-01-01 10:30:00"],  # 60 min
        ["Case2", "res1", "Act2", "2025-01-01 11:00:00", "2025-01-01 12:00:00"],  # 60 min
    ]

    return pd.DataFrame(data, columns=columns)


def mock_simod_log_cost():
    """
    Returns a short mocked eventlog as a pandas dataframe.
    """
    columns = ["case_id", "resource", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "res1", "Act1", "2025-01-01 23:00:00", "2025-01-02 12:00:00"],
        ["Case1", "res2", "Act2", "2025-01-02 13:00:00", "2025-01-02 14:00:00"],
        ["Case1", "res3", "Act3", "2025-01-02 14:30:00", "2025-01-02 17:00:00"],
        ["Case1", "res1", "Act4", "2025-01-03 08:00:00", "2025-01-03 09:00:00"],
        ["Case2", "res1", "Act1", "2025-01-03 10:00:00", "2025-01-04 10:00:00"],
        ["Case2", "res2", "Act2", "2025-01-04 12:00:00", "2025-01-04 13:00:00"],
        ["Case2", "res3", "Act3", "2025-01-04 14:00:00", "2025-01-04 15:00:00"],
        ["Case2", "res3", "Act5", "2025-01-04 16:00:00", "2025-01-04 17:00:00"],
        ["Case2", "res1", "Act4", "2025-01-05 08:00:00", "2025-01-05 10:00:00"],
    ]

    return pd.DataFrame(data, columns=columns)


def mock_agent_log_cost():
    """
    Returns a short mocked eventlog as a pandas dataframe.
    """
    columns = ["case_id", "agent", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "0", "Act1", "2025-01-01 09:00:00", "2025-01-02 12:00:00"],
        ["Case1", "1", "Act2", "2025-01-02 12:00:00", "2025-01-02 14:00:00"],
        ["Case1", "2", "Act4", "2025-01-03 08:00:00", "2025-01-03 09:00:00"],
        ["Case2", "2", "Act1", "2025-01-03 10:00:00", "2025-01-04 10:00:00"],
        ["Case2", "1", "Act2", "2025-01-04 13:00:00", "2025-01-04 17:00:00"],
        ["Case2", "2", "Act4", "2025-01-05 08:00:00", "2025-01-05 10:00:00"],
    ]
    return pd.DataFrame(data, columns=columns)


def get_agent_params() -> dict:
    """
    Returns mocked parameters containing resource calendars and resource salaries for agent_sim.
    """
    params = {}
    simulation_parameters = {}
    res_salaries = [
        {"id": "0", "name": "0", "cost_per_hour": "20"},
        {"id": "1", "name": "1", "cost_per_hour": "20"},
        {"id": "2", "name": "2", "cost_per_hour": "20"},
    ]
    simulation_parameters["res_salaries"] = res_salaries
    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

    p1 = ("08:00:00", "10:00:00")
    p2 = ("11:00:00", "13:00:00")
    p3 = ("14:00:00", "15:00:00")
    plist = [p1, p2, p3]

    res_calendars = {}

    for i, person in enumerate(res_salaries):
        pers_dict = {}
        data = {}
        time_periods = []
        for day in days:
            pass1 = {"from": day, "to": day, "beginTime": plist[i][0], "endTime": plist[i][1]}
            time_periods.append(pass1)

        data["time_periods"] = time_periods
        pers_dict["data"] = data
        res_calendars[str(i)] = pers_dict
    simulation_parameters["res_calendars"] = res_calendars
    params["simulation_parameters"] = simulation_parameters
    return params


def get_simod_params() -> dict:
    """
    Returns mocked parameters containing resource calendars and resource salaries for simod.
    """
    params = {}
    resource_list = [
        {"id": "res1", "name": "res1", "cost_per_hour": "20"},
        {"id": "res2", "name": "res2", "cost_per_hour": "20"},
        {"id": "res3", "name": "res3", "cost_per_hour": "20"},
    ]
    resource_profiles = [{"resource_list": resource_list}]
    params["resource_profiles"] = resource_profiles

    days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

    time_periods = []

    for day in days:
        pass1 = {"from": day, "to": day, "beginTime": "08:00:00", "endTime": "10:00:00"}
        pass2 = {"from": day, "to": day, "beginTime": "11:00:00", "endTime": "12:00:00"}
        pass3 = {"from": day, "to": day, "beginTime": "13:00:00", "endTime": "15:00:00"}

        time_periods.append(pass1)
        time_periods.append(pass2)
        time_periods.append(pass3)

    resource_calendars = [{"time_periods": time_periods}]
    params["resource_calendars"] = resource_calendars

    return params


def test_waiting_time_average():
    """
    Tests if the average waiting time matches the expected value.
    """
    mock_log = mock_event_log()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)

    total, by_activity = log_analyzer.waiting_time()

    assert total == 13.5


def test_waiting_time_by_activity():
    """
    Tests if average waiting time by activity matches the expected value.
    """
    mock_log = mock_event_log()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)

    total, by_activity = log_analyzer.waiting_time()

    assert by_activity["Act1"] == 0
    assert by_activity["Act2"] == 5
    assert by_activity["Act3"] == 0
    assert by_activity["Act4"] == 5
    assert by_activity["Act5"] == 7


def test_activity_cycle_time():
    """
    Tests if average cycle time by activity matches the expected value.
    """
    mock_log = mock_event_log()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)

    act_mean, act_median, act_mean_percentages, act_median_percentages = log_analyzer.activity_cycle_time()

    assert act_mean == {"Act1": 5, "Act2": 7.5, "Act3": 6.5, "Act4": 3, "Act5": 5}
    mean_sum = 0
    for key in act_mean:
        mean_sum += act_mean[key]

    for key in act_mean_percentages:
        assert act_mean_percentages[key] == (act_mean[key] / mean_sum)

    median_sum = 0
    for key in act_median:
        median_sum += act_median[key]

    for key in act_median_percentages:
        assert act_median_percentages[key] == (act_median[key] / median_sum)


def test_resouce_util_agent():
    """
    Tests if resource utilization matches the expected value.
    Each agent has different working hours:
    - Agent 0: 2 hours/day (8:00-10:00)
    - Agent 1: 2 hours/day (11:00-13:00)
    - Agent 2: 1 hour/day (14:00-15:00)
    """
    mock_log = mock_agent_log_cost()
    mock_params = get_agent_params()
    log_analyzer = EventLogAnalysis(mock_log, agent_param=mock_params)
    actual_utilization = log_analyzer.resource_utilization()

    # Maximum available working hours per day for each agent
    agent_available_hours = [2, 2, 1]

    # Actual hours worked per day for each agent
    # Structure: [agent_0_days, agent_1_days, agent_2_days]
    # Each inner list contains hours worked on each day
    agent_worked_hours = [[1, 2], [1, 0], [0, 1, 0, 0]]

    # Sum of all hours worked across all agents and days
    total_worked_hours = sum(sum(daily_hours) for daily_hours in agent_worked_hours)

    # Calculate total possible working hours
    # For each agent: (available hours per day) * (number of days they worked)
    total_available_hours = sum(
        available_hours * len(worked_days)
        for available_hours, worked_days in zip(agent_available_hours, agent_worked_hours)
    )

    # Calculate utilization as percentage of worked hours vs available hours
    expected_utilization = (total_worked_hours / total_available_hours) * 100

    assert actual_utilization == pytest.approx(expected_utilization)


def test_resouce_util_simod():
    """
    Tests if resource utilization matches the expected value.
    Each resource has different working hours:
    - Resource 1: 5 hours/day (8:00-10:00, 11:00-12:00, 13:00-15:00)
    - Resource 2: 5 hours/day (8:00-10:00, 11:00-12:00, 13:00-15:00)
    - Resource 3: 5 hours/day (8:00-10:00, 11:00-12:00, 13:00-15:00)
    """
    mock_log = mock_simod_log_cost()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)
    actual_utilization = log_analyzer.resource_utilization()

    # Maximum available working hours per day for each resource
    resource_available_hours = 5  # All resources have same availability

    # Actual hours worked per day for each resource
    # Structure: [resource_1_days, resource_2_days, resource_3_days]
    # Each inner list contains hours worked on each day
    resource_worked_hours = [
        [0, 3, 4, 2, 2],  # Resource 1 worked hours
        [1, 0],  # Resource 2 worked hours
        [0.5, 1, 0],  # Resource 3 worked hours
    ]

    # Sum of all hours worked across all resources and days
    total_worked_hours = sum(sum(daily_hours) for daily_hours in resource_worked_hours)

    # Calculate total possible working hours
    # For each resource: (available hours per day) * (number of days they worked)
    total_available_hours = sum(resource_available_hours * len(worked_days) for worked_days in resource_worked_hours)

    # Calculate utilization as percentage of worked hours vs available hours
    expected_utilization = (total_worked_hours / total_available_hours) * 100

    assert actual_utilization == pytest.approx(expected_utilization)


def test_resouce_util_agent_fixed_schedule():
    """
    Tests if resource utilization matches the expected value.
    Each agent has different working hours:
    - Agent 0: 2 hours/day (8:00-10:00)
    - Agent 1: 2 hours/day (11:00-13:00)
    - Agent 2: 1 hour/day (14:00-15:00)
    """
    mock_log = mock_agent_log_cost()
    mock_params = get_agent_params()
    log_analyzer = EventLogAnalysis(mock_log, agent_param=mock_params)
    actual_utilization = log_analyzer.resource_utilization_fixed_schedule()

    # Maximum available working hours per day for each agent ( 5 days total worked)
    agent_available_hours = [2, 2, 1] * 5

    # Actual hours worked per day for each agent
    # Structure: [agent_0_days, agent_1_days, agent_2_days]
    # Each inner list contains hours worked on each day
    agent_worked_hours = [[1, 2], [1, 0], [0, 1, 0, 0]]

    # Sum of all hours worked across all agents and days
    total_worked_hours = sum(sum(daily_hours) for daily_hours in agent_worked_hours)

    # Calculate total possible working hours
    # For each agent: (available hours per day) * (number of days they worked)
    total_available_hours = sum(agent_available_hours)

    # Calculate utilization as percentage of worked hours vs available hours
    expected_utilization = (total_worked_hours / total_available_hours) * 100
    assert actual_utilization == pytest.approx(expected_utilization)


def test_resouce_util_simod_fixed_schedule():
    """
    Tests if resource utilization matches the expected value using a different calculation method.
    Each resource has different working hours:
    - Resource 1: 5 hours/day (8:00-10:00, 11:00-12:00, 13:00-15:00)
    - Resource 2: 5 hours/day (8:00-10:00, 11:00-12:00, 13:00-15:00)
    - Resource 3: 5 hours/day (8:00-10:00, 11:00-12:00, 13:00-15:00)
    """
    mock_log = mock_simod_log_cost()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)
    actual_utilization = log_analyzer.resource_utilization_fixed_schedule()

    # Maximum available working hours per day for each resource
    resource_available_hours = 5  # All resources have same availability

    # Number of days in the simulation period
    simulation_days = 5

    # Actual hours worked per day for each resource
    # Structure: [resource_1_days, resource_2_days, resource_3_days]
    # Each inner list contains hours worked on each day
    resource_worked_hours = [
        [0, 3, 4, 2, 2],  # Resource 1 worked hours
        [1, 0],  # Resource 2 worked hours
        [0.5, 1, 0],  # Resource 3 worked hours
    ]

    # Sum of all hours worked across all resources and days
    total_worked_hours = sum(sum(daily_hours) for daily_hours in resource_worked_hours)

    # Calculate total possible working hours
    # Total hours = (available hours per day) * (number of resources) * (simulation days)
    total_available_hours = resource_available_hours * len(resource_worked_hours) * simulation_days

    # Calculate utilization as percentage of worked hours vs available hours
    expected_utilization = (total_worked_hours / total_available_hours) * 100

    assert actual_utilization == pytest.approx(expected_utilization)


def test_case_cycle_time():
    """
    Tests if average and median case cycle time matches the expected value.
    """
    mock_log = mock_event_log()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)

    mean, median = log_analyzer.case_cycle_time()

    assert mean == pytest.approx(38)
    assert median == pytest.approx(40)


def test_cost_simod():
    """
    Tests if cost for simod matches the expected value.
    """
    mock_log = mock_simod_log_cost()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, simod_params=mock_params)
    tot, per_person = log_analyzer.cost(log_analyzer._salaries)

    assert tot == pytest.approx(270.0)
    assert per_person["res1"] == pytest.approx(220)
    assert per_person["res2"] == pytest.approx(20)
    assert per_person["res3"] == pytest.approx(30)


def test_cost_agent():
    """
    Tests if cost for simod matches the expected value.
    """
    mock_log = mock_agent_log_cost()
    mock_params = get_agent_params()
    log_analyzer = EventLogAnalysis(mock_log, agent_param=mock_params)
    tot, per_person = log_analyzer.cost(log_analyzer._salaries)

    assert tot == pytest.approx(100)
    assert per_person["0"] == pytest.approx(60)
    assert per_person["1"] == pytest.approx(20)
    assert per_person["2"] == pytest.approx(20)


def test_full_analysis_simod():
    """
    Tests if full analysis works for simod.
    """
    mock_log = mock_simod_log_cost()
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, simod_params=mock_params)
    res = log_analyzer.full_analysis()

    assert res


def test_full_analysis_agent():
    """
    Tests if full analysis works for agent.
    """
    mock_log = mock_agent_log_cost()
    mock_params = get_agent_params()
    log_analyzer = EventLogAnalysis(mock_log, agent_param=mock_params)
    res = log_analyzer.full_analysis()
    assert res


def test_zero_cost_simod():
    """
    Tests if events with zero lenght has zero cost with simod.
    """
    columns = ["case_id", "resource", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "res1", "Act1", "2025-01-01 11:30:00", "2025-01-01 11:30:00"],
    ]
    mock_log = pd.DataFrame(data, columns=columns)
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, simod_params=mock_params)
    tot, _ = log_analyzer.cost(log_analyzer._salaries)

    assert tot == pytest.approx(0.0)


def test_zero_cost_agent():
    """
    Tests if events with zero lenght has zero cost with agent simulator.
    """
    columns = ["case_id", "agent", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "0", "Act1", "2025-01-01 11:30:00", "2025-01-01 11:30:00"],
    ]

    mock_log = pd.DataFrame(data, columns=columns)
    mock_params = get_agent_params()
    log_analyzer = EventLogAnalysis(mock_log, agent_param=mock_params)
    tot, _ = log_analyzer.cost(log_analyzer._salaries)

    assert tot == pytest.approx(0.0)


def test_no_side_effects():
    """
    Runs analysis in different orders and checks that the result is not affected.
    """

    mock_log = mock_agent_log_cost()
    mock_params = get_agent_params()
    log_analyzer = EventLogAnalysis(mock_log, agent_param=mock_params)

    tot, per_person = log_analyzer.cost(log_analyzer._salaries)
    act_mean, act_median, act_mean_percentages, act_median_percentages = log_analyzer.activity_cycle_time()
    mean, median = log_analyzer.case_cycle_time()
    total, by_activity = log_analyzer.waiting_time()

    mock_log_ = mock_agent_log_cost()
    mock_params_ = get_agent_params()
    log_analyzer_ = EventLogAnalysis(mock_log_, agent_param=mock_params_)

    total_, by_activity_ = log_analyzer_.waiting_time()
    mean_, median_ = log_analyzer_.case_cycle_time()
    act_mean_, act_median_, act_mean_percentages_, act_median_percentages_ = log_analyzer_.activity_cycle_time()
    tot_, per_person_ = log_analyzer_.cost(log_analyzer_._salaries)

    assert per_person == per_person_
    assert tot == pytest.approx(tot_)
    assert act_mean == act_mean_
    assert act_median == act_median_
    assert act_mean_percentages == act_mean_percentages_
    assert act_median_percentages == act_median_percentages_
    assert mean == pytest.approx(mean_)
    assert median == pytest.approx(median_)
    assert total == pytest.approx(total_)
    assert by_activity == by_activity_


def test_waiting_time_average_simod_overlapping_cases():
    """
    Tests if the average waiting time matches the expected value when cases start and end times overlapp.
    """

    columns = ["case_id", "resource", "activity", "start_time", "end_time"]
    data = [
        ["Case1", "res1", "Act1", "2025-01-01 09:00:00", "2025-01-01 09:30:00"],
        ["Case1", "res2", "Act2", "2025-01-01 09:30:00", "2025-01-01 10:00:00"],
        ["Case1", "res1", "Act3", "2025-01-01 10:00:00", "2025-01-01 10:30:00"],
        ["Case2", "res3", "Act1", "2025-01-01 09:30:00", "2025-01-01 10:30:00"],
        ["Case2", "res1", "Act2", "2025-01-01 11:00:00", "2025-01-01 12:00:00"],  # waits 30 min
        ["Case1", "res4", "Act2", "2025-01-01 12:00:00", "2025-01-01 13:00:00"],  # waits 90 min
    ]

    mock_log = pd.DataFrame(data, columns=columns)
    mock_params = get_simod_params()
    log_analyzer = EventLogAnalysis(mock_log, mock_params)

    average_waiting_time, by_activity = log_analyzer.waiting_time()

    assert average_waiting_time == pytest.approx(3600)  # 120 min (7200 s) divided by 2 (nr of cases)
