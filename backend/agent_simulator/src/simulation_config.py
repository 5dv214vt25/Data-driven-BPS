import os
import pickle

import debug_config
import pandas as pd
from source.agent_simulator import AgentSimulator

BASE_PICKLE_PATH = os.path.join(os.path.dirname(__file__), "../pickle_resources")


"""
File is used for breaking up AgentSimulator in two different phases.
File should be used by agent_simulation_manager.py with an open interface with the funcitons:
run_discovery, process_discovery_args, run_simulation

Responsible group - Oregano, Group 3
"""


class SimulationConfig:

    # ========= Public class functions =========
    __all__ = [
        "run_discovery",
        "process_discovery_args",
        "run_simulation",
        "load_simulation_config",
        "save_simulation_config",
    ]

    def __init__(self):
        """
        Shows what is used in class, for simpler understanding.
        """
        self.discover_extr_delays = False
        self.discover_parallel_work = False
        self.central_orchestration = False
        self.determine_automatically = False
        self.path_log = None
        self.path_log_test = None
        self.train_and_test = False
        self.column_names = None
        self.params = None
        self.num_simulations = None
        self.activity_filter = None
        self.new_activity_duration = None

        self.activity_duration_map: dict[str, float] = {}

        # This is an agent_simulator ("object")
        self.sim_instance = None

    def run_discovery(self):
        """
        The function to start a discovery with all set params.
        Note:
            Function process_discovery_args() needs to have been called correctly to initialize the
            discovery object, so all parametres for the discovery are set.

        Args:
            None

        Prerequisites:
            process_discovery_args() is correctly called on instance.

        Returns:
            AgentSimulator, instance with all training done, later to be ran a simulation on.

        """
        self.sim_instance = AgentSimulator(self.params)
        self.sim_instance.execute_discover()
        return self

    def process_discovery_args(self, args):
        """
        Function is the main function to procces all arguments and sets all needed fields
        for the discovery phase to run and complete.

        Args:
            dict: a dict for all arguments that are used by the discovery phase

        Example Dictionary tamplate:
            Note: Create this "params" dict somewhere and call this function for a
            complete discovery object that can run a discovery phase.

            params = {
                'log_path': 'src/raw_data/LoanApp.csv',
                'train_path': None,
                'test_path': None,
                'case_id': 'case_id',
                'activity_name': 'activity',
                'resource_name': 'resource',
                'end_timestamp': 'end_time',
                'start_timestamp': 'start_time',
                'extr_delays': False,
                'central_orchestration': False,
                'determine_automatically': False,
                'num_simulations': 1
            }
        """
        # Sets log path
        self._set_path_log(args["log_path"])
        self._set_path_log_test(args["test_path"])

        # Sets col names from .csv file
        column_names = {
            args["case_id"]: "case_id",
            args["activity_name"]: "activity_name",
            args["resource_name"]: "resource",
            args["end_timestamp"]: "end_timestamp",
            args["start_timestamp"]: "start_timestamp",
        }
        self._set_column_names(column_names)

        # Sets complicated discovery parameters on what "types" of discovery that should be used
        self._set_extr_delays(args["extr_delays"])
        self._set_central_orchestration(args["central_orchestration"])
        self._set_determine_automatically(args["determine_automatically"])

        self._set_num_simulations(args["num_simulations"])

        self._set_params(self._generate_params())

    def run_simulation(self):
        """
        Runs the simulation, needs to be done with a complete discovery phase. Either loaded from a file
        or directyl from the object itself.

        Args:
            None / all args stored in instance itself

        Prerequisites:
            A instance of a ran discovery phase

        Returns:
            None, #TODO: Should this return something down the line?
        """
        if not isinstance(self.sim_instance.df_train, pd.DataFrame):
            raise TypeError(
                f"Expected df_train to be a pandas DataFrame, got {type(self.sim_instance.df_train).__name__}"
            )

        if not isinstance(self.sim_instance.simulation_parameters, dict):
            raise TypeError(
                f"Expected simulation_parameters to be a dict, got {type(self.sim_instance.simulation_parameters).__name__}"
            )

        if not isinstance(self.sim_instance.data_dir, str):
            raise TypeError(f"Expected data_dir to be a str, got {type(self.sim_instance.data_dir).__name__}")

        if not isinstance(self.num_simulations, int) or self.num_simulations <= 0:
            raise ValueError(f"num_simulations must be a positive integer, got {self.num_simulations}")

        if not isinstance(self.sim_instance.num_cases_to_simulate, int) or self.sim_instance.num_cases_to_simulate <= 0:
            raise ValueError(f"num_cases must be a positive integer, got {self.sim_instance.num_cases_to_simulate}")

        return_code = self.sim_instance.generate_log()

        return return_code  # TODO: What to return here?, now this is done for some specifisity to do tests

    def __eq__(self, other):
        """
        This function is vibe-coded, the code is however tested in test_simulation_config, in the test_load_saved_config test
        where two instances should / should not be equal in different situations.

        Args:
            other, Other object to compare self to

        Returns:
            Bool, if the two are eqaul
        """

        if not isinstance(other, SimulationConfig):
            return False

        # compare all simple fields
        attrs = [
            "discover_extr_delays",
            "discover_parallel_work",
            "central_orchestration",
            "determine_automatically",
            "path_log",
            "path_log_test",
            "train_and_test",
            "column_names",
            "params",
            "num_simulations",
        ]
        for a in attrs:
            if getattr(self, a) != getattr(other, a):
                return False

        # Uses AgentSims own EQ method that is implemented
        if self.sim_instance != other.sim_instance:
            return False

        return True

    def __ne__(self, other):
        """
        Not equal function, opposite of __eq__, uses __eq__ in its comparison,
        See: __eq__ for more detailed explanation
        """
        return not (self == other)

    # ========================== Internal Helper Functions ==========================

    def _set_extr_delays(self, extr_delays):
        """
        Setter for delay for discovery phase.

        Args:
            Bool
        """
        self.extr_delays = extr_delays

    def _set_discover_parallel_work(self, discover_parallel_work):
        """
        Setter for paralell work for discovery phase.

        Args:
            Bool
        """
        self.discover_parallel_work = discover_parallel_work

    def _set_central_orchestration(self, central_orchestration):
        """
        Setter for central orchestration for discovery phase.

        Args:
            Bool
        """
        self.central_orchestration = central_orchestration

    def _set_determine_automatically(self, determine_automatically):
        """
        Setter for determine automatically for discovery phase.

        Args:
            Bool
        """
        self.determine_automatically = determine_automatically

    def _set_path_log(self, path_log):
        """
        Setter for the log path to use for discovery phase, the path to .csv file to train on.

        Args:
            Sring, path
        """
        self.path_log = path_log

    def _set_path_log_test(self, path_log_test):
        """
        Setter for the test log path to use for discovery phase, the path to .csv file to train on.

        Args:
            Sring, path
        """
        self.path_log_test = path_log_test

    def _set_train_and_test(self, train_and_test):
        """
        Setter for train and test.

        Args:
            Bool
        """
        self.train_and_test = train_and_test

    def _set_column_names(self, column_names):
        """
        Setter for column names to be used in discovery phase.

        Args:
            dict: a dict containing collumn names
        """
        self.column_names = column_names

    def _set_num_simulations(self, num_simulations):
        """
        Setter for number of simulations that are used
        """
        self.num_simulations = num_simulations

    def _set_params(self, params):
        """
        Setter for params dict in the discovery_obj class

        Args:
            dict, containing params used by discovery phase
        """
        self.params = params

    def _generate_params(self):
        """
        Creates a dictoinary that is used by discovery phase.
        Is made to more simply create the dictionary that should be set by _set_params()

        Returns:
            dict, used for setting the self.params field
        """
        return {
            "discover_extr_delays": self.discover_extr_delays,
            "discover_parallel_work": self.discover_parallel_work,
            "central_orchestration": self.central_orchestration,
            "determine_automatically": self.determine_automatically,
            "path_log": self.path_log,
            "path_log_test": self.path_log_test,
            "train_and_test": self.train_and_test,
            "column_names": self.column_names,
            "num_simulations": self.num_simulations,
            "activity_filter": self.activity_filter,
            "new_activity_duration": self.new_activity_duration,
            "activity_duration_map": self.activity_duration_map,
        }

    # ======================== Depricated functions (to be removed) ========================

    # TODO: Dont know if these are even used, I think that Konstantin uses other funcs, however these
    # should not be where they were (function on the class SimulationConfig)
    # Ask kon when he is back

    # not sure about this
    def _set_activity_filter(self, activity_filter):
        self.activity_filter = activity_filter
        # if we've already created the simulator, re-apply any duration override
        if self.sim_instance is not None and self.new_activity_duration is not None:
            self.sim_instance.override_activity_duration(self.activity_filter, self.new_activity_duration)

    # not sure about this
    def _set_new_activity_duration(self, new_activity_duration):
        """Setter for the new‐activity duration (and record in map)."""
        self.new_activity_duration = new_activity_duration

        # keep our batch map in sync
        if self.activity_filter is not None:
            self.activity_duration_map[self.activity_filter] = new_activity_duration

        # mirror into params so pickle/unpickle carries it
        if self.params is not None:
            self.params["new_activity_duration"] = new_activity_duration
            # also include the full map in params
            self.params["activity_duration_map"] = self.activity_duration_map

        # if we've already created the simulator, push the override now
        if self.sim_instance is not None and self.activity_filter is not None:
            self.sim_instance.override_activity_duration(self.activity_filter, new_activity_duration)


