import copy

# import sys
from typing import Dict

from source.discovery import compute_activity_duration_distribution_per_agent
from source.discovery import get_case_arrival_times

# This file holds a bunch of small functions that manipulate a sim_config object.
# This is done to change the output of the simulation that is ran on a SimulationConfig object.


# ==================== Parameter Changing Functions ====================


def change_start_time(sim_config, dt):
    sim_config.sim_instance.simulation_parameters["start_timestamp"] = dt

    sim_config.sim_instance.simulation_parameters["case_arrival_times"], _ = get_case_arrival_times(
        sim_config.sim_instance.df_train,
        sim_config.sim_instance.simulation_parameters["start_timestamp"],
        sim_config.sim_instance.num_cases_to_simulate,
        train=True,
    )


def change_inter_arrival_distribution(simulation_config, user_input):
    """
    NOTE: Start time needs to be set before this function, because start_time is used!

    Changes the distribution method for inter arrival times between cases
    currently supports mean value, or normal distribution.
    Args:
        simulation_config: A simulation_config instance
        user_input: "normal" or "mean" corresponding to normal distribution or the mean as a fixed value distr.

    Returns: The modified simulation_config object with the new distribution for arrival times.
    """

    simulation_config.sim_instance.simulation_parameters["distribution_type"] = user_input

    start_time_here = simulation_config.sim_instance.simulation_parameters["start_timestamp"]

    simulation_config.sim_instance.simulation_parameters["case_arrival_times"], _ = get_case_arrival_times(
        simulation_config.sim_instance.df_train,
        start_time_here,
        simulation_config.sim_instance.num_cases_to_simulate,
        train=True,
        user_input=user_input,
    )


def change_distribution_activity_durations(simulation_config, user_input):
    simulation_config.sim_instance.simulation_parameters["activity_durations_dict"] = (
        compute_activity_duration_distribution_per_agent(
            simulation_config.sim_instance.df_train,
            simulation_config.sim_instance.simulation_parameters["res_calendars"],
            simulation_config.sim_instance.simulation_parameters["roles"],
            user_input,
        )
    )


def rename_agent(agent_to_resource, old_agent_id, new_name):
    """
    Function that lets the user rename a resource in the discovered parameters.
    Args:
        agent_to_resource (dict): A dictionary that maps agent id to resource
        old_agent_id (int): The id of the old agent
        new_name (str): The new name
    Returns:
        the updated agent_to_resource dictionary
    """

    # Update the mapping dictionary
    agent_to_resource[old_agent_id] = new_name

    return agent_to_resource


def change_num_cases(sim_config, new_num_cases_to_simulate):
    """
    Function "re-discovers" all case start times, makes it possible to simulate
    more cases than what was specified by the discovery phase.
    """

    sim_config.sim_instance.num_cases_to_simulate = new_num_cases_to_simulate

    case_arrival_times, train_params = get_case_arrival_times(  # "Re-discovers" case arrival time
        sim_config.sim_instance.df_train,
        start_timestamp=sim_config.sim_instance.simulation_parameters["start_timestamp"],
        num_cases_to_simulate=sim_config.sim_instance.num_cases_to_simulate,
        train=True,  # TODO: Fix this in the future so that Train could be false
    )
    sim_config.sim_instance.simulation_parameters["case_arrival_times"] = case_arrival_times


def apply_simple_overrides(sim_cfg, overrides: Dict[str, float]) -> None:
    """
    Apply simple single-valued overrides (e.g., num_simulations) on sim_cfg.
    """
    for key, val in overrides.items():
        setter = f"_set_{key}"
        if hasattr(sim_cfg, setter):
            getattr(sim_cfg, setter)(val)
        elif hasattr(sim_cfg, key):
            setattr(sim_cfg, key, val)
        else:
            raise KeyError(f"No field or setter for '{key}' on SimulationConfig")

        if hasattr(sim_cfg, "params") and key in sim_cfg.params:
            sim_cfg.params[key] = val


def apply_global_activity_overrides(sim_cfg, activity_durations: Dict[str, float]) -> None:
    """
    Override global activity durations in both params and live simulator.
    """

    sim = sim_cfg.sim_instance
    sim_cfg.params.setdefault("activity_duration_map", {})
    for act_name, dur in activity_durations.items():
        sim_cfg.params["activity_duration_map"][act_name] = dur
        sim.override_activity_duration(act_name, dur)


