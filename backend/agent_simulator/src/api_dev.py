import json
import os
import tempfile
import warnings
import zipfile
from io import BytesIO

import agent_simulator_manager
from simulation_config import SimulationConfig

warnings.filterwarnings("ignore")


# NOTE: THIS FILE IS NOT SUPPOSED TO BE USED FROM ANYTHING OR ANYWHERE, ALL FUNCTIONALITY IS A MOCK OF THE REGULAR api.py FILE
# 		THIS IS ONLY FOR RUNNING THE APPLICATION LOCALLY WITHOUT RUNINNG A FLASK SERVER, THIS TO SIMPLIFY IMPLEMENTING FUNCTIONS
# 		THAT ARE LATER USED BY THE REGULAR API
#       ASK KEV - agentsim IF ANY QUESTIONS


def start_agent_discovery(event_log_path: str, parameters_path: str = None) -> BytesIO:
    """
    Starts the agent discovery process.

    Args:
        event_log_path (str): Path to CSV file containing the event log.
        parameters_path (str, optional): Path to JSON file with discovery input parameters.

    Returns:
        BytesIO: In-memory zip file containing model.pkl, params.json, and visualization.json.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, "uploaded_file.csv")
        with open(event_log_path, "rb") as src, open(temp_file_path, "wb") as dst:
            dst.write(src.read())

        if parameters_path and os.path.exists(parameters_path):
            with open(parameters_path, "r") as f:
                args = json.load(f)
                args["log_path"] = temp_file_path

                # TODO: This needs to be done another way than this below.
                # None of central_orc or determine_auto is supported with
                # the current vizualisation and therefore the program crahshes
                # if the simulation is ran without vizualisation the program works as intended.
                # This is because elizabeth's code does not support the differnet settings
                # Change this in the future, (re-do the vizu code) or implement new way of
                # imputing neccesary values when these settings are used

                args["central_orchestration"] = False
                args["determine_automatically"] = False

        else:
            args = {
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

        sim_config = SimulationConfig()

        visualization_data, params_data, pkl_data = agent_simulator_manager.start_discovery_from_api(sim_config, args)

        visualization_json = json.dumps(visualization_data, indent=2)
        params_json = json.dumps(params_data, indent=2)

        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, "w") as zf:
            zf.writestr("visualization.json", visualization_json)
            zf.writestr("params.json", params_json)
            zf.writestr("model.pkl", pkl_data)

        memory_file.seek(0)
        return memory_file


def update_parameters(pkl_path: str, changed_params_path: str) -> BytesIO:
    """
    Updates simulation parameters and returns a zip file.

    Args:
        pkl_path (str): Path to .pkl file.
        changed_params_path (str): Path to .json file containing parameter changes.

    Returns:
        BytesIO: In-memory zip file with updated data.
    """
    with open(pkl_path, "rb") as pkl_file, open(changed_params_path, "rb") as json_file:
        return agent_simulator_manager.update_parameters(pkl_file, json_file)


def start_agent_simulation(pkl_path: str) -> BytesIO:
    """
    Starts the agent simulation based on the provided model.

    Args:
        pkl_path (str): Path to .pkl file.

    Returns:
        BytesIO: In-memory zip file containing simulation output.
    """
    with open(pkl_path, "rb") as pkl_file:
        return agent_simulator_manager.start_simulation_from_api(pkl_file)


def _extract_all_zips_in_dir(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            zip_path = os.path.join(directory, filename)
            extract_path = os.path.join(directory, os.path.splitext(filename)[0])  # Subfolder per zip
            os.makedirs(extract_path, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
            # print(f"Extracted {filename} to {extract_path}")


if __name__ == "__main__":

    # This small script should not be noted or anythinfg. It is only here for us devs
    # Change the dirs to fit your own, and run the file instead of spinning up the API

    # Define your output directory
    output_dir = "kev_dev/tmp_files"
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
    # print("1")
    # Run discovery
    # zip_data = start_agent_discovery("kev_dev/raw_data/LoanAppSmall.csv")
    zip_data = start_agent_discovery("kev_dev/raw_data/LoanAppSmall.csv")

    discovery_zip_path = os.path.join(output_dir, "discovery_output.zip")
    with open(discovery_zip_path, "wb") as f:
        f.write(zip_data.read())
    # print("2")

    # Extract model.pkl from the discovery output
    with zipfile.ZipFile(discovery_zip_path, "r") as zip_ref:
        zip_ref.extract("model.pkl", path=output_dir)  # Extract into output_dir

    model_path = os.path.join(output_dir, "model.pkl")
    # print("3")

    # Update parameters
    zip_data_2 = update_parameters(model_path, "kev_dev/params/params.json")
    updated_zip_path = os.path.join(output_dir, "updated_output.zip")
    with open(updated_zip_path, "wb") as f:
        f.write(zip_data_2.read())

    # print("4")

    # Extract model.pkl from the discovery output
    with zipfile.ZipFile(updated_zip_path, "r") as zip_ref:
        zip_ref.extract("model.pkl", path=output_dir)  # Extract into output_dir

    model_path_2 = os.path.join(output_dir, "model.pkl")
    # print(f"model_path_2: {model_path_2}")
    # print("5")

    # Run simulation
    zip_data_2 = start_agent_simulation(model_path_2)
    simulation_zip_path = os.path.join(output_dir, "simulation_output.zip")
    with open(simulation_zip_path, "wb") as f:
        f.write(zip_data_2.read())

    # print("6")

    # Extract all .zip to look at output without manually extracting
    _extract_all_zips_in_dir(output_dir)
