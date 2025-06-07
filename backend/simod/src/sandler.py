import json
import shutil
from io import BytesIO
from pathlib import Path

import pandas as pd
from pix_framework.filesystem.file_manager import get_random_folder_id

from simod.event_log.event_log import EventLog
from simod.settings.control_flow_settings import ProcessModelDiscoveryAlgorithm
from simod.settings.simod_settings import SimodSettings
from simod.simod import Simod
from simod.simulation.prosimos import ProsimosSettings
from simod.simulation.prosimos import simulate

"""
Working example

# df = pd.read_csv('df.csv')
# sandler = Sandler("/app/simod/test/", df)
# sandler.discover()

"""


class Sandler:
    """
    Handles saving a provided DataFrame to a specified path structure
    and ensures necessary directories exist.

    Attributes:
        __output_path: class: Path: Path object pointing to the output directory.

    Methods:
        discover(csv_io: BytesIO): Starts the Simod discovery phase.
        simulate(bpmn_io: BytesIO, json_io: BytesIO, timestamp: Pandas.Timestamp): Starts the Prosimos simulation phase.
    """

    def __init__(self):
        """
        Initializes the Sandler instance by setting up paths and saving the event log.

        Args:
            df: class: Pandas.DataFrame: The event log data to be saved.
        """
        self.__output_path = Path("sandler") / get_random_folder_id()
        self.__ensure_directory_exists(self.__output_path)

    def __ensure_directory_exists(self, path: Path):
        """
        Create a path if it does not exist

        Args:
            path: class: Path, the path to be checked

        Returns:
            None
        """
        # Check if the directory exists, and create it if it doesn't
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

    def cleanup(self):
        """
        Remove the output directory and all its contents.
        """
        if self.__output_path.exists():
            shutil.rmtree(self.__output_path)

    def discover(self, csv_io: BytesIO, modifiable_settings: dict = None):
        """
        Start a Simod discovery for the Sandler instance.

        Args:
            csv_io: class: BytesIO, the event log to run the discovery phase on.

        Returns:
            Tuple of BytesIO objects, the .bpmn file and .json file
        """
        print("Starting discover\n", flush=True)

        event_log_str = "event_log.csv"
        event_log_path = self.__output_path / Path(event_log_str)

        # Save the Event_log file
        with open(event_log_path, "wb") as f_bpmn:
            f_bpmn.write(csv_io.getbuffer())

        settings = SimodSettings.default()
        settings.common.train_log_path = event_log_path
        settings.common.perform_final_evaluation = False
        settings.control_flow.mining_algorithm = ProcessModelDiscoveryAlgorithm("sm2")
        # Read and preprocess event log
        event_log = EventLog.from_path(
            log_ids=settings.common.log_ids,
            train_log_path=settings.common.train_log_path,
            test_log_path=settings.common.test_log_path,
            preprocessing_settings=settings.preprocessing,
            need_test_partition=settings.common.perform_final_evaluation,
        )

        if modifiable_settings is not None:
            # Deep copy to avoid mutating the original
            cfg = json.loads(json.dumps(modifiable_settings))
            # Alternatively, if you're okay with a shallower copy:
            # cfg = deepcopy(modifiable_settings)

            # ─── disable_extraneous_delay ─────────────────────────────────────────
            # Default: False (i.e. delays stay at whatever SimodSettings.default is)
            disable_extraneous = cfg.get("disable_extraneous_delay", False)
            if not isinstance(disable_extraneous, bool):
                disable_extraneous = False

            if disable_extraneous:
                settings.extraneous_activity_delays = None
            # else: leave settings.extraneous_activity_delays alone (default)

            # ─── set_split_miner_v1 ───────────────────────────────────────────────
            # Default: False → use "sm2"
            use_v1 = cfg.get("set_split_miner_v1", False)
            if not isinstance(use_v1, bool):
                use_v1 = False

            miner_choice = "sm1" if use_v1 else "sm2"
            settings.control_flow.mining_algorithm = ProcessModelDiscoveryAlgorithm(miner_choice)

        # Instantiate and run SIMOD
        simod = Simod(settings=settings, event_log=event_log, output_dir=self.__output_path)
        simod.run()

        # Paths to output files
        output_json_path = self.__output_path / "best_result/event_log.json"
        output_bpmn_path = self.__output_path / "best_result/event_log.bpmn"

        # Read both files into memory
        with open(output_json_path, "r", encoding="utf-8") as json_file:
            json_bytes = BytesIO(json_file.read().encode("utf-8"))

        with open(output_bpmn_path, "r", encoding="utf-8") as bpmn_file:
            bpmn_bytes = BytesIO(bpmn_file.read().encode("utf-8"))

        print("Discover complete\n", flush=True)

        # Clean up the output directory
        self.cleanup()

        # Return both files
        return bpmn_bytes, json_bytes

    def simulate(
        self,
        bpmn_io: BytesIO,
        json_io: BytesIO,
        timestamp: pd.Timestamp = pd.Timestamp("2025-01-01 12:00:00").tz_localize("UTC"),
    ):
        """
        Start a Prosimos simulation for the Sandler instance.

        Args:
            bpmn_io:   class: BytesIO, a bytesio object containing the bpmn to simulate
            json_io:   class: BytesIO, a bytesio object containing the json parameters to simulate
            timestamp: class: pd.Timestamp default: pd.Timestamp('2025-01-01 12:00:00').tz_localize('UTC')
                the time in the simulation.

        Returns:
            A BytesIO object containing the .csv file
        """
        print("Starting simulation\n", flush=True)

        _bpmn_path = Path(self.__output_path / "output.bpmn")
        _json_path = Path(self.__output_path / "output.json")

        with open(_bpmn_path, "wb") as f:
            f.write(bpmn_io.getbuffer())
        with open(_json_path, "wb") as f:
            f.write(json_io.getbuffer())

        settings = ProsimosSettings(
            bpmn_path=_bpmn_path,
            parameters_path=_json_path,
            output_log_path=Path(self.__output_path / "event_log.csv"),
            num_simulation_cases=1000,
            simulation_start=timestamp,
        )

        simulate(settings)

        output_log_path = settings.output_log_path
        with open(output_log_path, "r") as file:
            file_contents = file.read()
        print("Simulation complete\n", flush=True)

        # Clean up the output directory
        self.cleanup()

        return BytesIO(file_contents.encode("utf-8"))


