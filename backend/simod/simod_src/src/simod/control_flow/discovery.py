import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Tuple

from lxml import etree

from simod.cli_formatter import print_step
from simod.control_flow.settings import HyperoptIterationParams
from simod.settings.control_flow_settings import ProcessModelDiscoveryAlgorithm
from simod.utilities import execute_external_command
from simod.utilities import is_windows

global bpmn_layout_jar_path
global split_miner_jar_path

split_miner_jar_path: Path = Path(__file__).parent / "lib/split-miner-1.7.1-all.jar"
bpmn_layout_jar_path: Path = Path(__file__).parent / "lib/bpmn-layout-1.0.6-jar-with-dependencies.jar"


def discover_process_model(log_path: Path, output_model_path: Path, params: HyperoptIterationParams):
    """
    Runs the specified process model discovery algorithm to extract a process model
    from an event log and save it to the given output path.

    This function supports Split Miner V1 and Split Miner V2 as discovery algorithms.

    Parameters
    ----------
    log_path : :class:`pathlib.Path`
        Path to the event log in XES format, required for Split Miner algorithms.
    output_model_path : :class:`pathlib.Path`
        Path to save the discovered process model.
    params : :class:`~simod.resource_model.settings.HyperoptIterationParams`
        Configuration containing the process model discovery algorithm and its parameters.

    Raises
    ------
    ValueError
        If the specified process model discovery algorithm is unknown.
    """
    if params.mining_algorithm is ProcessModelDiscoveryAlgorithm.SPLIT_MINER_V1:
        discover_process_model_with_split_miner_v1(
            SplitMinerV1Settings(
                log_path,
                output_model_path,
                params.eta,
                params.epsilon,
                params.prioritize_parallelism,
                params.replace_or_joins,
            )
        )
    elif params.mining_algorithm is ProcessModelDiscoveryAlgorithm.SPLIT_MINER_V2:
        discover_process_model_with_split_miner_v2(SplitMinerV2Settings(log_path, output_model_path, params.epsilon))
    else:
        raise ValueError(f"Unknown process model discovery algorithm: {params.mining_algorithm}")
    # Assert that model file was created
    assert output_model_path.exists(), f"Error trying to discover the process model in '{output_model_path}'."
    # Post-process to transform implicit activity self-loops into explicit (modeled through gateways)
    print("Post-processing discovered process model to explicitly model self-loops through gateways.")
    post_process_bpmn_self_loops(output_model_path)


def _generate_node_id():
    return f"node_{uuid.uuid4()}"


def post_process_bpmn_self_loops(bpmn_model_path: Path):
    tree = etree.parse(bpmn_model_path)
    root = tree.getroot()
    nsmap = root.nsmap

    bpmn_namespace = nsmap.get(None, "http://www.omg.org/spec/BPMN/20100524/MODEL")
    ns = {"bpmn": bpmn_namespace}

    tasks = root.findall(".//bpmn:task", namespaces=ns)
    sequence_flows = root.findall(".//bpmn:sequenceFlow", namespaces=ns)
    process = root.find(".//bpmn:process", namespaces=ns)

    for task in tasks:
        loop_characteristics = task.find("bpmn:standardLoopCharacteristics", namespaces=ns)
        if loop_characteristics is not None:
            # Task with self-loop
            task_id = task.get("id")
            # Remove loop characteristics
            task.remove(loop_characteristics)
            # Generate unique IDs
            gt1_id = _generate_node_id()
            gt2_id = _generate_node_id()
            sf1_id = _generate_node_id()
            sf2_id = _generate_node_id()
            sf3_id = _generate_node_id()
            # Create exclusive gateways with attributes
            gt1 = etree.Element("{%s}exclusiveGateway" % bpmn_namespace, id=gt1_id, gatewayDirection="Converging")
            gt2 = etree.Element("{%s}exclusiveGateway" % bpmn_namespace, id=gt2_id, gatewayDirection="Diverging")
            process.append(gt1)
            process.append(gt2)
            # Modify existing sequence flows
            incoming_gt1_1, outgoing_gt2_1 = None, None
            for sf in sequence_flows:
                if sf.get("targetRef") == task_id:
                    sf.set("targetRef", gt1_id)
                    incoming_gt1_1 = etree.Element("{%s}incoming" % bpmn_namespace)
                    incoming_gt1_1.text = sf.get("id")
                if sf.get("sourceRef") == task_id:
                    sf.set("sourceRef", gt2_id)
                    outgoing_gt2_1 = etree.Element("{%s}outgoing" % bpmn_namespace)
                    outgoing_gt2_1.text = sf.get("id")
            # Create new sequence flows
            sf1 = etree.Element("{%s}sequenceFlow" % bpmn_namespace, id=sf1_id, sourceRef=gt1_id, targetRef=task_id)
            process.append(sf1)
            sf2 = etree.Element("{%s}sequenceFlow" % bpmn_namespace, id=sf2_id, sourceRef=task_id, targetRef=gt2_id)
            process.append(sf2)
            sf3 = etree.Element("{%s}sequenceFlow" % bpmn_namespace, id=sf3_id, sourceRef=gt2_id, targetRef=gt1_id)
            process.append(sf3)
            # Add incoming and outgoing elements for gateways
            outgoing_gt1_1 = etree.Element("{%s}outgoing" % bpmn_namespace)
            outgoing_gt1_1.text = sf1_id
            incoming_gt1_2 = etree.Element("{%s}incoming" % bpmn_namespace)
            incoming_gt1_2.text = sf3_id
            incoming_gt2_1 = etree.Element("{%s}incoming" % bpmn_namespace)
            incoming_gt2_1.text = sf2_id
            outgoing_gt2_2 = etree.Element("{%s}outgoing" % bpmn_namespace)
            outgoing_gt2_2.text = sf3_id
            gt1.append(incoming_gt1_1)
            gt1.append(incoming_gt1_2)
            gt1.append(outgoing_gt1_1)
            gt2.append(incoming_gt2_1)
            gt2.append(outgoing_gt2_1)
            gt2.append(outgoing_gt2_2)
    # Write to file
    tree.write(bpmn_model_path, xml_declaration=True, encoding="UTF-8", pretty_print=True)


