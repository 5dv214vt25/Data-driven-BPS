import uuid
from pathlib import Path
from typing import List

from extraneous_activity_delays.config import Configuration as ExtraneousActivityDelaysConfiguration
from extraneous_activity_delays.config import SimulationEngine
from extraneous_activity_delays.config import SimulationModel
from extraneous_activity_delays.config import TimerPlacement
from extraneous_activity_delays.enhance_with_delays import DirectEnhancer
from extraneous_activity_delays.enhance_with_delays import HyperOptEnhancer
from lxml import etree
from pix_framework.filesystem.file_manager import remove_asset

from simod.cli_formatter import print_step
from simod.event_log.event_log import EventLog
from simod.extraneous_delays.types import ExtraneousDelay
from simod.settings.extraneous_delays_settings import ExtraneousDelaysSettings
from simod.simulation.parameters.BPS_model import BPSModel


class ExtraneousDelaysOptimizer:
    """
    Optimizer for the discovery of the extraneous delays model.

    This class performs either a direct discovery of the extraneous delays of the process, or launches an iterative
    optimization that first discovers the extraneous delays and then adjusts their size to better reflect reality.

    Attributes
    ----------
    event_log : :class:`~simod.event_log.event_log.EventLog`
        The event log containing the train and validation data.
    bps_model : :class:`~simod.simulation.parameters.BPS_model.BPSModel`
        The business process simulation model to enhance with extraneous delays, including the BPMN representation.
    settings : :class:`~simod.settings.extraneous_delays_settings.ExtraneousDelaysSettings`
        Configuration settings for extraneous delay discovery.
    base_directory : :class:`pathlib.Path`
        Directory where output files will be stored.
    """

    def __init__(
        self,
        event_log: EventLog,
        bps_model: BPSModel,
        settings: ExtraneousDelaysSettings,
        base_directory: Path,
    ):
        self.event_log = event_log
        self.bps_model = bps_model
        self.settings = settings
        self.base_directory = base_directory

        assert self.bps_model.process_model is not None, "BPMN model is not specified."

    def run(self) -> List[ExtraneousDelay]:
        """
        Executes the extraneous delay discovery process.

        This method configures the optimization process, applies either a direct enhancement
        or a hyperparameter optimization approach to identify delays, and returns the best
        detected delays as a list of `ExtraneousDelay` objects.

        Returns
        -------
        List[:class:`~simod.extraneous_delays.types.ExtraneousDelay`]
            A list of detected extraneous delays, each containing activity names, delay IDs,
            and their corresponding duration distributions.
        """
        # Set-up configuration for extraneous delay discovery
        configuration = ExtraneousActivityDelaysConfiguration(
            log_ids=self.event_log.log_ids,
            process_name=self.event_log.process_name,
            num_iterations=self.settings.num_iterations,
            num_evaluation_simulations=self.settings.num_evaluations_per_iteration,
            training_partition_ratio=0.5,
            optimization_metric=self.settings.optimization_metric,
            discovery_method=self.settings.discovery_method,
            timer_placement=TimerPlacement.BEFORE,
            simulation_engine=SimulationEngine.PROSIMOS,
        )
        configuration.PATH_OUTPUTS = self.base_directory
        # Discover extraneous delays
        simulation_model = _bps_model_to_simulation_model(self.bps_model)
        if self.settings.num_iterations > 1:
            enhancer = HyperOptEnhancer(self.event_log.train_validation_partition, simulation_model, configuration)
            enhancer.enhance_simulation_model_with_delays()
            best_timers = enhancer.best_timers
        else:
            enhancer = DirectEnhancer(self.event_log.train_validation_partition, simulation_model, configuration)
            best_timers = enhancer.timers
        # Return best delays
        return [
            ExtraneousDelay(
                activity_name=activity,
                delay_id=f"Event_{str(uuid.uuid4())}",
                duration_distribution=best_timers[activity],
            )
            for activity in best_timers
        ]

    def cleanup(self):
        print_step(f"Removing {self.base_directory}")
        remove_asset(self.base_directory)


def _bps_model_to_simulation_model(bps_model: BPSModel) -> SimulationModel:
    parser = etree.XMLParser(remove_blank_text=True)
    bpmn_model = etree.parse(bps_model.process_model, parser)
    parameters = bps_model.to_prosimos_format()

    simulation_model = SimulationModel(bpmn_model, parameters)

    return simulation_model
