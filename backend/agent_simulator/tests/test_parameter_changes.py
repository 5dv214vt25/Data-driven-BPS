"""
Unit tests for parameter changes.
"""

import io
import json
import pickle
import zipfile
from datetime import datetime

import pandas as pd
import pytest
from agent_simulator_manager import _apply_changes
from agent_simulator_manager import apply_agent_activity_overrides
from agent_simulator_manager import apply_global_activity_overrides
from agent_simulator_manager import start_simulation_from_api
from param_changes import _add_new_agents
from param_changes import change_num_cases
from param_changes import change_start_time
from param_changes import deactivate_agents
from simulation_config import SimulationConfig
from simulation_config import load_simulation_config
from werkzeug.datastructures import FileStorage

# This file tests parameter changes and that they have an actual impact on the output data, some
# tests in this folder are more of a system-test and should be conisdered to be moved to another file.


@pytest.fixture(scope="module")
def run_discovery():
    """
    Fixture that runs discovery and returns the simulation config
    """
    # Setup test parameters
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

    # Create and configure simulation config
    sim_config = SimulationConfig()
    sim_config.process_discovery_args(args)
    sim_config.run_discovery()

    # Return the simulation config
    return sim_config


@pytest.fixture(scope="module")
def setup_discovery_object_from_file(filename="test_resources/sim_dump_3"):
    sim = load_simulation_config(filename)
    return sim


# =============== Unit Tests ===============
def test_deactivate_agents(setup_discovery_object_from_file):
    # Get the simulation config
    sim_config = setup_discovery_object_from_file

    # Deactivate agent 0
    deactivate_agents(sim_config, [0, 4, 9])

    # Check that agent 0 is in the deactivated_resources list
    assert 0 in sim_config.sim_instance.simulation_parameters["deactivated_resources"]
    assert 4 in sim_config.sim_instance.simulation_parameters["deactivated_resources"]
    assert 9 in sim_config.sim_instance.simulation_parameters["deactivated_resources"]


def test_change_num_cases(setup_discovery_object_from_file):
    """
    Test that the number of cases is reduced by 1
    """
    # Get the simulation config
    sim_config = setup_discovery_object_from_file

    # Get the number of cases before change
    num_cases_before = sim_config.sim_instance.num_cases_to_simulate

    # Change the number of cases
    change_num_cases(sim_config, 400)

    # Get the number of cases after change
    num_cases_after = sim_config.sim_instance.num_cases_to_simulate

    assert num_cases_before != num_cases_after
    assert num_cases_after == 400


# Checks that you can change starttime of first case to arrive
def test_change_start_time(setup_discovery_object_from_file):
    sim_config = setup_discovery_object_from_file

    start_time_before = sim_config.sim_instance.simulation_parameters["start_timestamp"]
    dt = datetime.fromisoformat("2026-01-01 08:00:00+00:00")
    change_start_time(sim_config, dt)

    start_time_after = sim_config.sim_instance.simulation_parameters["start_timestamp"]

    assert start_time_after == dt
    assert start_time_before != start_time_after


def test_add_agents(setup_discovery_object_from_file):
    """
    Test that the number of agents are increased
    """
    # Get the simulation config
    sim_config = setup_discovery_object_from_file

    # Get the agents before changing, (list copy)
    keys = list(sim_config.sim_instance.simulation_parameters["agent_to_resource"].keys())
    key_max = max(keys)

    # Add two additional agents
    agents_to_duplicate = [(0, 2), (1, 4), (2, 2)]  # adds 1 + 3 + 1 = 5 agents

    _add_new_agents(sim_config, agents_to_duplicate)

    # Get the agents after
    keys_after = sim_config.sim_instance.simulation_parameters["agent_to_resource"].keys()
    key_max_after = max(keys_after)

    assert keys != keys_after
    assert key_max != key_max_after
    assert key_max + 5 == key_max_after


def test_activity_durations_for_all_agents():
    config_1 = load_simulation_config("test_resources/sim_dump_activity_duration")

    apply_global_activity_overrides(config_1, activity_durations={"AML check": 90.0, "Assess loan risk": 120.0})

    expected = {"AML check": 90.0, "Assess loan risk": 120.0}
    assert config_1.params["activity_duration_map"] == expected
    assert config_1.sim_instance.activity_duration_overrides == expected


