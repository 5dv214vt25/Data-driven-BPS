import os

import debug_config

# import numpy as np
from deepdiff import DeepDiff
from source.discovery import discover_simulation_parameters
from source.generate_discovery_data import create_interactive_network
from source.simulation import BusinessProcessModel
from source.simulation import simulate_process
from source.train_test_split import load_data


class AgentSimulator:
    def __init__(self, params):
        self.params = params
        self.activity_duration_overrides = {}
        self.agent_activity_duration_overrides: dict[int, dict[str, float]] = {}  # for overriding specific agents

    def generate_html(self):

        starting_activity = BusinessProcessModel(
            self.df_train,
            self.simulation_parameters,
        ).contractor_agent.sample_starting_activity()

        return create_interactive_network(self.simulation_parameters, starting_activity)

    def generate_log(self):

        return_code = simulate_process(
            self.df_train,
            self.simulation_parameters,
            self.data_dir,
            self.params["num_simulations"],
            self.num_cases_to_simulate,
        )

        return return_code  # for success code only, does not return anything usually, consider other possibilites of doing this

    def _split_log_from_path(self, path_log):
        """
        Split the log into training, testing and validation data.
        """

        def get_validation_data(df):
            df_sorted = df.sort_values(by=["case_id", "start_timestamp"])
            total_cases = df_sorted["case_id"].nunique()
            twenty_percent = int(total_cases * 0.2)
            last_20_percent_case_ids = df_sorted["case_id"].unique()[-twenty_percent:]
            df_val = df_sorted[df_sorted["case_id"].isin(last_20_percent_case_ids)]

            return df_val

        if path_log is None:
            raise ValueError("No PATH_LOG provided. Please check your command-line arguments.")

        if not os.path.exists(path_log):
            raise FileNotFoundError(f"The file {path_log} does not exist.")

        file_extension = path_log.lower().split(".")[-1]
        df_train, num_cases_to_simulate = load_data(path_log, file_extension, self.params["column_names"])
        directory_path = os.path.dirname(path_log)
        self.data_dir = os.path.join(os.getcwd(), "simulated_data", directory_path)
        df_val = get_validation_data(df_train)
        num_cases_to_simulate_val = len(set(df_val["case_id"]))
        return (
            df_train,
            df_val,
            num_cases_to_simulate,
            num_cases_to_simulate_val,
        )

    def _split_log_from_buffer(self, buffer_log):
        """
        Split the log into training, testing and validation data.
        """

        def get_validation_data(df):
            df_sorted = df.sort_values(by=["case_id", "start_timestamp"])
            total_cases = df_sorted["case_id"].nunique()
            twenty_percent = int(total_cases * 0.2)
            last_20_percent_case_ids = df_sorted["case_id"].unique()[-twenty_percent:]
            df_val = df_sorted[df_sorted["case_id"].isin(last_20_percent_case_ids)]

            return df_val

        if self.params["determine_automatically"]:
            print("Choice for architecture and extraneous delays will be determined automatically")
            file_name_extension = "main_results"
        else:
            if self.params["central_orchestration"]:
                file_name_extension = "orchestrated"
            else:
                file_name_extension = "autonomous"

        file_extension = "csv"
        df_train, num_cases_to_simulate = load_data(buffer_log, file_extension, self.params["column_names"])
        file_name = os.path.splitext(os.path.basename(self.params["PATH_LOG"]))[0]

        self.data_dir = os.path.join(os.getcwd(), "simulated_data", file_name, file_name_extension)
        df_val = get_validation_data(df_train)
        num_cases_to_simulate_val = len(set(df_val["case_id"]))
        return (
            df_train,
            df_val,
            num_cases_to_simulate,
            num_cases_to_simulate_val,
        )

    def execute_discover(self):
        (
            self.df_train,
            self.df_val,
            self.num_cases_to_simulate,
            self.num_cases_to_simulate_val,
        ) = self._split_log_from_path(self.params["path_log"])

        # discover basic simulation parameters
        # not sure if need to add my two new added params here
        self.df_train, self.simulation_parameters = discover_simulation_parameters(
            self.df_train,
            None,
            self.df_val,
            self.data_dir,
            self.num_cases_to_simulate,
            self.num_cases_to_simulate_val,
            self.params["determine_automatically"],
            self.params["central_orchestration"],
            self.params["discover_extr_delays"],
            None,  # start time
            self.params["activity_filter"],
            self.params["new_activity_duration"],
        )

        if debug_config.debug:
            # print(self.simulation_parameters["activity_durations_dict"])
            pass

    # For comparisions to make sure a save then load of a sim is the same as base obj.
    def __eq__(self, other):
        """
        Equals method that comepares two AgentSimulators if they are equal or not
        See simulation_configs __eq__ mehthod for more details on why this is done
        """
        if not isinstance(other, AgentSimulator):
            return False

        # 1) compare params dict
        if self.params != other.params:
            return False

        # 2) compare DataFrames if they exist
        for df_attr in ("df_train", "df_val"):
            a = getattr(self, df_attr, None)
            b = getattr(other, df_attr, None)
            if a is None or b is None:
                # if one has it and the other doesn’t, not equal
                if a is not b:
                    return False
            else:
                # both are DataFrames: use .equals()
                if not a.equals(b):
                    return False

        # 3) compare simple scalar attributes
        for attr in ("num_cases_to_simulate", "num_cases_to_simulate_val", "data_dir"):
            if getattr(self, attr, None) != getattr(other, attr, None):
                return False

        # 4) compare simulation_parameters dict (or replace with deeper logic if needed)
        diff = DeepDiff(self.simulation_parameters, other.simulation_parameters, ignore_order=True)

        if diff:
            # print("Deep diff")
            return False

        return True

    def __ne__(self, other):
        return not (self == other)

    def create_agent_simulator_from_args(self, args):
        # Process arguments Set paths
        column_names = {
            args.case_id: "case_id",
            args.activity_name: "activity_name",
            args.resource_name: "resource",
            args.end_timestamp: "end_timestamp",
            args.start_timestamp: "start_timestamp",
        }

        # Feature flags
        discover_extr_delays = args.extr_delays
        central_orchestration = args.central_orchestration
        determine_automatically = args.determine_automatically

        params = {
            "discover_extr_delays": discover_extr_delays,
            "discover_parallel_work": False,
            "central_orchestration": central_orchestration,
            "determine_automatically": determine_automatically,
            "column_names": column_names,
            "num_simulations": args.num_simulations,
            "activity_filter": args.activity_filter,  # remove
            "new_activity_duration": args.new_activity_duration,  # remove
        }

        simulator = AgentSimulator(params)
        return simulator

    # ======== DEPRICATED FUNCTIONS ========

    # TODO: Ask Konstantin if theses are needed, it seems like it is not needed nor used

    def override_activity_duration(self, activity_name: str, duration: float):
        self.activity_duration_overrides[activity_name] = duration

        if isinstance(self.simulation_parameters, dict):
            self.simulation_parameters.setdefault("activity_duration_map", {})[activity_name] = duration

        if isinstance(self.simulation_parameters, dict):
            if debug_config.debug:
                print(f"Overriding discovery parameter for '{activity_name}':" f" new_activity_duration → {duration}")
            self.simulation_parameters["new_activity_duration"] = duration
        elif hasattr(self.simulation_parameters, "new_activity_duration"):
            setattr(self.simulation_parameters, "new_activity_duration", duration)
        else:
            print("Couldn't find a place to write new_activity_duration!")

    # overriding for specific agents
    def override_agent_activity_duration(self, agent_id: int, activity_name: str, duration: float):
        # store the override
        self.agent_activity_duration_overrides.setdefault(agent_id, {})[activity_name] = duration

        # persist it so pickle/json carries it through
        self.simulation_parameters.setdefault("agent_activity_duration_map", {}).setdefault(str(agent_id), {})[
            activity_name
        ] = duration

        # print(f"[Agent {agent_id}] override “{activity_name}” → {duration}")
