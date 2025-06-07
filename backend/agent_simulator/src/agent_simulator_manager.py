import io
import json
import os
import pickle
import tempfile
import warnings
import zipfile
from datetime import datetime
from io import BytesIO
from pprint import pprint
from typing import Optional
from typing import Tuple

import debug_config
from param_changes import apply_agent_activity_overrides
from param_changes import apply_global_activity_overrides
from param_changes import apply_simple_overrides
from param_changes import change_agent_schedule
from param_changes import change_distribution_activity_durations
from param_changes import change_inter_arrival_distribution
from param_changes import change_num_cases
from param_changes import change_start_time
from param_changes import change_transition_probabilities
from param_changes import update_agent_count
from simulation_config import SimulationConfig
from simulation_config import load_simulation_config
from simulation_config import save_simulation_config
from source.discovery_to_json import agent_to_json
from source.json_data_class import JsonVisualization
from werkzeug.datastructures import FileStorage

"""
This module is responsible for managing Agent Simulator.
It contains the functions that can be used by the controller
to access the agent simulator.
"""

# Module-level constants
MODEL_NAME = "agent_simulator_manager"
MODEL_VERSION = "1.0.0"
MODEL_DESCRIPTION = "Module for managing Agent Simulator."


# ============= Public module functions =============
__all__ = ["start_simulation_from_api", "update_parameters", "start_discovery_from_api"]


def start_discovery_from_api(sim_config: SimulationConfig, args) -> Tuple[JsonVisualization, Optional[str]]:
    """
    Runs the discovery phase, generates Json data for visualization and dumps a pkl file for simulation phase
    """

    # Process all arguments
    sim_config.process_discovery_args(args)

    # Run discovery
    sim_config.run_discovery()

    # Save to pkl
    # Create a bytes buffer for the pkl object
    buffer = io.BytesIO()

    # Dump the object into the buffer
    pickle.dump(sim_config, buffer)

    # Get the binary content
    binary_data = buffer.getvalue()

    # Generate JSON Visualization data
    json_visualization_data = sim_config.sim_instance.generate_html()

    # Generate Json params
    json_params_data = agent_to_json(sim_config.sim_instance)

    # Return all json visualization data along with the parameter data and pkl file to api
    return json_visualization_data, json_params_data["data"], binary_data


def start_simulation_from_api(pkl_file: FileStorage):
    # Load the pickle data
    buffer = io.BytesIO(pkl_file.read())
    sim_config = pickle.load(buffer)

    with tempfile.TemporaryDirectory() as simulation_dir:
        # Set the correct path
        sim_config.sim_instance.data_dir = simulation_dir

        _start_simulation(sim_config)

        # Get number of simulations for knowing the amount of eventlogs in the output
        num_simulations = sim_config.sim_instance.params["num_simulations"]

        # Create in-memory ZIP
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, "w") as zf:
            for i in range(num_simulations):
                filename = f"simulated_log_{i}.csv"
                file_path = os.path.join(simulation_dir, filename)

                # Check if the file exists before reading
                if os.path.exists(file_path):
                    with open(file_path, "r") as file:
                        content = file.read()
                    zf.writestr(filename, content)
                else:
                    print("File: ", file_path, " not found")

        memory_file.seek(0)

        return memory_file


def update_parameters(pkl_file: FileStorage, json_file: FileStorage):
    """
    Takes a pickle binary file and a json with parameter changes and updates
        the pickle file with those changes.

        Returns: A zip file
    """
    # Load pickle file
    buffer = io.BytesIO(pkl_file.read())

    sim_config = pickle.load(buffer)

    json_data = json.load(json_file)

    # Apply all the changes, ALL CHANGES ARE APPLIED HERE
    updated_sim_config = _apply_changes(sim_config, json_data)

    # Create a bytes buffer
    buffer = io.BytesIO()

    # Dump the object into the buffer
    pickle.dump(updated_sim_config, buffer)

    # Get the binary content
    pkl_data = buffer.getvalue()

    # Compute the new visualization data
    json_visualization_data = updated_sim_config.sim_instance.generate_html()

    # Generate Json params
    json_params_data = agent_to_json(updated_sim_config.sim_instance)
    visualization_json = json.dumps(json_visualization_data, indent=2)
    params_json = json.dumps(json_params_data["data"], indent=2)

    # Create in-memory ZIP
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        zf.writestr("visualization.json", visualization_json)
        zf.writestr("params.json", params_json)
        zf.writestr("model.pkl", pkl_data)

    memory_file.seek(0)

    return memory_file


