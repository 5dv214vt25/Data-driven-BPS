import json
import shutil
from pathlib import Path
from typing import List
from typing import Optional
from typing import Tuple

import hyperopt
import numpy as np
import pandas as pd
from hyperopt import STATUS_FAIL
from hyperopt import STATUS_OK
from hyperopt import Trials
from hyperopt import fmin
from hyperopt import hp
from hyperopt import tpe
from pix_framework.discovery.gateway_probabilities import GatewayProbabilities
from pix_framework.discovery.gateway_probabilities import GatewayProbabilitiesDiscoveryMethod
from pix_framework.discovery.gateway_probabilities import compute_gateway_probabilities
from pix_framework.filesystem.file_manager import create_folder
from pix_framework.filesystem.file_manager import get_random_folder_id
from pix_framework.filesystem.file_manager import remove_asset
from pix_framework.io.bpm_graph import BPMNGraph

from simod.branch_rules.discovery import discover_branch_rules
from simod.branch_rules.discovery import map_branch_rules_to_flows
from simod.branch_rules.types import BranchRules

from ..cli_formatter import print_message
from ..cli_formatter import print_step
from ..cli_formatter import print_subsection
from ..event_log.event_log import EventLog
from ..settings.control_flow_settings import ControlFlowSettings
from ..settings.control_flow_settings import ProcessModelDiscoveryAlgorithm
from ..simulation.parameters.BPS_model import BPSModel
from ..simulation.prosimos import simulate_and_evaluate
from ..utilities import get_process_model_path
from ..utilities import get_simulation_parameters_path
from ..utilities import hyperopt_step
from .discovery import discover_process_model
from .settings import HyperoptIterationParams