def add_bpmn_diagram_to_model(bpmn_model_path: Path):
    """
    Add BPMN diagram to the control flow of the existing BPMN model using the hierarchical layout algorithm.
    This function overwrites the existing BPMN model file.

    :param bpmn_model_path:
    :return: None
    """

    # This row was changed from
    # args = ["java", "-jar", '"' + str(bpmn_layout_jar_path) + '"', '"' + str(bpmn_model_path) + '"']
    # This doesn't work on UNIX or MAC systems, however this was changed in the simod source code on 27th May,
    # three weeks after we had cloned the simod repo: https://github.com/AutomatedProcessImprovement/Simod
    # SHA for Simod commit fixing the bug on UNIX and MAC systems: d62096d3f4275cc4d4be9544e99274fa2a1a9e6b

    # Further the jar file that is executed here has been edited.
    args = ["java", "-jar", str(bpmn_layout_jar_path), str(bpmn_model_path)]
    print_step(f"Adding BPMN diagram to the model: {args}")
    execute_external_command(args)


@dataclass
class SplitMinerV1Settings:
    log_path: Path
    output_model_path: Path
    eta: float
    epsilon: float
    parallelism_first: bool  # Prioritize parallelism over loops
    replace_or_joins: bool  # Replace non-trivial OR joins
    remove_loop_activity_markers: bool = False  # False increases model complexity


@dataclass
class SplitMinerV2Settings:
    """
    Original author of Split Miner hardcoded eta, parallelism_first, replace_or_joins, and remove_loop_activity_markers
    values into the algorithm. It might have been done because it gives better results, but it is not clear.
    We pass only epsilon to Split Miner 2 for now.
    """

    log_path: Path
    output_model_path: Path
    epsilon: float


def discover_process_model_with_split_miner_v1(settings: SplitMinerV1Settings):

    args, split_miner_path, input_log_path, model_output_path = _prepare_split_miner_params(
        split_miner_jar_path, settings.log_path, settings.output_model_path, strip_output_suffix=False
    )

    args += [
        "-jar",
        split_miner_path,
        "--logPath",
        input_log_path,
        "--outputPath",
        model_output_path,
        "--eta",
        str(settings.eta),
        "--epsilon",
        str(settings.epsilon),
    ]

    # Boolean flags added only when they are True
    if settings.parallelism_first:
        args += ["--parallelismFirst"]
    if settings.replace_or_joins:
        args += ["--replaceIORs"]
    if settings.remove_loop_activity_markers:
        args += ["--removeLoopActivityMarkers"]

    print_step(f"SplitMiner v1 is running with the following arguments: {args}")
    execute_external_command(args)


def discover_process_model_with_split_miner_v2(settings: SplitMinerV2Settings):

    assert settings.epsilon is not None, "Epsilon must be provided for Split Miner v2."

    args, split_miner_path, input_log_path, model_output_path = _prepare_split_miner_params(
        split_miner_jar_path, settings.log_path, settings.output_model_path, strip_output_suffix=False
    )

    args += [
        "-jar",
        split_miner_path,
        "--logPath",
        input_log_path,
        "--outputPath",
        model_output_path,
        "--epsilon",
        str(settings.epsilon),
        "--splitminer2",  # Boolean flag is always added here to run Split Miner v2
    ]

    print_step(f"SplitMiner v2 is running with the following arguments: {args}")
    execute_external_command(args)


def _prepare_split_miner_params(
    split_miner: Path,
    log_path: Path,
    output_model_path: Path,
    strip_output_suffix: bool = True,
    headless: bool = True,
) -> Tuple[List[str], str, str, str]:
    if is_windows():
        # Windows: ';' as separator and escape string with '"'
        args = ["java"]
        if headless:
            args += ["-Djava.awt.headless=true"]
        split_miner_path = '"' + str(split_miner) + '"'
        input_log_path = '"' + str(log_path) + '"'
        if strip_output_suffix:
            model_output_path = '"' + str(output_model_path.with_suffix("")) + '"'
        else:
            if ".bpmn" not in str(output_model_path):
                model_output_path = str(output_model_path.with_suffix(".bpmn"))
            else:
                model_output_path = '"' + str(output_model_path) + '"'
    else:
        # Linux: ':' as separator and add memory specs
        args = ["java", "-Xmx2G", "-Xms1024M"]
        if headless:
            args += ["-Djava.awt.headless=true"]
        split_miner_path = str(split_miner)
        input_log_path = str(log_path)
        if strip_output_suffix:
            model_output_path = str(output_model_path.with_suffix(""))
        else:
            if ".bpmn" not in str(output_model_path):
                model_output_path = str(output_model_path.with_suffix(".bpmn"))
            else:
                model_output_path = str(output_model_path)

    return args, split_miner_path, input_log_path, model_output_path