def parse_discovery_parameters(request, temp_file_path):
    """
    Parse the discovery parameters

    Args:
        request (Flask request): The incoming HTTP request containing optional parameters.
        temp_file_path (str): Path to the temporary file storing the uploaded event log.

    Returns:
        dict: Dictionary containing the discovery parameters with enforced defaults.
    """

    # Default parameters
    default_args = {
        "log_path": temp_file_path,
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

    # Update parameters
    if "parameters" in request.files:
        user_args = json.load(request.files["parameters"])
        user_args.pop("log_path", None)  # Remove if user attempts to set it
        user_args.pop("train_path", None)  # Remove if user attempts to set it
        user_args.pop("test_path", None)  # Remove if user attempts to set it
        default_args.update(user_args)  # Update only existing keys

    return default_args


# ============== Helper Functions ==============


def _start_simulation(sim_config: SimulationConfig):
    """
    Start simulation phase and returns _(a path to where the simulations are stored or the simulator object)_

    Args:
        df_train (dict): A 'trained' dataframe generated from a discovery phase
        simulation_parameters (?): Simulation parameters generated from a discovery phase
        data_dir (path_str): A path to where the simulated data should be saved
        num_simulations (int): The number of simulations that should be ran
        num_cases (int): The number of cases

    Returns:
        The simulation is ran and the simulations are stored in some files that are outputed to the terminal.
        Will return either a path to where the simulations are stored or the simulator object.

    """

    try:
        return sim_config.run_simulation()
    except Exception as e:
        print(f"Simulation phase failed: {e}")
        raise e


def _apply_changes(sim_config: SimulationConfig, json_data) -> SimulationConfig:
    """
    Goes through the json and applies only the changes specified in the json
    This could easily be used to update, add and remove different parameters in the future.
    To see how the parameters should look, see /agent_simulator/parameters/params.json on gitlab

    """

    # ==================== GENERAL PARAMETERS ====================

    # 0) Start time
    if _find_key(json_data, "start_timestamp") is not None:
        time_str = json_data["params"]["start_timestamp"]
        dt = datetime.fromisoformat(time_str)
        change_start_time(sim_config, dt)
    else:
        default_start_time = sim_config.sim_instance.df_train.groupby("case_id")["start_timestamp"].min().min()
        change_start_time(sim_config, default_start_time)

    # 1) num_simulations
    if _find_key(json_data, "num_simulations") is not None:
        n = json_data["params"]["num_simulations"]
        apply_simple_overrides(sim_config, {"num_simulations": n})

    # 2) new_num_cases_to_simulate
    if _find_key(json_data, "new_num_cases_to_simulate") is not None:
        v = _find_key(json_data, "new_num_cases_to_simulate")
        change_num_cases(sim_config, v)
        if debug_config.debug:
            print(f"Changed number of cases to simulate to: {v}")

    # 3) inter_arrival_distribution
    if _find_key(json_data, "inter_arrival_distribution") is not None:
        iad = json_data["params"]["inter_arrival_distribution"]
        change_inter_arrival_distribution(sim_config, iad["distribution"])

    # ===================================================================
    # ==================== AGENT SPECIFIC PARAMETERS ====================

    # 4) Change amount of each agent (add / remove)
    result = _find_key(json_data, "agent_count_changes")
    if result is not None:
        update_agent_count(sim_config, result)

    # 5) per-agent activity durations
    if _find_key(json_data, "agent_activity_durations") is not None:
        aad = json_data["params"]["agent_activity_durations"]

        # making it a list
        if isinstance(aad, dict):
            items = [aad]
        elif isinstance(aad, list):
            items = aad
        else:
            raise ValueError("agent_activity_durations must be object or list")

        overrides_map = {}
        for entry in items:
            agent_id = entry["agent_id"]
            ov_map = entry["overrides"]
            overrides_map[agent_id] = ov_map

        apply_agent_activity_overrides(sim_config, overrides_map)

    # 6) resource calendars
    if _find_key(json_data, "res_calendars") is not None:
        res_cal = sim_config.sim_instance.simulation_parameters["res_calendars"]
        # change each agent (from params.json) calendar
        for agent_cal in json_data["params"]["res_calendars"]:
            aid = agent_cal["agent_id"]
            days = agent_cal["days"]
            sched = agent_cal["schedule"]
            change_agent_schedule(res_cal, aid, days, sched)

    # 7) Agent activity mapping
    # TODO: This is a feature that is implemnted on the frontend, but not here on the backend
    #       This should be looked into

    # 8) change transition probabilities
    if _find_key(json_data, "transition_probabilities") is not None:
        js = json_data["params"]["transition_probabilities"]
        transition_probabilies = sim_config.sim_instance.simulation_parameters["transition_probabilities"]
        transition_probabilies = change_transition_probabilities(transition_probabilies, js)

    if _find_key(json_data, "transition_probabilities_autonomous") is not None:
        js = json_data["params"]["transition_probabilities_autonomous"]
        transition_probabilities_autonomous = sim_config.sim_instance.simulation_parameters[
            "transition_probabilities_autonomous"
        ]
        transition_probabilities_autonomous = change_transition_probabilities(transition_probabilities_autonomous, js)

    # ===================================================================
    # ==================== GLOBAL PARAMETERS ====================

    # 9) Global activity durations
    if _find_key(json_data, "global_activity_durations") is not None:
        durations = json_data["params"]["global_activity_durations"]
        apply_global_activity_overrides(sim_config, durations)

    # 10) activity_durations distribution
    if _find_key(json_data, "new_distribution_activity_duration") is not None:
        dist_activity_duration = json_data["params"]["new_distribution_activity_duration"]["distribution"]
        change_distribution_activity_durations(sim_config, dist_activity_duration)

    # ==================== NON WORKING PARAMETERS (remove?) ====================
    # TODO: Look over these, and re-implement. These are rither somewhat working or
    #       not working. They might also only support one change (can only change name
    #       of one agent, not all agents that you want.) This is waht is sought after.

    # # ?) roles
    # if _find_key(json_data, "roles") is not None:
    #     js = json_data["params"]["roles"]
    #     sim_config.sim_instance.simulation_parameters["roles"] = change_agent_role(
    #         sim_config.sim_instance.simulation_parameters["roles"], js["agent_id"], js["new_role"]
    #     )

    # # ?) rename_agent
    # if _find_key(json_data, "rename_agent") is not None:
    #     js = json_data["params"]["rename_agent"]
    #     sim_config.sim_instance.simulation_parameters["agent_to_resource"] = rename_agent(
    #         sim_config.sim_instance.simulation_parameters["agent_to_resource"], js["agent_id"], js["new_name"]
    #     )

    return sim_config


def _find_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            found = _find_key(value, target_key)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_key(item, target_key)
            if found is not None:
                return found
    return None


def _print_config(cfg):
    """Nicely show contents of a dict or an object with public attrs."""
    if isinstance(cfg, dict):
        pprint(cfg)
        print("keys:", list(cfg.keys()))
    else:
        attrs = [a for a in dir(cfg) if not a.startswith("_")]
        print("Attributes:", attrs)
        for a in attrs:
            print(f"  {a} = {getattr(cfg, a)}")


# ============== Depricated =============
# To be removed when we see that the new functions are 100% woring


def start_discovery_with_args(sim_config: SimulationConfig, args):
    """
    Start the discovery phase with custom arguments and save the output to a pickle file.

    Args:
        args (dict): A dictionary containing the arguments neccecary to start the discovery phase.
            Expected arguments are:
                "log_path"
                "train_path"
                "test_path"
                "case_id"
                "activity_name"
                "resource_name"
                "end_timestamp"
                "start_timestamp"
                "extr_delays"
                "central_orchestration"
                "determine_automatically"
                "num_simulations"
    Returns:
        dump_filename (str): A path and filename to where the pickle file was saved
        or None if an error occured

    """

    print("\n\n===================\nUsing a Depricated Function (start_discovery_with_args)\n===================\n\n")

    # Processes all args in dictionary
    sim_config.process_discovery_args(args)

    # Runs a discovery
    sim_config.run_discovery()

    filename_pkl = save_simulation_config(sim_config, "sim_dump.pkl")

    return filename_pkl


if __name__ == "__main__":
    """
    A script that can be run to see that the manager behaves correctly
    """
    warnings.filterwarnings("ignore")

    print("\n\n=#=#=#=#=#=#=#=#=\n\nRunning agent_simulator-manager as main file\n\n=#=#=#=#=#=#=#=#=\n\n")

    debug_input = input("Do you wish to use DEBUG mode? (Y/n)")
    if debug_input != "n":
        debug_config.debug = True

    # This dict is what is used to start a sim, could be edited to use different parameters
    # Should get this from API when discovery should start
    args = {
        "log_path": "raw_data/output.csv",
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

    if debug_config.debug:
        print("Starting discovery with args!\n")

    filename = start_discovery_with_args(sim_config, args)

    if debug_config.debug:
        print("Discovery finished")
        print("\n\n=#=#=#=#=#=#=#=#=#=\n\n")

    if debug_config.debug:
        print("\n-------------------\n Generating HTML on discovery (before file dump)\n-------------------\n")

    # Generating HTML on discovery (before save to pkl)
    # html_content_1 = sim_config.sim_instance.generate_html("html_base")
    json_data = sim_config.sim_instance.generate_html()

    with open("output.json", "w") as f:
        json.dump(json_data, f, indent=2)

    # print(json_data["agent_nodes"])

    if debug_config.debug:
        print(f"Loading a discovery from file. Filename: {filename}")

    sim_config_pkl = load_simulation_config(filename)

    json_data = {
        "params": {
            "activity_durations": {"AML check": 60.0, "Assess loan risk": 10.0},
            "res_calendars": {
                "Agent_id": 7.0,
                "Days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
                "Schedule": [["09:00:00", "17:00:00"]],
            },
            "num_simulations": 3,
            "new_num_cases_to_simulate": 750,
        }
    }

    # sim_config_pkl = update_parameters(json_data)

    # res_calendars = sim_config_pkl.sim_instance.simulation_parameters["res_calendars"]

    # change_agent_schedule(res_calendars, 7, ["MONDAY", "TUESDAY"], [("09:00:00", "15:00:00")])

    # sim_config_pkl.sim_instance.simulation_parameters["res_calendars"][7].print_calendar_info()

    save_simulation_config(sim_config_pkl, "config_modified.pkl")
    updated_sim_config_pkl = load_simulation_config("config_modified")

    if debug_config.debug:
        _print_config(updated_sim_config_pkl)

    if debug_config.debug:
        print("\n-------------------\n Generating HTML (2) in PICKLE \n-------------------\n")

    json_data2 = sim_config.sim_instance.generate_html()

    run_sim_input = input("Would you like to run simulations? (Y/n)")
    if run_sim_input != "n":

        change_num_cases(updated_sim_config_pkl, 750)

        _start_simulation(updated_sim_config_pkl)

    if debug_config.debug:
        print("Program finished. No errors occured")
