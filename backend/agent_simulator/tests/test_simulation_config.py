import pytest
from simulation_config import SimulationConfig
from simulation_config import load_simulation_config
from simulation_config import save_simulation_config
from source.agent_simulator import AgentSimulator

# This file should test the following functions:
# "run_discovery"
# "process_discovery_args"
#  "run_simulation"
#  "load_simulation_config"
#  "save_simulation_config"
#
# And any other functions that are added to the file that should be "open" for use and public
# Any functions that are private _ prefixed, are not tested by themselves.


@pytest.fixture(scope="module")
def setup_similation_config():
    params = {
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

    config = SimulationConfig()
    config.process_discovery_args(params)

    return config


def test_run_discovery(setup_similation_config):

    sim_config = setup_similation_config

    sim_config.run_discovery()

    assert isinstance(sim_config.sim_instance, AgentSimulator)


def test_process_discovery_args():
    params = {
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
        "determine_automatically": True,
        "num_simulations": 4,
    }

    config = SimulationConfig()
    config.process_discovery_args(params)

    assert config.num_simulations == 4
    assert isinstance(config.params, dict)
    assert isinstance(config.column_names, dict)
    assert config.sim_instance is None  # Is yet not set, gets set in discovery
    assert config.determine_automatically is True
    assert config.extr_delays is False
    assert config.central_orchestration is False
    assert config.path_log == "test_resources/LoanAppSmall.csv"


def test_run_simulation(setup_similation_config):
    sim_config = setup_similation_config

    # Prereq for a simulation to run
    sim_config.run_discovery()

    # TODO: This should be updated when run_simulation is updated to return something
    # Currently only a successcode is returned if simulation is sucessful on a "good" input
    assert sim_config.run_simulation() == 0


# ===================== Depricated =====================
# These fnctions are no longer used in the actual program if ran through the API,
# however they do work and are used for testing and running stuff localy when developing.
# These funcitons are also used in a lot of tests for simplicity sake because we did not
# have the time or the will to update them :)


def test_save_simulation_config(setup_similation_config):
    config = setup_similation_config

    filename = save_simulation_config(config, "test_save_sim")

    assert filename.endswith("test_save_sim.pkl")

    config_2 = load_simulation_config(filename)

    assert config == config_2


def test_load_simulation_config(setup_similation_config):

    sim_config = setup_similation_config
    sim_config.run_discovery()
    filename = save_simulation_config(sim_config, "test")

    sim_1 = load_simulation_config(filename)
    sim_2 = load_simulation_config(filename)

    assert isinstance(sim_1, SimulationConfig)

    assert sim_1 == sim_2

    assert sim_config == sim_1
    assert sim_config == sim_2

    params = {
        "log_path": "test_resources/LoanAppSmall.csv",
        "train_path": None,
        "test_path": None,
        "case_id": "case_id",
        "activity_name": "activity",
        "resource_name": "resource",
        "end_timestamp": "end_time",
        "start_timestamp": "start_time",
        "extr_delays": False,
        "central_orchestration": True,
        "determine_automatically": False,
        "num_simulations": 2,
    }

    config = SimulationConfig()
    config.process_discovery_args(params)
    config.run_discovery()

    assert config != sim_config
    assert config != sim_1
    assert config != sim_2