def test_activity_durations_for_specific_agents():
    config_1 = load_simulation_config("test_resources/sim_dump_activity_duration_agent")

    agent_map = {
        0: {"AML check": 90.0, "Assess loan risk": 120.0},
        1: {"AML check": 60.0},
    }

    apply_agent_activity_overrides(
        config_1,
        agent_activity_durations=agent_map,
    )

    # ensuring no global overrides are set
    assert config_1.params.get("activity_duration_map", {}) == {}

    # the params dict must carry the agent overrides (keys as strings)
    expected_params = {
        "0": {"AML check": 90.0, "Assess loan risk": 120.0},
        "1": {"AML check": 60.0},
    }
    assert config_1.params["agent_activity_duration_map"] == expected_params

    assert config_1.sim_instance.agent_activity_duration_overrides == agent_map


# =============== Larger (System)? Tests ===============


def test_case_count_output_file():
    """
    Test that the simulation output files are created and contain the expected data
    """

    # Load pickle file as FileStorage
    with open("test_resources/parameter_changes_resources/model.pkl", "rb") as f:
        pkl_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="model.pkl", content_type="application/octet-stream"
        )
        buffer = io.BytesIO(pkl_file.read())
        sim_config = pickle.load(buffer)

    # Load JSON file as FileStorage and parse the JSON
    with open("test_resources/parameter_changes_resources/change_case_count_params.json", "rb") as f:
        json_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="update_params.json", content_type="application/json"
        )
        json_data = json.load(json_file)

    # Apply parameter changes
    updated_sim_config = _apply_changes(sim_config, json_data)

    # Serialize the updated simulation config to bytes
    buffer = io.BytesIO()
    pickle.dump(updated_sim_config, buffer)
    buffer.seek(0)

    # Wrap the bytes in a FileStorage object
    updated_pkl_file = FileStorage(stream=buffer, filename="model.pkl", content_type="application/octet-stream")

    # Run the simulation
    return_file = start_simulation_from_api(updated_pkl_file)

    # Assert the result is not None
    assert return_file is not None

    with zipfile.ZipFile(return_file, "r") as zf:
        assert "simulated_log_0.csv" in zf.namelist()

        with zf.open("simulated_log_0.csv") as csv_file:
            df = pd.read_csv(csv_file)
            max_case_id = df["case_id"].max()
            assert (
                max_case_id == 250 - 1
            ), f"{max_case_id} cases in output, 250 (249) excpected"  # Specified in the update params file


def test_agent_deactivation_output_file():
    """
    Test that the simulation output files are created and contain the expected data
    """

    # Load pickle file as FileStorage
    with open("test_resources/parameter_changes_resources/model.pkl", "rb") as f:
        pkl_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="model.pkl", content_type="application/octet-stream"
        )
        buffer = io.BytesIO(pkl_file.read())
        sim_config = pickle.load(buffer)

    # Load JSON file as FileStorage and parse the JSON
    with open("test_resources/parameter_changes_resources/deactivate_agent_params.json", "rb") as f:
        json_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="update_params.json", content_type="application/json"
        )
        json_data = json.load(json_file)

    # Apply parameter changes
    updated_sim_config = _apply_changes(sim_config, json_data)

    # Serialize the updated simulation config to bytes
    buffer = io.BytesIO()
    pickle.dump(updated_sim_config, buffer)
    buffer.seek(0)

    # Wrap the bytes in a FileStorage object
    updated_pkl_file = FileStorage(stream=buffer, filename="model.pkl", content_type="application/octet-stream")

    # Run the simulation
    return_file = start_simulation_from_api(updated_pkl_file)

    # Assert the result is not None
    assert return_file is not None

    with zipfile.ZipFile(return_file, "r") as zf:
        assert "simulated_log_0.csv" in zf.namelist()

        with zf.open("simulated_log_0.csv") as csv_file:
            df = pd.read_csv(csv_file)
            removed_agents = {0, 4, 12}

            # Assert that none of the removed agents are present in the 'agent' column
            assert df["agent"].isin(removed_agents).sum() == 0, (
                f"Found forbidden agents in 'agent' column: "
                f"{df[df['agent'].isin(removed_agents)]['agent'].unique()}"
            )