def apply_agent_activity_overrides(sim_cfg, agent_activity_durations: Dict[int, Dict[str, float]]) -> None:
    """
    Override per-agent activity durations in both params and live simulator.
    """

    sim = sim_cfg.sim_instance
    sim_cfg.params.setdefault("agent_activity_duration_map", {})
    for agent_id, act_map in agent_activity_durations.items():
        str_id = str(agent_id)
        sim_cfg.params["agent_activity_duration_map"].setdefault(str_id, {})
        for act_name, dur in act_map.items():
            sim_cfg.params["agent_activity_duration_map"][str_id][act_name] = dur
            sim.override_agent_activity_duration(agent_id, act_name, dur)


def change_agent_schedule(res_calendars, target_agent_id, days, new_schedule):
    """
    Update the RCalendar of a single agent.

    Args:
      res_calendars: dict[int, RCalendar]
        mapping from resource-ID → RCalendar instance
      target_agent_id: int
        which agent to modify
      days: list[str]
        e.g. ["MONDAY","TUESDAY"]
      new_schedule: list[list[str]]
        e.g. [["09:00:00","12:00:00"], ...]

    Returns:
      None (modifies the calendars in-place)
    """
    # look up the RCalendar object by its agent ID
    cal = res_calendars.get(int(target_agent_id))
    if cal is None:
        raise KeyError(f"No calendar for agent {target_agent_id}")

    # For each weekday, pull out the matching sub-list of intervals
    for day_str, day_schedule in zip(days, new_schedule):
        # day_schedule is e.g. [["05:00:00","12:00:00"], ["13:00:00","15:00:00"]]
        cal.update_day_schedule(day_str, day_schedule)


def update_agent_count(sim_config, changes):
    """
    This is the main fucntion that gets called when the agent counts should
    be updated. This then calls helper functions that parses the input and
    later calls two functions that adds or removes agents from the simulation.

    Args:
                sim_config - The simulation config to update
        changes - The passed value taken from the json input.
                                  Values then gets extracted in the helper functions
                  which are later used to remove / add agents.
    """

    # List looks like this: [(0, 2), (4, 0), (1, 2)] "raw"
    deactivate_list = _get_agents_to_deactivate_from_count_changes(changes)

    deactivate_agents(sim_config, deactivate_list)

    duplicate_list = _get_agents_to_duplicate_from_count_changes(changes)
    duplicate_agents(sim_config, duplicate_list)


def change_transition_probabilities(config_transition_probabilities, js_transition_probabilities):
    """
    Function updates the transition probabilites based based on the input parameter data. Updates every
    occurence in config_transition_probabilities by corresponding to js_transition_probabilities.

    Args:
        config_transition_probabilities: Dictionary with parameters to be updated
        js_transition_probabilities: Dictonary with parameters to update the simulation with

    Returns:
        The updated dictonary

    """

    # Loops over all source activities
    for source_activity in js_transition_probabilities.keys():

        source_activity_t = eval(source_activity)  # Converts string representation into an actual tuple

        # Ensure source_activity exists in config_transition_probabilities
        if source_activity_t not in config_transition_probabilities:
            config_transition_probabilities[source_activity_t] = {}

        # Loops over all target agents
        for target_agent, target in js_transition_probabilities[source_activity].items():

            target_agent_t = eval(target_agent)  # Converts string representation into an actual tuple

            # Ensure target_activity exists before assigning
            if target_agent_t not in config_transition_probabilities[source_activity_t]:
                config_transition_probabilities[source_activity_t][target_agent_t] = {}

            # Loops over all target activities
            for target_activity, activity_probs in target.items():
                config_transition_probabilities[source_activity_t][target_agent_t][target_activity] = activity_probs

    return config_transition_probabilities


def deactivate_agents(sim_config, deacivated_agents_list):
    """
    Fucntion to deactivate certain agents so that they are not created when the simulation is ran.

    NOTE:
        This behaviour is "experimental". When certain agents are removed, the simulation does not end,
        this is because agents hand-over their task to certain agents that are now removed.

    Args:
        sim_config: The config to change the active agents
        agent_to_be_deactivated (int): The agent_id that should be de-activated

    Returns:
        None

    """

    # print(f"\n\nDEACTIVATED AGENTS: \n {deacivated_agents_list}\n\n")
    sim_config.sim_instance.simulation_parameters["deactivated_resources"] = deacivated_agents_list


def duplicate_agents(sim_config, duplicated_agents_list):
    """
    Function to update the agent count of all agents. This created / removes agents from the simulation.
    All created agents are a "clone" of a base agent that was there from the beginning

    Args:
        :sim_config - SimulationConfig class
        :duplicated_agent_list - count of agents to change

        [(3, 2), (5, 3)],
        creates one more of agent 3. (1 is base)
        Creates two more of agent 5 (1 is base)

    """

    _add_new_agents(sim_config, duplicated_agents_list)
    _clone_base_agent(sim_config, duplicated_agents_list)


