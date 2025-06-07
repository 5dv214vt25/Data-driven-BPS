import json
from datetime import timedelta

import agent_simulator_manager
import deepdiff
import pandas as pd
import pytest
from param_changes import change_agent_schedule
from param_changes import change_inter_arrival_distribution
from param_changes import rename_agent
from simulation_config import SimulationConfig
from simulation_config import load_simulation_config

# TODO: NOTE: If big changes are made to simulation_config / agent_simulation_manager
# then the test resource .pkl file needs to be updated
# This way of loading configs are also old, a new way is done in the API and test should probibaly
# change and migrate so that tests are more similar to actual API & flow of the program


@pytest.fixture(scope="module")
def setup_discovery():

    args = {
        "log_path": "../src/raw_data/LoanApp.csv",
        "train_path": None,
        "test_path": None,
        "case_id": "case_id",
        "activity_name": "activity",
        "resource_name": "resource",
        "end_timestamp": "end_time",
        "start_timestamp": "start_time",
        "extr_delays": False,
        "central_orchestration": False,
        "determine_automatically": False,
        "num_simulations": 1,
    }

    filename = agent_simulator_manager.start_discovery_with_args(args)

    simulator = load_simulation_config(filename)

    return simulator


@pytest.fixture(scope="module")
def setup_discovery_object_from_file(filename="test_resources/sim_dump_3"):
    sim = load_simulation_config(filename)
    return sim


@pytest.fixture(scope="module")
def setup_sim_config():

    # Arrange: mock discovery args
    args = {
        "log_path": "test_resources/LoanAppSmall.csv",
        "train_path": None,
        "test_path": None,
        "case_id": "case_id",
        "activity_name": "activity",
        "resource_name": "resource",
        "end_timestamp": "end_time",
        "start_timestamp": "start_time",
        "extr_delays": False,
        "central_orchestration": False,
        "determine_automatically": False,
        "num_simulations": 1,
    }

    sim_config = SimulationConfig()
    return sim_config, args


# Tests if the returns are correct data type
def test_start_discovery(setup_discovery_object_from_file):
    simulator = setup_discovery_object_from_file

    assert isinstance(simulator.sim_instance.df_train, pd.DataFrame)
    assert isinstance(simulator.sim_instance.params, dict)
    assert isinstance(simulator.sim_instance.data_dir, str)


# Test that errors are raised.
def test_start_simulation(setup_discovery_object_from_file):
    simulator = setup_discovery_object_from_file
    with pytest.raises(TypeError):
        agent_simulator_manager._start_simulation(
            simulator.sim_instance.df_train, simulator.sim_instance.params, 1, "str", 200
        )


def test_start_discovery_from_api(setup_sim_config):
    sim_config, args = setup_sim_config

    # Act
    json_data, json_params_data, pkl_path = agent_simulator_manager.start_discovery_from_api(sim_config, args)

    with open("test_resources/Expected_json_output_after_discovery.json") as f:
        expected_json_data = json.load(f)
    _assert_json_equal_ignoring_keys(expected_json_data, json_data, keys_to_ignore=["color"])


def test_rename_agents(setup_discovery_object_from_file):
    simulator = setup_discovery_object_from_file
    agent_to_resource = simulator.sim_instance.simulation_parameters["agent_to_resource"]
    updated_agent_to_resource = rename_agent(agent_to_resource, 0, "David")
    assert updated_agent_to_resource[0] == "David"
    assert len(updated_agent_to_resource) == len(agent_to_resource)


def test_change_arrival_distribution(setup_discovery_object_from_file):
    simulator = setup_discovery_object_from_file
    change_inter_arrival_distribution(simulator, "test")
    arrival_times = simulator.sim_instance.simulation_parameters["case_arrival_times"]
    expected_diff = timedelta(minutes=45)
    actual_diff = arrival_times[1] - arrival_times[0]
    assert actual_diff == expected_diff, f"Expected 45 minutes difference, got {actual_diff}"


# ================== Helper functions to use in tests ==================


def _remove_keys(obj, keys_to_ignore):
    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            cleaned = _remove_keys(parsed, keys_to_ignore)
            return json.dumps(cleaned)  # Re-stringify it if it was originally a string
        except json.JSONDecodeError:
            return obj  # It's a normal string, not JSON
    elif isinstance(obj, dict):
        return {k: _remove_keys(v, keys_to_ignore) for k, v in obj.items() if k not in keys_to_ignore}
    elif isinstance(obj, list):
        return [_remove_keys(item, keys_to_ignore) for item in obj]
    else:
        return obj


def _assert_json_equal_ignoring_keys(json1, json2, keys_to_ignore):
    cleaned1 = _remove_keys(json1, keys_to_ignore)
    cleaned2 = _remove_keys(json2, keys_to_ignore)

    # Use deepdiff to compare the cleaned JSONs
    diff = deepdiff.DeepDiff(cleaned1, cleaned2, ignore_order=True)

    if diff:
        raise AssertionError(f"Differences found:\n{json.dumps(diff, indent=2)}")


def test_change_schedules_for_agents(setup_discovery_object_from_file):
    simulator = setup_discovery_object_from_file
    agent = 7

    schedules = simulator.sim_instance.simulation_parameters["res_calendars"]

    value = schedules[agent].total_weekly_work / 3600
    assert value == 40

    work_intervals = schedules[7].work_intervals

    for i in range(0, 7):
        for interval in work_intervals[i]:
            assert interval.start.hour == 7
            assert interval.start.minute == 0
            assert interval.end.hour == 15
            assert interval.end.minute == 0

    change_agent_schedule(
        schedules, agent, ["MONDAY", "TUESDAY"], [[("09:00:00", "15:00:00")], [("09:00:00", "15:00:00")]]
    )

    value = schedules[agent].total_weekly_work / 3600
    assert value == 36

    for i in range(0, 7):
        for interval in work_intervals[i]:
            if i < 2:
                assert interval.start.hour == 9
                assert interval.start.minute == 0
                assert interval.end.hour == 15
                assert interval.end.minute == 0
            else:
                assert interval.start.hour == 7
                assert interval.start.minute == 0
                assert interval.end.hour == 15
                assert interval.end.minute == 0


# ================== Test functions whos functionality is no longer supported ==================


# Test is the old test for changing agents, this function has been out-commented in param-changes.py
# Consider using this again later when changing agents works and are supported

# def test_change_roles_for_agents(setup_discovery_object_from_file):
#     simulator = setup_discovery_object_from_file
#     agent = 1

#     roles = simulator.sim_instance.simulation_parameters["roles"]

#     assert agent in roles["Role 1"]["agents"]

#     change_agent_role(roles, agent, "Role 2")

#     assert agent not in roles["Role 1"]["agents"]
#     assert agent in roles["Role 2"]["agents"]


# Not yet implemented ? or changed, consider removing or refining this
# def test_change_distribution_activity_duration(setup_discovery_object_from_file):
#     simulator = setup_discovery_object_from_file
#     change_distribution_activity_durations(simulator, "test")
#     activity_durations = simulator.sim_instance.simulation_parameters["activity_durations_dict"]
#     expected_diff = timedelta(minutes=45)
#     actual_diff = activity_durations[1] - activity_durations[0]
#     assert actual_diff == expected_diff, f"Expected 45 minutes difference, got {actual_diff}"
