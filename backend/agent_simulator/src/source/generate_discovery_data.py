import json
import random
from collections import defaultdict

import networkx as nx
from pyvis.network import Network
from source.agent_types.calendar_discovery_parameters import int_week_days

# NOTE: TODO: This entire file is taken from PHD student Elizabeth's code that was given to us.
# Unfortiunately this is not public anywhere, and was give to us by a simple .zip file of entire repo.
# This code we are not entirely pleased with since it does not support central_orchistration or
# determine_automatically from what we can understand. For future implementation of paramters,
# some consideration should be taken with this file. Or if it is plauseble if this should be
# re-written entirely with some more support of the different simulation paramters.
# Some of her code can still be seen (& used) in visualization.py


def get_edges_between_agents(agents, agent_transition_probabilities):
    edges = []
    for agent in agents:
        for activity, transtion_agents_dict in agent_transition_probabilities[agent].items():
            for transition_agent, probability_dict in transtion_agents_dict.items():
                for trans_acitivity, probability in probability_dict.items():
                    probability = probability * 100
                    edges.append(
                        (
                            str(agent),
                            str(transition_agent),
                            activity,
                            trans_acitivity,
                            probability,
                        )
                    )
    return edges


def get_agent_with_highes_transition_probability(agents, agent_transition_probabilities):
    edges = []
    for agent in agents:
        for activity, transtion_agents_dict in agent_transition_probabilities[agent].items():
            max_probability = 0.0
            max_activity = ""
            transition_activity = ""
            trans_agent = ""
            for (
                transition_agent,
                activity_probability_dict,
            ) in transtion_agents_dict.items():
                if len(transtion_agents_dict) == 1:
                    max_probability = list(activity_probability_dict.values())
                    max_probability = max_probability[0]
                    trans_agent = transition_agent
                    max_activity = activity
                    transition_activity = list(activity_probability_dict.keys())[0]
                    edge = (
                        str(agent),
                        str(trans_agent),
                        max_activity,
                        transition_activity,
                        max_probability,
                    )

                    continue

                for trans_activity, probability in activity_probability_dict.items():
                    if probability > max_probability:
                        max_probability = probability
                        max_activity = activity
                        trans_agent = transition_agent
                        transition_activity = trans_activity

            max_probability = max_probability * 100
            edge = (
                str(agent),
                str(trans_agent),
                max_activity,
                transition_activity,
                max_probability,
            )
            if edge not in edges:
                edges.append(edge)
    return edges


def generate_random_color():
    """Generate a random HEX color."""
    r, g, b = [random.randint(0, 255) for _ in range(3)]
    return f"#{r:02x}{g:02x}{b:02x}"


def get_agent_for_role(agents, roles):
    agent_to_roles = {}
    for agent in agents:
        for role, agents_dict in roles.items():
            if int(agent) in agents_dict["agents"]:
                agent_to_roles[agent] = role
                break
    return agent_to_roles


def get_string_calendar(agent, resource_calendars):
    info = []
    agent = int(agent)

    for resource_id, calendar in resource_calendars.items():
        if resource_id == agent:
            info.append(f"Total Weekly Work: {calendar.total_weekly_work / 3600:.2f} Hours")
            for i in range(0, 7):
                if len(calendar.work_intervals[i]) > 0:
                    info.append(int_week_days[i])
                    for interval in calendar.work_intervals[i]:
                        info.append(
                            f"from {interval.start.hour:02d}:{interval.start.minute:02d} - "
                            f"to {interval.end.hour:02d}:{interval.end.minute:02d}"
                        )

    return "\n".join(info)


def get_interacting_resources(agent_transition_probabilities):
    interacting_resources = {}
    for agent, transition_dict in agent_transition_probabilities.items():
        interacting_resources[agent] = []
        for activity, transitions in transition_dict.items():
            for target_agent in list(transitions.keys()):
                if target_agent not in interacting_resources[agent]:
                    interacting_resources[agent].append(target_agent)
    return interacting_resources


