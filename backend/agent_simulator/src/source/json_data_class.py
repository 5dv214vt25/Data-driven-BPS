from dataclasses import dataclass


@dataclass
class JsonVisualization:
    agent_nodes: dict
    agent_edges: dict
    role_nodes: dict
    role_edges: dict
    activity_nodes: dict
    activity_edges: dict
    activity_flow: dict