def _add_new_agents(sim_config, agents_to_duplicate, new_name_prefix="DUPE"):
    """
    Updates the count of total agents. By adding more of an agent. This agents name is
    DUPE_(NAME)_(ID)_(count)
    """

    simulation_parameters = sim_config.sim_instance.simulation_parameters

    simulation_parameters.setdefault("duplicated_agents_mapping", {})
    simulation_parameters["duplicated_agents"] = agents_to_duplicate

    current_max_id = max(simulation_parameters["agent_to_resource"].keys(), default=-1)

    # print(f"Duplicating agents: {agents_to_duplicate}")
    for original_id, count in agents_to_duplicate:
        original_name = simulation_parameters["agent_to_resource"][original_id]

        for i in range(count - 1):  # if count == 2 we create 1 new
            current_max_id += 1
            new_name = f"{new_name_prefix}_{original_name}_{original_id}_({i})"

            simulation_parameters["agent_to_resource"][current_max_id] = new_name
            simulation_parameters["duplicated_agents_mapping"][current_max_id] = original_id

            # print(f"Duplicated agent {original_id} -> {current_max_id} with name '{new_name}'")


def _clone_base_agent(sim_config, duplicated_agents_list):
    """
    Helper function that clones some of the neccesary dictionaries to make the simulation
    run with the new agents.
    """
    # Makes each clone have same activity as "parent"
    _update_activity_mapping(sim_config, duplicated_agents_list)

    # initializes a role for the clone
    _init_cloned_role(sim_config, duplicated_agents_list)

    # Calendear as the base
    _clone_calendar(sim_config)

    # Might not be needed with new way of adding agents and making htem work.
    # Clones some of the agnents transition probabilites
    _clone_transition_probabilities_1(sim_config)


def _init_cloned_role(sim_config, duplicated_agents_list):
    """
    Adds each of the cloned agents to the same role that the base agent has.
    Args:
                duplicated_agents_list - list of tuple: [(clone_id, original_id), (clone_id, original_id)]
    """
    simulation_parameters = sim_config.sim_instance.simulation_parameters
    roles = simulation_parameters["roles"]

    for clone_id, original_id in duplicated_agents_list:
        for role_name, role_data in roles.items():
            if original_id in role_data["agents"]:
                role_data["agents"].append(clone_id)


def _clone_transition_probabilities_1(sim_config):
    """
    TODO: Might not be needed, was used experimental at first to make agents actually take on tasks
                  however another way of calculating agents that could work on a task has been used since
          this func was implemented.
    """

    simulation_parameters = sim_config.sim_instance.simulation_parameters

    duplicated_agents_mapping = simulation_parameters["duplicated_agents_mapping"]

    probability_dicts_to_clone = [
        "transition_probabilities",
        "transition_probabilities_autonomous",
        "agent_transition_probabilities_autonomous",
        "agent_transition_probabilities",
    ]

    for dict_name in probability_dicts_to_clone:
        prob_dict = simulation_parameters.get(dict_name, {})

        # TODO: this handles edge case when central_orch is True so that agent_transition_probs is not initailized
        # Look into this in the future, central_orch and determine_auto does not initialize these dictionaries
        # Currently central_orch and determine_auto is simply not supported on the frontend
        if prob_dict is not None:
            for prefix, agent_probs in prob_dict.items():
                for agent_id, base_agent in duplicated_agents_mapping.items():
                    if base_agent in agent_probs:
                        agent_probs[agent_id] = copy.deepcopy(agent_probs[base_agent])
                    else:
                        # print(f"Warning: Base agent {base_agent} not found in {dict_name} under prefix {prefix}")
                        pass


def _clone_calendar(sim_config):
    simulation_parameters = sim_config.sim_instance.simulation_parameters

    duplicated_agents_mapping = simulation_parameters["duplicated_agents_mapping"]
    calendar_dict = simulation_parameters["res_calendars"]

    for agent_id, base_agent in duplicated_agents_mapping.items():
        if base_agent in calendar_dict:
            calendar_dict[agent_id] = copy.deepcopy(calendar_dict[base_agent])
        else:
            # print(f"Warning: base agent {base_agent} has no calendar.")
            pass