def test_add_agents_file():
    """
    Test that the simulation output files are created and contain the expected data.
    Adds 10 new agents and makes sure they are in the output file. This test has a
    suuuuuper small possibility of being failed. When the file is parsed, there might
    have been a possible case where one agent is suuuuper unlucky and no cases were provided to him.
    Re-run the test if so :)
    """

    # Load pickle file as FileStorage
    with open("test_resources/parameter_changes_resources/model.pkl", "rb") as f:
        pkl_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="model.pkl", content_type="application/octet-stream"
        )
        buffer = io.BytesIO(pkl_file.read())
        sim_config = pickle.load(buffer)

    # Load JSON file as FileStorage and parse the JSON
    with open("test_resources/parameter_changes_resources/add_agents_params.json", "rb") as f:
        json_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="update_params.json", content_type="application/json"
        )
        json_data = json.load(json_file)

    # Apply parameter changes
    updated_sim_config = _apply_changes(sim_config, json_data)

    # Serialize the updated simulation config to bytes
    buffer = io.BytesIO()
    pickle.dump(updated_sim_config, buffer)
    buffer.seek(0)

    # Wrap the bytes in a FileStorage object
    updated_pkl_file = FileStorage(stream=buffer, filename="model.pkl", content_type="application/octet-stream")

    # Run the simulation
    return_file = start_simulation_from_api(updated_pkl_file)

    # Assert the result is not None
    assert return_file is not None

    with zipfile.ZipFile(return_file, "r") as zf:
        assert "simulated_log_0.csv" in zf.namelist()

        with zf.open("simulated_log_0.csv") as csv_file:
            df = pd.read_csv(csv_file)
            added_agents = {19, 20, 21, 22, 23, 24, 25, 26, 27, 28}

            agents_in_log = set(df["agent"].unique())
            missing_agents = added_agents - agents_in_log

            assert not missing_agents, f"The following added agents are missing from the log: {missing_agents}"


def test_change_start_time_file():
    # Load pickle file as FileStorage
    with open("test_resources/parameter_changes_resources/model.pkl", "rb") as f:
        pkl_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="model.pkl", content_type="application/octet-stream"
        )
        buffer = io.BytesIO(pkl_file.read())
        sim_config = pickle.load(buffer)

    # Load JSON file as FileStorage and parse the JSON
    with open("test_resources/parameter_changes_resources/change_start_time.json", "rb") as f:
        json_file = FileStorage(
            stream=io.BytesIO(f.read()), filename="update_params.json", content_type="application/json"
        )
        json_data = json.load(json_file)

    # Apply parameter changes
    updated_sim_config = _apply_changes(sim_config, json_data)

    # Serialize the updated simulation config to bytes
    buffer = io.BytesIO()
    pickle.dump(updated_sim_config, buffer)
    buffer.seek(0)

    # Wrap the bytes in a FileStorage object
    updated_pkl_file = FileStorage(stream=buffer, filename="model.pkl", content_type="application/octet-stream")

    # Run the simulation
    return_file = start_simulation_from_api(updated_pkl_file)

    # Assert the result is not None
    assert return_file is not None

    with zipfile.ZipFile(return_file, "r") as zf:
        assert "simulated_log_0.csv" in zf.namelist()

        with zf.open("simulated_log_0.csv") as csv_file:
            df = pd.read_csv(csv_file)

            # expected_start_time = "2026-01-01 08:00:00+00:00" # In the change_start_time.json
            expected_start_time = json_data["params"]["start_timestamp"]  # Gets the startime from file

            # Gets the starttime of the first row
            actual_start_time = df.loc[0, "start_timestamp"]

            # Asser that they are equal
            assert (
                actual_start_time == expected_start_time
            ), f"actual_start_time: {actual_start_time}, excpected: {expected_start_time}"


# ============= Old & Depricated test =============


# Old test for activity_dutration, the functionality was changed and test became outdated
# def test_update_and_reload():
#     config_1 = load_simulation_config("test_resources/sim_dump_activity_duration")

#     modified_config = update_config(config_1, activity_durations={"AML check": 90.0, "Assess loan risk": 120.0}, num_simulations=2)
#     base = "test_resources/tmp/cfg_mod"
#     os.makedirs(os.path.dirname(base + ".pkl"), exist_ok=True)
#     save_simulation_config(modified_config, base)

#     assert os.path.exists(str(base) + ".pkl")

#     reloaded = load_simulation_config(str(base))
#     assert reloaded.params["num_simulations"] == 2

#     expected = {"AML check": 90.0, "Assess loan risk": 120.0}
#     assert reloaded.params["activity_duration_map"] == expected
#     assert reloaded.sim_instance.activity_duration_overrides == expected