class ControlFlowOptimizer:
    """
    Optimizes the control-flow of a business process model using hyperparameter optimization.

    This class performs iterative optimization to refine the structure of a process model
    and discover optimal gateway probabilities. It evaluates different configurations to
    improve the process model based on a given metric.

    The search space is built based on the parameters ranges in [settings].

    Attributes
    ----------
    event_log : :class:`EventLog`
        Event log containing train and validation partitions.
    initial_bps_model : :class:`BPSModel`
        Business process simulation (BPS) model to use as a base, by replacing its control-flow model
        with the discovered one in each iteration.
    settings : :class:`ControlFlowSettings`
        Configuration settings to build the search space for the optimization process.
    base_directory : :class:`pathlib.Path`
        Root directory where output files will be stored.
    best_bps_model : :class:`BPSModel`, optional
        Best discovered BPS model after the optimization process.
    evaluation_measurements : :class:`pandas.DataFrame`
        Quality measures recorded for each hyperopt iteration.

    Notes
    -----
    - If no process model is provided, a discovery method will be used.
    - Optimization is performed using TPE-hyperparameter optimization.
    """

    # Event log with train/validation partitions
    event_log: EventLog
    # BPS model taken as starting point
    initial_bps_model: BPSModel
    # Configuration settings
    settings: ControlFlowSettings
    # Root directory for the output files
    base_directory: Path
    # Path to the best process model
    best_bps_model: Optional[BPSModel]
    # Quality measure of each hyperopt iteration
    evaluation_measurements: pd.DataFrame

    # Flag indicating if the model is provided of it needs to be discovered
    _need_to_discover_model: bool
    # Path to the training log in XES format, needed for Split Miner
    _xes_train_log_path: Optional[Path] = None
    # Set of trials for the hyperparameter optimization process
    _bayes_trials = Trials

    def __init__(self, event_log: EventLog, bps_model: BPSModel, settings: ControlFlowSettings, base_directory: Path):
        # Save event log, optimization settings, and output directory
        self.event_log = event_log
        self.initial_bps_model = bps_model.deep_copy()
        self.settings = settings
        self.base_directory = base_directory
        # Check if it is needed to discover the process model
        self.best_bps_model = None
        if self.initial_bps_model.process_model is None:
            # Not provided, create path to best discovered model
            self._need_to_discover_model = True
            # Export training log (XES format) for SplitMiner
            self._xes_train_both_timestamps_log_path = self.base_directory / (self.event_log.process_name + ".xes")
            self.event_log.train_to_xes(self._xes_train_both_timestamps_log_path)
            self._xes_train_only_end_log_path = self.base_directory / (self.event_log.process_name + "_only_end.xes")
            self.event_log.train_to_xes(self._xes_train_only_end_log_path, only_complete_events=True)
        else:
            # Process model provided
            self._need_to_discover_model = False
        # Initialize table to store quality measures of each iteration
        self.evaluation_measurements = pd.DataFrame(
            columns=[
                "distance",
                "metric",
                "status",
                "gateway_probabilities",
                "epsilon",
                "eta",
                "prioritize_parallelism",
                "replace_or_joins",
                "output_dir",
                "f_score",
            ]
        )
        # Instantiate trials for hyper-optimization process
        self._bayes_trials = Trials()
        self.iteration_index = 0

    def _hyperopt_iteration(self, hyperopt_iteration_dict: dict):
        # Report new iteration
        print_subsection(f"Control-flow optimization iteration {self.iteration_index}")
        # Initialize status
        status = STATUS_OK
        # Create folder for this iteration
        output_dir = self.base_directory / get_random_folder_id(prefix="iteration_")
        create_folder(output_dir)
        # Initialize BPS model for this iteration
        current_bps_model = self.initial_bps_model.deep_copy()
        # Parameters of this iteration
        hyperopt_iteration_params = HyperoptIterationParams.from_hyperopt_dict(
            hyperopt_dict=hyperopt_iteration_dict,
            optimization_metric=self.settings.optimization_metric,
            mining_algorithm=self.settings.mining_algorithm,
            provided_model_path=None if self._need_to_discover_model else self.initial_bps_model.process_model,
            output_dir=output_dir,
            project_name=self.event_log.process_name,
        )
        print_message(f"Parameters: {hyperopt_iteration_params}")

        # Discover process model (if needed)
        if self._need_to_discover_model:
            try:
                status, current_bps_model.process_model = hyperopt_step(
                    status, self._discover_process_model, hyperopt_iteration_params
                )
            except Exception as e:
                print_message(f"Process Discovery failed: {e}")
                status = STATUS_FAIL
        else:
            current_bps_model.process_model = hyperopt_iteration_params.provided_model_path

        # Discover gateway probabilities
        status, current_bps_model.gateway_probabilities = hyperopt_step(
            status,
            self._discover_gateway_probabilities,
            current_bps_model.process_model,
            hyperopt_iteration_params.gateway_probabilities_method,
        )

        #  Discover branch rules
        if self.settings.discover_branch_rules:
            status, current_bps_model.branch_rules = hyperopt_step(
                status, self._discover_branch_rules, current_bps_model.process_model, hyperopt_iteration_params
            )

            current_bps_model.gateway_probabilities = map_branch_rules_to_flows(
                current_bps_model.gateway_probabilities, current_bps_model.branch_rules
            )

        # Simulate candidate and evaluate its quality
        status, evaluation_measurements = hyperopt_step(
            status, self._simulate_bps_model, current_bps_model, hyperopt_iteration_params.output_dir
        )

        # Define the response of this iteration
        status, response = self._define_response(
            status, evaluation_measurements, hyperopt_iteration_params.output_dir, current_bps_model.process_model
        )
        print(f"Control-flow optimization iteration response: {response}")

        # Save the quality of this evaluation and increase iteration index
        self._process_measurements(hyperopt_iteration_params, status, evaluation_measurements)
        self.iteration_index += 1

        return response

    def run(self) -> HyperoptIterationParams:
        """
        Runs the control-flow optimization process.

        This method defines the hyperparameter search space and executes a
        TPE-hyperparameter optimization process to discover the best control-flow model.
        It evaluates multiple iterations and selects the best-performing set of parameters
        for its discovery.

        Returns
        -------
        :class:`~simod.control_flow.settings.HyperoptIterationParams`
            The parameters of the best iteration of the optimization process.

        Raises
        ------
        AssertionError
            If the best discovered process model path does not exist after optimization.
        """
        # Define search space
        self.iteration_index = 0
        search_space = self._define_search_space(settings=self.settings)

        # Launch optimization process
        best_hyperopt_params = fmin(
            fn=self._hyperopt_iteration,
            space=search_space,
            algo=tpe.suggest,
            max_evals=self.settings.num_iterations,
            trials=self._bayes_trials,
            show_progressbar=False,
        )
        best_hyperopt_params = hyperopt.space_eval(search_space, best_hyperopt_params)

        # Process best results
        results = pd.DataFrame(self._bayes_trials.results).sort_values("loss")
        best_result = results[results.status == STATUS_OK].iloc[0]
        assert best_result[
            "process_model_path"
        ].exists(), f"Best model path {best_result['process_model_path']} does not exist"

        # Re-build parameters of the best hyperopt iteration
        best_hyperopt_parameters = HyperoptIterationParams.from_hyperopt_dict(
            hyperopt_dict=best_hyperopt_params,
            optimization_metric=self.settings.optimization_metric,
            mining_algorithm=self.settings.mining_algorithm,
            provided_model_path=None if self._need_to_discover_model else self.initial_bps_model.process_model,
            output_dir=best_result["output_dir"],
            project_name=self.event_log.process_name,
        )

        # Instantiate best BPS model
        self.best_bps_model = self.initial_bps_model.deep_copy()
        # Update best process model (save it in base directory)
        self.best_bps_model.process_model = get_process_model_path(self.base_directory, self.event_log.process_name)
        best_model_path = (
            best_result["process_model_path"] if self._need_to_discover_model else self.initial_bps_model.process_model
        )
        shutil.copyfile(best_model_path, self.best_bps_model.process_model)
        # Update simulation parameters (save them in base directory)
        best_parameters_path = get_simulation_parameters_path(self.base_directory, self.event_log.process_name)
        shutil.copyfile(
            get_simulation_parameters_path(best_result["output_dir"], self.event_log.process_name), best_parameters_path
        )
        self.best_bps_model.gateway_probabilities = [
            GatewayProbabilities.from_dict(gateway_probabilities)
            for gateway_probabilities in json.load(open(best_parameters_path, "r"))["gateway_branching_probabilities"]
        ]

        # Save evaluation measurements
        self.evaluation_measurements.sort_values("distance", ascending=True, inplace=True)
        self.evaluation_measurements.to_csv(self.base_directory / "evaluation_measures.csv", index=False)

        # Return settings of the best iteration
        return best_hyperopt_parameters

    def _define_search_space(self, settings: ControlFlowSettings) -> dict:
        space = {}
        if isinstance(settings.gateway_probabilities, list):
            space["gateway_probabilities_method"] = hp.choice(
                "gateway_probabilities_method", settings.gateway_probabilities
            )
        else:
            space["gateway_probabilities_method"] = settings.gateway_probabilities

        # Process model discovery parameters if we need to discover it
        if self._need_to_discover_model:
            if settings.mining_algorithm == ProcessModelDiscoveryAlgorithm.SPLIT_MINER_V1:
                if isinstance(settings.epsilon, tuple):
                    space["epsilon"] = hp.uniform("epsilon", settings.epsilon[0], settings.epsilon[1])
                else:
                    space["epsilon"] = settings.epsilon

                if isinstance(settings.eta, tuple):
                    space["eta"] = hp.uniform("eta", settings.eta[0], settings.eta[1])
                else:
                    space["eta"] = settings.eta

                if isinstance(settings.prioritize_parallelism, list):
                    space["prioritize_parallelism"] = hp.choice(
                        "prioritize_parallelism", [str(value) for value in settings.prioritize_parallelism]
                    )
                else:
                    space["prioritize_parallelism"] = str(settings.prioritize_parallelism)

                if isinstance(settings.replace_or_joins, list):
                    space["replace_or_joins"] = hp.choice(
                        "replace_or_joins", [str(value) for value in settings.replace_or_joins]
                    )
                else:
                    space["replace_or_joins"] = str(settings.replace_or_joins)
            elif settings.mining_algorithm == ProcessModelDiscoveryAlgorithm.SPLIT_MINER_V2:
                if isinstance(settings.epsilon, tuple):
                    space["epsilon"] = hp.uniform("epsilon", settings.epsilon[0], settings.epsilon[1])
                else:
                    space["epsilon"] = settings.epsilon

        if settings.discover_branch_rules and settings.f_score:
            if isinstance(settings.f_score, tuple):
                space["f_score"] = hp.uniform("f_score", settings.f_score[0], settings.f_score[1])
            else:
                space["f_score"] = settings.f_score

        return space

    def cleanup(self):
        remove_asset(self.base_directory)

    @staticmethod
    def _define_response(
        status: str, evaluation_measurements: list, output_dir: Path, process_model_path: Path
    ) -> Tuple[str, dict]:
        # Compute mean distance if status is OK
        if status is STATUS_OK:
            distance = np.mean([x["distance"] for x in evaluation_measurements])
            # Change status if distance value is negative
            if distance < 0.0:
                status = STATUS_FAIL
        else:
            distance = 1.0
        # Define response dict
        response = {
            "loss": distance,  # Loss value for the fmin function
            "status": status,  # Status of the optimization iteration
            "output_dir": output_dir,
            "process_model_path": process_model_path,
        }
        # Return updated status and processed response
        return status, response

    def _process_measurements(self, params: HyperoptIterationParams, status, evaluation_measurements):
        optimization_parameters = params.to_dict()
        optimization_parameters["status"] = status

        if status == STATUS_OK:
            for measurement in evaluation_measurements:
                values = {
                    "distance": measurement["distance"],
                    "metric": measurement["metric"],
                }
                values = values | optimization_parameters
                self.evaluation_measurements = pd.concat([self.evaluation_measurements, pd.DataFrame([values])])
        else:
            values = {
                "distance": 0,
                "metric": params.optimization_metric,
            }
            values = values | optimization_parameters
            self.evaluation_measurements = pd.concat([self.evaluation_measurements, pd.DataFrame([values])])

    def _discover_process_model(self, params: HyperoptIterationParams) -> Path:
        print_step(f"Discovering Process Model with {params.mining_algorithm.value}")
        output_model_path = get_process_model_path(params.output_dir, self.event_log.process_name)
        if params.mining_algorithm is ProcessModelDiscoveryAlgorithm.SPLIT_MINER_V1:
            discover_process_model(self._xes_train_only_end_log_path, output_model_path, params)
        else:
            discover_process_model(self._xes_train_both_timestamps_log_path, output_model_path, params)
        return output_model_path

    def _discover_branch_rules(self, process_model: Path, params: HyperoptIterationParams) -> List[BranchRules]:
        print_step(f"Discovering branch rules with f_score {params.f_score}")
        bpmn_graph = BPMNGraph.from_bpmn_path(process_model)
        return discover_branch_rules(
            bpmn_graph, self.event_log.train_partition, self.event_log.log_ids, f_score=params.f_score
        )

    def _discover_gateway_probabilities(
        self, process_model: Path, gateway_probabilities_method: GatewayProbabilitiesDiscoveryMethod
    ) -> List[GatewayProbabilities]:
        print_step(f"Computing gateway probabilities with {gateway_probabilities_method}")
        bpmn_graph = BPMNGraph.from_bpmn_path(process_model)
        return compute_gateway_probabilities(
            event_log=self.event_log.train_partition,
            log_ids=self.event_log.log_ids,
            bpmn_graph=bpmn_graph,
            discovery_method=gateway_probabilities_method,
        )

    def _simulate_bps_model(self, bps_model: BPSModel, output_dir: Path) -> List[dict]:
        bps_model.replace_activity_names_with_ids()

        json_parameters_path = bps_model.to_json(output_dir, self.event_log.process_name)
        evaluation_measures = simulate_and_evaluate(
            process_model_path=bps_model.process_model,
            parameters_path=json_parameters_path,
            output_dir=output_dir,
            simulation_cases=self.event_log.validation_partition[self.event_log.log_ids.case].nunique(),
            simulation_start_time=self.event_log.validation_partition[self.event_log.log_ids.start_time].min(),
            validation_log=self.event_log.validation_partition,
            validation_log_ids=self.event_log.log_ids,
            metrics=[self.settings.optimization_metric],
            num_simulations=self.settings.num_evaluations_per_iteration,
        )

        return evaluation_measures