def get_average_completion_time_per_activity(activity_duration_dict):
    duration_per_activity = {}
    for agent, activities_duration in activity_duration_dict.items():
        for activity, duration in activities_duration.items():
            if activity not in duration_per_activity.keys():
                duration_per_activity[activity] = {"duration": 0, "count": 0}
            if duration != []:
                duration_per_activity[activity]["duration"] += duration.mean
                duration_per_activity[activity]["count"] += 1
    avg_duration_per_activity = {
        activity: data["duration"] / data["count"] for activity, data in duration_per_activity.items()
    }
    return avg_duration_per_activity


def get_resource_information(
    resource_calendars,
    activity_duration_dict,
    agent_for_role,
    agent_to_resource,
    agent_transition_probabilities,
):
    avg_duration_per_activity = get_average_completion_time_per_activity(activity_duration_dict)
    interacting_agents_dict = get_interacting_resources(agent_transition_probabilities)
    resource_information = {}
    for agent, resource in agent_to_resource.items():
        resource_information[resource] = {}
        resource_information[resource]["calendar"] = get_string_calendar(agent, resource_calendars)
        resource_information[resource]["role"] = agent_for_role.get(str(agent))

        interacting_agents = interacting_agents_dict.get(agent)
        interacting_resources = [agent_to_resource.get(interacting_agent) for interacting_agent in interacting_agents]
        resource_information[resource]["interacting_resources"] = "\n".join(interacting_resources)

        resource_information[resource]["activities"] = {}
        for curr_agent, activities_duration in activity_duration_dict.items():
            if curr_agent != agent:
                continue
            for activity, duration in activities_duration.items():
                if activity == "zzz_end":
                    continue
                performer = "Low Performer"
                if duration != []:
                    hours_mean = int(duration.mean // 3600)
                    minutes_mean = int((duration.mean % 3600) // 60)

                    hours_std = int(duration.std // 3600)
                    minutes_std = int((duration.std % 3600) // 60)

                    if duration.mean < avg_duration_per_activity.get(activity):
                        performer = "High Performer"

                    resource_information[resource]["activities"][
                        activity
                    ] = f"Average Completion Time: {hours_mean}h {minutes_mean}min, Deviation: {hours_std}h {minutes_std}min, Performer: {performer}"
            resource_information[resource]["activities"] = dict(
                sorted(resource_information[resource]["activities"].items())
            )

    return resource_information


def get_all_activities(max_activity_count_per_case):
    activities = []
    for activity in max_activity_count_per_case.keys():
        activities.append(activity)
    return activities


def get_probabilites_between_roles(agents, agent_transition_probabilities, roles):
    probabilities_betwenn_roles = {}
    agent_to_role = get_agent_for_role(agents, roles)
    for agent in agents:
        agent_role = agent_to_role[agent]
        if agent_role not in probabilities_betwenn_roles.keys():
            probabilities_betwenn_roles[agent_role] = {}
        for activity, transtion_agents_dict in agent_transition_probabilities[agent].items():
            for transition_agent, probability_dict in transtion_agents_dict.items():
                transition_agent_role = agent_to_role[transition_agent]
                if transition_agent_role not in probabilities_betwenn_roles[agent_role].keys():
                    probabilities_betwenn_roles[agent_role][transition_agent_role] = 1
                else:
                    probabilities_betwenn_roles[agent_role][transition_agent_role] += 1

    for role, transition_roles_dict in probabilities_betwenn_roles.items():
        total_activities = sum(transition_roles_dict.values())
        for transition_role, num_activities in transition_roles_dict.items():
            probabilities_betwenn_roles[role][transition_role] = (num_activities / total_activities) * 100

    return probabilities_betwenn_roles


def get_all_activities_for_role_as_string(agents, target_role, agent_for_role, agent_transition_probabilities):
    activities = []
    for agent in agents:
        if agent_for_role.get(str(agent)) == target_role:
            for activity, transtion_agents_dict in agent_transition_probabilities[agent].items():
                if activity not in activities and activity != "zzz_end":
                    activities.append(activity)
    return "\n".join(activities)


def get_starting_agents(transition_probabilities, starting_activity):
    starting_agents = []
    for agent, transition_activities in transition_probabilities.items():
        for transition_activity, proabilities_dict in transition_activities.items():
            if transition_activity == starting_activity:
                starting_agents.append(str(agent))

    return starting_agents


def get_activity_flow_for_starting_agent(agents, transition_probabilities, starting_activity):
    all_edges_sorted_by_probability = sorted(
        get_edges_between_agents(agents, transition_probabilities),
        key=lambda x: x[4],
        reverse=True,
    )
    starting_agents = get_starting_agents(transition_probabilities, starting_activity)
    activity_flow_for_agent = {}

    def trace_activity_flow(current_agent, current_activity, visited_activities):
        flow = [current_activity]
        while current_activity != "zzz_end":
            next_edge = None
            for edge in all_edges_sorted_by_probability:
                start_resource, end_resource, activity, trans_activity, probability = edge
                if start_resource == current_agent and activity == current_activity:
                    if trans_activity not in visited_activities or trans_activity == "zzz_end":
                        next_edge = edge
                        break
            if not next_edge:
                break

            start_resource, end_resource, activity, trans_activity, probability = next_edge

            flow.append(trans_activity)
            current_agent, current_activity = end_resource, trans_activity

            if trans_activity == "zzz_end":
                break

            visited_activities.add(trans_activity)

        flow.insert(0, "Process Start")
        return flow

    for starting_agent in starting_agents:
        activity_flow_for_agent[starting_agent] = trace_activity_flow(
            starting_agent, starting_activity, set([starting_activity])
        )

    return activity_flow_for_agent


# Returns: agent_nodes_json, agent_edges_json, role_nodes_json, role_edges_json, activity_nodes_json, activity_edges_json, activity_flow_json
def create_interactive_network(discovered_simulation_parameters, starting_activity):

    roles = discovered_simulation_parameters["roles"]
    agent_transition_probabilities = discovered_simulation_parameters["agent_transition_probabilities"]
    transition_probabilities = discovered_simulation_parameters["transition_probabilities"]
    agent_to_resource = discovered_simulation_parameters["agent_to_resource"]
    # resource_calendars = discovered_simulation_parameters["res_calendars"]
    activity_duration_dict = discovered_simulation_parameters["activity_durations_dict"]

    max_activity_count_per_case = discovered_simulation_parameters["max_activity_count_per_case"]

    # TODO: Kev - edge case for when central_orhcistration is True
    # See line 742 in discovery.py (our gitlab)
    # See line 664 in discovery.py (lukas github)
    # Don't exactly know why this is needed or why this is not set when discovering the
    # Simulation paramters, This should probably be further looked into if someone gets more time
    # (will not be done bcus no-one has any time at all)

    # if agent_transition_probabilities is None:
    #     agent_transition_probabilities = discovered_simulation_parameters["agent_transition_probabilities_autonomous"]

    activity_flow_for_starting_agent = get_activity_flow_for_starting_agent(
        list(agent_transition_probabilities.keys()),
        agent_transition_probabilities,
        starting_activity,
    )

    agents = [str(agent) for agent in agent_transition_probabilities.keys()]

    # Get agent network data
    edges_between_agents = get_edges_between_agents(
        list(agent_transition_probabilities.keys()), agent_transition_probabilities
    )

    edges_between_agents_max_probability = get_agent_with_highes_transition_probability(
        list(agent_transition_probabilities.keys()), agent_transition_probabilities
    )

    # Get role network data
    edges_between_roles = get_probabilites_between_roles(
        list(agent_transition_probabilities.keys()),
        agent_transition_probabilities,
        roles,
    )

    activities = get_all_activities(max_activity_count_per_case)

    agent_for_role = get_agent_for_role(agents, roles)
    unique_roles = set(agent_for_role.values())
    role_colors = {role: generate_random_color() for role in unique_roles}
    activity_colors = {activity: generate_random_color() for activity in activities if activity != "zzz_end"}

    # resource_information = get_resource_information(
    #    resource_calendars,
    #    activity_duration_dict,
    #    agent_for_role,
    #    agent_to_resource,
    #    agent_transition_probabilities,
    # )

    get_average_completion_time_per_activity(activity_duration_dict)

    # Create agent network
    g = nx.DiGraph()

    for agent in agents:
        g.add_node(
            agent,
            role=agent_for_role.get(agent, "Unknown"),
        )
    g.add_edges_from(
        [
            (source, target, {"activity": activity, "probability": probability})
            for source, target, activity, trans_activity, probability in edges_between_agents
        ]
    )

    net = Network(
        directed=True,
        cdn_resources="remote",
        height="100%",
        width="100%",
        notebook=True,
    )

    # Organize agent nodes by role
    roles_to_agents = defaultdict(list)

    for agent in agents:
        role = agent_for_role.get(agent, "Unknown")
        roles_to_agents[role].append(agent)

    for role in roles_to_agents:
        roles_to_agents[role] = sorted(roles_to_agents[role], key=lambda x: int(x))

    max_agents_role = max(roles_to_agents.items(), key=lambda x: len(x[1]))
    max_agents_count = len(max_agents_role[1])

    horizontal_spacing = 100
    vertical_spacing = 400

    total_height = max_agents_count * horizontal_spacing

    role_order = {}
    for role, role_agents in roles_to_agents.items():
        if role_agents:
            min_agent_id = min(int(agent) for agent in role_agents)
            role_order[role] = min_agent_id

    sorted_roles = sorted(role_order.keys(), key=lambda role: role_order[role])

    role_vertical_positions = {}
    for i, role in enumerate(sorted_roles):
        role_vertical_positions[role] = i

    # Position agent nodes
    nodes_by_position = {}

    for role in sorted_roles:
        role_agents = roles_to_agents[role]
        num_agents = len(role_agents)

        if num_agents == max_agents_count:
            spacing = total_height / (num_agents - 1 if num_agents > 1 else 1)
        else:
            spacing = total_height / (num_agents - 1 if num_agents > 1 else 1)

        y_positions = []
        if num_agents == 1:
            y_positions = [total_height / 2]
        else:
            for j in range(num_agents):
                y_positions.append(j * spacing)

        sorted_role_agents = sorted(role_agents, key=lambda x: int(x))

        x_pos = role_vertical_positions[role] * vertical_spacing
        for j, agent in enumerate(sorted_role_agents):
            nodes_by_position[agent] = {
                "id": agent,
                "role": role,
                "color": role_colors[role],
                "x": x_pos,
                "y": y_positions[j],
            }

    # Add agent nodes to network
    agent_nodes_data = []
    for agent, node_data in nodes_by_position.items():
        agent_node = {
            "id": node_data["id"],
            "color": node_data["color"],
            "label": agent_to_resource[int(node_data["id"])],
            "x": node_data["x"],
            "y": node_data["y"],
            "fixed": True,
            "shape": "dot",
            "size": 25,
        }
        agent_nodes_data.append(agent_node)

    # Prepare role nodes
    role_nodes_data = []
    for i, role in enumerate(sorted_roles):
        x_pos = i * vertical_spacing
        role_node = {
            "id": role,
            "color": role_colors[role],
            "label": role,
            "x": x_pos,
            "y": total_height,
            "fixed": True,
            "size": 50,
            "shape": "square",
        }
        role_nodes_data.append(role_node)

    # Prepare activity nodes
    activity_frequencies = {}
    for agent in agent_transition_probabilities.keys():
        for activity in agent_transition_probabilities[agent].keys():
            if activity not in activity_frequencies:
                activity_frequencies[activity] = 0
            activity_frequencies[activity] += 1

    sorted_activities = []
    if starting_activity in activities:
        sorted_activities.append(starting_activity)

    for activity in sorted([a for a in activities if a != starting_activity]):
        sorted_activities.append(activity)

    activity_nodes_data = []
    activity_horizontal_spacing = 300

    sorted_activities.insert(0, "Process Start")

    for i, activity in enumerate(sorted_activities):
        shape = "dot"
        label = activity
        if activity == "Process Start":
            shape = "triangle"
        elif activity == "zzz_end":
            shape = "square"
            label = "Process End"

        activity_node = {
            "id": f"activity_{activity}",
            "title": f"Activity: {activity}",
            "label": label,
            "color": "#4286f4",
            "x": i * activity_horizontal_spacing,
            "y": total_height / 2,
            "fixed": True,
            "shape": shape,
            "size": 25,
        }
        activity_nodes_data.append(activity_node)
        net.add_node(
            n_id=activity_node["id"],
            title=activity_node["title"],
            color=activity_node["color"],
            label=activity_node["label"],
            x=activity_node["x"],
            y=activity_node["y"],
            fixed=activity_node["fixed"],
            shape=activity_node["shape"],
            size=activity_node["size"],
        )

    # Prepare agent edges
    agent_edges_data = []
    edge_id_count = defaultdict(int)
    for source, target, activity, trans_activity, probability in edges_between_agents:
        is_max_prob = any(
            (source, target, activity, trans_activity, prob) in edges_between_agents_max_probability
            for prob in [probability]
        )

        edge_id_base = f"{source}-{target}-{activity}"
        edge_id_count[edge_id_base] += 1
        edge_id = f"{edge_id_base}-{edge_id_count[edge_id_base]}"

        edge_data = {
            "id": edge_id,
            "from": source,
            "to": target,
            "smooth": {"type": "curvedCW", "roundness": 0.3},
            "arrows": "to",
            "color": activity_colors.get(activity, "#000000"),
            "label": f"{probability:.2f}%",
            "activity": activity,
            "probability": probability,
            "isMaxProbability": is_max_prob,
        }
        agent_edges_data.append(edge_data)

    # Prepare role edges
    role_edges_data = []
    # for source_role, target_role, activity, probability in edges_between_roles:
    for source_role, target_roles_dict in edges_between_roles.items():

        for target_role, probability in target_roles_dict.items():
            if source_role in sorted_roles and target_role in sorted_roles:
                edge_id_base = f"{source_role}-{target_role}"
                edge_id_count[edge_id_base] += 1
                edge_id = f"{edge_id_base}-{edge_id_count[edge_id_base]}"
                edge_data = {
                    "id": edge_id,
                    "from": source_role,
                    "to": target_role,
                    "color": "black",
                    "smooth": {"type": "curvedCW", "roundness": 0.3},
                    "arrows": "to",
                    "label": f"{probability:.2f}%",
                    "probability": probability,
                }
                role_edges_data.append(edge_data)

    # Prepare activity edges
    activity_edges_data = []
    edge_id_count = defaultdict(int)

    activity_transitions_probabilites_edge_count = defaultdict(lambda: defaultdict(int))

    activity_transitions = defaultdict(lambda: defaultdict(int))

    # Dictonary that holds the activity transition probability
    activity_transitions_probabilites = defaultdict(lambda: defaultdict(float))

    for agent in agent_transition_probabilities.keys():
        for source_activity, targets in agent_transition_probabilities[agent].items():
            for target_agent, activity_probs in targets.items():
                for target_activity, prob in activity_probs.items():
                    activity_transitions[source_activity][target_activity] += 1

    # TODO: Kev, fixed this part here so that central-orch works, however this might not be correct and changes the
    # actual simulation output, however this is needed according to Jack (from robert and lukas) since the simulation
    # should work on all eventlogs with no exceptions.
    # I suppose this is a problem since we relied on Elizabeth's code and visualization to much.
    # If this is urther developed, another way of generating some output of the discovery phase
    # might be better and more concise with other simulators (simod).
    # This should be further looked into since I currently have no more time left on this project!

    # This outcommented code below was experimental in order to get central_orchestration to work
    # Personal reccomentedtion on how to develop this further is to re-do how the vizualisation gets
    # it's values, right not central_orch and determ._auto is not supported (re-write a lot of this
    # because certain dictionaires that are used are simply not even initialized when these settings
    # are enabled)

    # for source_activity in transition_probabilities.keys():
    #     for target_activity, target in transition_probabilities[source_activity].items():
    #
    #         if discovered_simulation_parameters["central_orchestration"] is True:
    #             if isinstance(target, dict):
    #                 for target_activity, activity_probs in target.items():
    #                     activity_transitions_probabilites_edge_count[source_activity][target_activity] += 1
    #                     activity_transitions_probabilites[source_activity][target_activity] += activity_probs
    #             else:
    #                 activity_transitions_probabilites_edge_count[source_activity][target_activity] += 1
    #                 activity_transitions_probabilites[source_activity][target_activity] += target
    #         else:

    #             for target_activity, activity_probs in target.items():
    #                 activity_transitions_probabilites_edge_count[source_activity][target_activity] += 1
    #                 activity_transitions_probabilites[source_activity][target_activity] += activity_probs

    for source_activity in transition_probabilities.keys():
        for target_agent, target in transition_probabilities[source_activity].items():

            for target_activity, activity_probs in target.items():
                activity_transitions_probabilites_edge_count[source_activity][target_activity] += 1

                # Estimation of the activity transition probability based on source -> target activity
                activity_transitions_probabilites[source_activity][target_activity] += activity_probs

    for source_activity, targets in activity_transitions.items():
        total_transitions = sum(targets.values())

        source_activity_tuple = (source_activity,)
        for target_activity, count in targets.items():
            probability = (count / total_transitions) * 100

            # Estimates the transition probabilites based on the mean value
            p = activity_transitions_probabilites[source_activity_tuple][target_activity]
            n = activity_transitions_probabilites_edge_count[source_activity_tuple][target_activity]
            probability = p / n * 100

            edge_id_base = f"activity_{source_activity}-activity_{target_activity}"
            edge_id_count[edge_id_base] += 1
            edge_id = f"{edge_id_base}-{edge_id_count[edge_id_base]}"

            edge_data = {
                "id": edge_id,
                "from": f"activity_{source_activity}",
                "to": f"activity_{target_activity}",
                "color": "black",
                "smooth": {"type": "curvedCW", "roundness": 0.3},
                "arrows": "to",
                "label": f"{probability:.2f}%",
                "probability": probability,
            }
            activity_edges_data.append(edge_data)

            net.add_edge(
                source=edge_data["from"],
                to=edge_data["to"],
                id=edge_data["id"],
                smooth=edge_data["smooth"],
                arrows=edge_data["arrows"],
                color=edge_data["color"],
                label=edge_data["label"],
                probability=edge_data["probability"],
            )

    process_start_edge = {
        "id": "activity_Process Start-activity_" + starting_activity,
        "from": "activity_Process Start",
        "to": f"activity_{starting_activity}",
        "color": "black",
        "smooth": {"type": "curvedCW", "roundness": 0.3},
        "arrows": "to",
        "label": "100%",
    }

    activity_edges_data.append(process_start_edge)

    net.add_edge(
        source=process_start_edge["from"],
        to=process_start_edge["to"],
        id=process_start_edge["id"],
        smooth=process_start_edge["smooth"],
        arrows=process_start_edge["arrows"],
        color=process_start_edge["color"],
        label=process_start_edge["label"],
    )

    options = {
        "layout": {"improvedLayout": True, "hierarchical": {"enabled": False}},
        "physics": {"enabled": False},
        "edges": {
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.4}},
            "smooth": {"enabled": True, "type": "curvedCW", "roundness": 0.1},
            "selfReference": {"size": 20, "angle": 0.7853981634},
            "color": {"inherit": "from"},
        },
        "margin": {"right": 300},
    }

    net.set_options(json.dumps(options))

    # Pass role network data to JavaScript
    agent_nodes_json = json.dumps(agent_nodes_data)
    agent_edges_json = json.dumps(agent_edges_data)
    role_nodes_json = json.dumps(role_nodes_data)
    role_edges_json = json.dumps(role_edges_data)
    activity_nodes_json = json.dumps(activity_nodes_data)
    activity_edges_json = json.dumps(activity_edges_data)

    activity_flow_json = json.dumps(activity_flow_for_starting_agent)

    return {
        "agent_nodes": agent_nodes_json,
        "agent_edges": agent_edges_json,
        "role_nodes": role_nodes_json,
        "role_edges": role_edges_json,
        "activity_nodes": activity_nodes_json,
        "activity_edges": activity_edges_json,
        "activity_flow": activity_flow_json,
    }