def _update_activity_mapping(sim_config, agents_to_duplicate):
    """
    Updates the agent activity mapping, (the new agents that are
    duplicated gets the same activity mapping as their "parent")
    """

    simulation_parameters = sim_config.sim_instance.simulation_parameters

    duplicated_agents_mapping = simulation_parameters["duplicated_agents_mapping"]
    agent_activity_mapping = simulation_parameters["agent_activity_mapping"]
    activity_durations_dict = simulation_parameters["activity_durations_dict"]

    for agent_id, base_agent in duplicated_agents_mapping.items():
        # Copy agent activity mapping
        if base_agent in agent_activity_mapping:
            agent_activity_mapping[agent_id] = copy.deepcopy(agent_activity_mapping[base_agent])
        else:
            # print(f"Warning: base agent {base_agent} has no activity mapping.")
            pass

        # Copy activity duration mapping
        if base_agent in activity_durations_dict:
            activity_durations_dict[agent_id] = copy.deepcopy(activity_durations_dict[base_agent])
        else:
            # print(f"Warning: base agent {base_agent} has no activity durations.")
            pass


def _get_agents_to_deactivate_from_count_changes(agent_count_changes):
    """
    Return agent IDs from 'agent_count_changes' where count is 0.

    Returns:
        list: A list of agent ID
    """
    return [agent["id"] for agent in agent_count_changes if agent.get("count", 1) == 0]


def _get_agents_to_duplicate_from_count_changes(agent_count_changes):
    """
    Return (agent_id, count) pairs from 'agent_count_changes' where count > 1.

    Returns:
        list: A list of agent ID
    """
    return [(agent["id"], agent["count"]) for agent in agent_count_changes if agent.get("count", 1) > 1]


# ==================== NON-WORKING ==================
# This could be a good startingpoint for implementing later


# TODO:
# DOESNT WORK: change_agent_role as it currently is doesn't work.
# The role itself can be changed for an agent but the agent doesn't perform any activities afterwards.
# The transition probabilities seem to be the issue but that's not definitive.
# Also be careful if implementing this, this function changes and accesses a lot of dictionaries used by other param-changing functions!
def change_agent_role(roles, agent, new_role, sim_config):
    """
    Changes the role for an agent. Roles are a dictionary consisting of a role-[agents] pair and a calendar for each role.
    This changes the role number for which the agent is listed in.
    Args:
        roles (dict): The roles dict obtained during discovery
        agent (int): The id of the agent to be moved
        new_role (str): the new role. The keys in the roles dict are for example "Role 1", "Role 2" and so on.
        sim_config: The simulation_config instance.
    Returns:
        Modified simulation_config instance.
    """
    # Helper function that gets the role for an agent based on its id
    # def get_role_for_agent(dictionary, thing):
    #     for key, value in dictionary.items():
    #         for (
    #             key1,
    #             value1,
    #         ) in value.items():
    #             if thing in value1:
    #                 return key
    #     return None
    # #To move an agents roles it needs to update at least the following parameters.
    # agent_activity_mapping = sim_config.sim_instance.simulation_parameters["agent_activity_mapping"]
    # activity_durations_dict = sim_config.sim_instance.simulation_parameters["activity_durations_dict"]
    # transition_probabilities = sim_config.sim_instance.simulation_parameters["transition_probabilities"]
    # calendars = sim_config.sim_instance.simulation_parameters["res_calendars"]
    # prev_role = get_role_for_agent(roles, agent)
    # if prev_role is not None:
    #     roles[prev_role]["agents"].remove(agent)

    #     # Get the new role agent list before adding the agent
    #     new_role_agents_before = roles[new_role]["agents"][:]

    #     # Choose a reference agent from the new role to copy parameters for
    #     next_agent = None
    #     if new_role_agents_before:
    #         next_agent = new_role_agents_before[0]

    #     # Add agent to the new role
    #     roles[new_role]["agents"].append(agent)

    #     # Copy activity mapping
    #     if next_agent is not None and next_agent in agent_activity_mapping:
    #         if next_agent in agent_activity_mapping:
    #             agent_activity_mapping[agent] = copy.deepcopy(agent_activity_mapping[next_agent])
    #         else:
    #             print(f"Warning: base agent {next_agent} has no activity mapping.")
    #     # Copy activity durations
    #         if next_agent in activity_durations_dict:
    #             activity_durations_dict[agent] = copy.deepcopy(activity_durations_dict[next_agent])
    #         else:
    #             print(f"Warning: base agent {next_agent} has no activity durations.")
    #     # Copy transition probabilities
    #         if next_agent is not None:
    #             found_probs = False
    #             for key, agent_probs in transition_probabilities.items():
    #                 if next_agent in agent_probs:
    #                     transition_probabilities.setdefault(key, {})[agent] = copy.deepcopy(agent_probs[next_agent])
    #                     found_probs = True
    #             if not found_probs:
    #                 print(f"Warning: base agent {next_agent} has no transition probabilities.")
    #     # Copy calendars
    #         if next_agent in calendars:
    #             calendars[agent] = copy.deepcopy(calendars[next_agent])
    #         else:
    #             print(f"Warning: base agent {next_agent} has no calendars.")