# NOTE: TODO: These funcitons are used in some of our old and first unittests,
#             we should probibaly consider removing these functions and updating
#             the way that we are doing some of our unittests. Howevert we do not
#             have the time for this currently.


def save_simulation_config(sim_config, filename):
    """
    Save the simulation_config to a Python pickle file.
    Pickle files are stpred in the directory: agent_simulator/pickle_resources

    Args:
        simulation_config

    Keyword Args:
        filename (str): Path and filename where the pickle file should be saved.

    Returns:
        filename (str): The path and filename where the picke file was saved
        or raises error if saving failed due to an error.

    """
    print("\n\n=========\n Using depricated func (save_sim_config)\n\n=========\n")

    try:
        if not filename.endswith(".pkl"):
            filename += ".pkl"
            if debug_config.debug:
                print("Added .pkl to filename")

        full_path = os.path.join(BASE_PICKLE_PATH, filename)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as f:
            pickle.dump(sim_config, f)

        if debug_config.debug:
            print(f"Simulator saved to {full_path}")
        return full_path

    except (OSError, pickle.PicklingError) as e:
        print(f"Failed to save simulator: {e}")
        raise


def load_simulation_config(filename):
    """
    Loads a previus simulation_config that had been stored as a pickle file.
    Pickle files are stpred in the directory: agent_simulator/pickle_resources
    Args:
        filename (str): The path and filename where the picke file is stored.
    Returns:
        simulation_config, the "object / instance" that was dumped to the pickle file
    """
    print("\n\n=========\n Using depricated func (load_sim_config)\n\n=========\n")

    try:
        if not filename.endswith(".pkl"):
            filename += ".pkl"
            if debug_config.debug:
                print("Added .pkl to filename")

        full_path = os.path.join(BASE_PICKLE_PATH, filename)

        with open(full_path, "rb") as f:
            sim_config = pickle.load(f)

        if debug_config.debug:
            print(f"Simulator loaded from {full_path}")
        return sim_config

    except (OSError, pickle.UnpicklingError) as e:
        print(f"Failed to load simulator: {e}")
        raise e
