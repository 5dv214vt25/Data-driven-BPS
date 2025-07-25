import tempfile
from pathlib import Path

import pytest
from lxml import etree
from pix_framework.discovery.gateway_probabilities import GatewayProbabilitiesDiscoveryMethod
from pix_framework.io.bpmn import get_activities_names_from_bpmn

from simod.control_flow.discovery import discover_process_model
from simod.control_flow.settings import HyperoptIterationParams
from simod.settings.common_settings import Metric
from simod.settings.control_flow_settings import ProcessModelDiscoveryAlgorithm

control_flow_config_sm2 = {
    "mining_algorithm": "sm2",
    "epsilon": 0.3,
    "eta": 0.5,
    "replace_or_joins": True,
    "prioritize_parallelism": True,
}

control_flow_config_sm1 = {
    "mining_algorithm": "sm1",
    "epsilon": 0.3,
    "eta": 0.5,
    "replace_or_joins": True,
    "prioritize_parallelism": True,
}

structure_optimizer_test_data = [
    {"name": "Split Miner 2", "config_data": control_flow_config_sm2},
    {"name": "Split Miner 1", "config_data": control_flow_config_sm1},
]


@pytest.mark.integration
@pytest.mark.parametrize(
    "test_data", structure_optimizer_test_data, ids=[test_data["name"] for test_data in structure_optimizer_test_data]
)
def test_discover_process_model(entry_point, test_data):
    """Smoke test to check that the structure optimizer can be instantiated and run successfully."""
    log_path = entry_point / "PurchasingExample.xes"

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "model.bpmn"
        params = HyperoptIterationParams(
            output_dir=Path(tmp_dir),
            provided_model_path=None,
            project_name="PurchasingExample",
            optimization_metric=Metric.TWO_GRAM_DISTANCE,
            gateway_probabilities_method=GatewayProbabilitiesDiscoveryMethod.EQUIPROBABLE,
            mining_algorithm=ProcessModelDiscoveryAlgorithm.from_str(test_data["config_data"]["mining_algorithm"]),
            epsilon=test_data["config_data"]["epsilon"],
            eta=test_data["config_data"]["eta"],
            replace_or_joins=test_data["config_data"]["replace_or_joins"],
            prioritize_parallelism=test_data["config_data"]["prioritize_parallelism"],
        )
        discover_process_model(log_path, output_path, params)

        # Assert file exists
        assert output_path.exists()
        # Assert is BPMN readable and has activities
        activities = get_activities_names_from_bpmn(output_path)
        assert len(activities) > 0


@pytest.mark.parametrize(
    "test_data", structure_optimizer_test_data, ids=[test_data["name"] for test_data in structure_optimizer_test_data]
)
def test_discover_process_model_explicit_self_loops(entry_point, test_data):
    if test_data["config_data"]["mining_algorithm"] == "sm1":
        log_path = entry_point / "model_sequence_self_loop_only_end.xes"
    else:
        log_path = entry_point / "model_sequence_self_loop.xes"
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "model.bpmn"
        params = HyperoptIterationParams(
            output_dir=Path(tmp_dir),
            provided_model_path=None,
            project_name="SelfLoopTest",
            optimization_metric=Metric.TWO_GRAM_DISTANCE,
            gateway_probabilities_method=GatewayProbabilitiesDiscoveryMethod.DISCOVERY,
            mining_algorithm=ProcessModelDiscoveryAlgorithm.from_str(test_data["config_data"]["mining_algorithm"]),
            epsilon=test_data["config_data"]["epsilon"],
            eta=test_data["config_data"]["eta"],
            replace_or_joins=test_data["config_data"]["replace_or_joins"],
            prioritize_parallelism=test_data["config_data"]["prioritize_parallelism"],
        )
        discover_process_model(log_path, output_path, params)
        # Assert that no implicit self-loops are there
        tree = etree.parse(output_path)
        root = tree.getroot()
        ns = {"bpmn": root.nsmap.get(None, "http://www.omg.org/spec/BPMN/20100524/MODEL")}

        tasks = root.findall(".//bpmn:task", namespaces=ns)
        for task in tasks:
            assert (
                task.find("bpmn:standardLoopCharacteristics", namespaces=ns) is None
            ), f"Task '{task.get('name')}' has an implicit self loop"
        exclusive_gateways = root.findall(".//bpmn:exclusiveGateway", namespaces=ns)
        assert len(exclusive_gateways) == 2, "There should only be two exclusive gateways in this model"
        # Commented because SM2 doesn't sort the events, thus no parallelism
        # parallel_gateways = root.findall(".//bpmn:parallelGateway", namespaces=ns)
        # assert len(parallel_gateways) == 2, "There should only be two parallel gateways in this model"