def main():
    """
    This is a working example of the Sandler class.
    It is used to discover a process model from an event log and simulate it.
    The event log is saved in the dev_resource folder.
    The modifiable_settings.json file is used to configure the discovery.
    The bpmn file is saved in the dev_resource folder.
    The json file is saved in the dev_resource folder.
    The simulated event log is saved in the dev_resource folder.
    """
    # Discovery
    path_to_res = "/simod/dev_resource/"
    df = pd.read_csv(path_to_res + "df.csv")

    # Load settings from modifiable_settings.json
    # You do not need to pass a json, if no json is passed, the default settings will be used.
    # If you wish to try the different modified setting locally, change the values in the modifiable_settings.json file from false to true.
    with open(path_to_res + "modifiable_settings.json", "r", encoding="utf-8") as f:
        modifiable_settings = json.load(f)

    # Convert to BytesIO
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # SandlerClass instance to handle the discovery
    sandler = Sandler()
    bpmn_file, json_file = sandler.discover(csv_buffer, modifiable_settings)

    # Save the JSON file
    with open(path_to_res + "event_log.json", "wb") as f_json:
        f_json.write(json_file.getbuffer())

    # Save the BPMN file
    with open(path_to_res + "event_log.bpmn", "wb") as f_bpmn:
        f_bpmn.write(bpmn_file.getbuffer())

    # Simulation
    # SandlerClass instance to handle the simulation
    sandler2 = Sandler()

    csv_file = sandler2.simulate(bpmn_io=bpmn_file, json_io=json_file)

    # Save the simulated event log
    with open(path_to_res + "simulated_event_log.csv", "wb") as f_bpmn:
        f_bpmn.write(csv_file.getbuffer())


if __name__ == "__main__":
    main()
