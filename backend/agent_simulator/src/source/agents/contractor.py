import math
import random
import time
from datetime import datetime

import scipy.stats as st
from mesa import Agent


class ContractorAgent(Agent):
    """
    One contractor agent to assign tasks using the contraction net protocol
    """

    def __init__(self, unique_id, model, activities, transition_probabilities, agent_activity_mapping):
        super().__init__(unique_id, model)
        self.activities = activities
        self.transition_probabilities = transition_probabilities
        self.agent_activity_mapping = agent_activity_mapping
        self.model = model
        self.current_activity_index = None
        self.activity_performed = False

        # #print(
        #     f"Created ContractorAgent in discovery! Id: {unique_id} Model: {self.model} Activities: {self.activities} Transition Probs: {self.transition_probabilities} Activity_mapping: {self.agent_activity_mapping} Activity_preformed: {self.activity_performed}"
        # )

    # def step(self, scheduler, agent_keys, cases):
    #     method = "step"
    #     # Remove contractor agent from agent_keys
    #     agent_keys = agent_keys[1:]

    #     if self.model.central_orchestration:
    #         # Simply sort by availability and use that order
    #         sorted_agent_keys = self.sort_agents_by_availability(agent_keys)
    #         selected_agent = sorted_agent_keys[0]
    #     else:
    #         current_agent = self.case.previous_agent
    #         if current_agent == -1:
    #             # If no previous agent/activity, just sort by availability
    #             sorted_agent_keys = self.sort_agents_by_availability(agent_keys)
    #             selected_agent = sorted_agent_keys[0]
    #         else:
    #             # Get transition probabilities for current state
    #             current_activity = self.case.activities_performed[-1]
    #             next_activity = self.activities[self.new_activity_index]

    #             # Get probabilities for each agent
    #             probabilities = {}
    #             for agent in agent_keys:
    #                 prob = (self.model.agent_transition_probabilities
    #                     .get(current_agent, {})
    #                     .get(current_activity, {})
    #                     .get(agent, {})
    #                     .get(next_activity, 0))
    #                 probabilities[agent] = prob

    #             # Filter agents with non-zero probabilities
    #             valid_agents = [agent for agent in agent_keys if probabilities[agent] > 0]
    #             if valid_agents:
    #                 # Sample one agent based on probabilities
    #                 valid_probs = [probabilities[agent] for agent in valid_agents]
    #                 selected_agent = random.choices(valid_agents, weights=valid_probs, k=1)[0]

    #             else:
    #                 # Fallback to availability sorting if no valid transitions
    #                 sorted_agent_keys = self.sort_agents_by_availability(agent_keys)
    #                 selected_agent = sorted_agent_keys[0]

    #     current_timestamp = self.get_current_timestamp(selected_agent)
    #     getattr(scheduler._agents[selected_agent], method)(
    #             parallel_activity=False,
    #             current_timestamp=current_timestamp,
    #             perform_multitask=False
    #         )

    def step(self, scheduler, agent_keys, cases):
        method = "step"
        agent_keys = agent_keys[1:]  # exclude contractor agent here as we only want to perform resource agent steps

        # 1) sort by specialism
        # bring the agents in an order to first ask the most specialized agents to not waste agent capacity for future cases -> principle of specialization
        def get_key_length(key):
            return len(self.agent_activity_mapping[key])

        # Sort the keys using the custom key function
        if isinstance(agent_keys[0], list):
            sorted_agent_keys = []
            for agent_list in agent_keys:
                sorted_agent_keys.append(sorted(agent_list, key=get_key_length))
        else:
            sorted_agent_keys = sorted(agent_keys, key=get_key_length)
        # print(f"Agents sorted by specialism: {sorted_agent_keys}")

        # # 2) sort by next availability
        sorted_agent_keys = self.sort_agents_by_availability(sorted_agent_keys)

        # if self.model.central_orchestration == False:
        #         # 3) sort by transition probs
        #         current_agent = self.case.previous_agent
        #         if current_agent != -1:
        #             current_activity = self.case.activities_performed[-1]
        #             if current_agent in self.model.agent_transition_probabilities:
        #                 if current_activity in self.model.agent_transition_probabilities[current_agent]:
        #                     current_probabilities = self.model.agent_transition_probabilities[current_agent][current_activity]
        #                 else:
        #                     current_probabilities = self.model.agent_transition_probabilities[current_agent]
        #             sorted_agent_keys = sorted(sorted_agent_keys, key=lambda x: current_probabilities.get(x, 0), reverse=True)

        if self.model.central_orchestration == False:
            # 3) sort by transition probs
            current_agent = self.case.previous_agent
            if current_agent != -1:
                current_activity = self.case.activities_performed[-1]
                next_activity = self.activities[self.new_activity_index]  # Get the next activity

                # Navigate through the nested dictionary structure
                if current_agent in self.model.agent_transition_probabilities:
                    if current_activity in self.model.agent_transition_probabilities[current_agent]:
                        # Create a dictionary to store probabilities for each potential next agent
                        current_probabilities = {}
                        for agent in sorted_agent_keys:
                            # Standard: use the same id as the agent id as lookup
                            lookup_agent_id = agent

                            # If the agent is a clone, use the
                            if (
                                agent not in self.model.agent_transition_probabilities[current_agent][current_activity]
                                and self.model.schedule._agents[agent].is_clone_of
                                in self.model.agent_transition_probabilities[current_agent][current_activity]
                            ):
                                lookup_agent_id = self.model.schedule._agents[agent].is_clone_of

                            # Lookup the base / clone's base probs.
                            if (
                                lookup_agent_id
                                in self.model.agent_transition_probabilities[current_agent][current_activity]
                            ):
                                prob = self.model.agent_transition_probabilities[current_agent][current_activity][
                                    lookup_agent_id
                                ].get(next_activity, 0)
                                current_probabilities[agent] = prob
                            else:
                                current_probabilities[agent] = 0
                        # print(f"current_activity: {current_activity}")
                        # print(f"current_agent: {current_agent}")
                        # print(f"current_probabilities: {self.model.agent_transition_probabilities[current_agent][current_activity]}")
                        # print(f"sorted_agent_keys before: {sorted_agent_keys}")
                        # Filter out agents with zero probability and sort remaining agents
                        sorted_agent_keys_ = [
                            agent for agent in sorted_agent_keys if current_probabilities.get(agent, 0) > 0
                        ]
                        if len(sorted_agent_keys_) > 0:
                            # sorted_agent_keys = sorted_agent_keys_
                            # sorted_agent_keys = sorted(sorted_agent_keys,
                            #                      key=lambda x: current_probabilities.get(x, 0),
                            #                      reverse=True)
                            probabilities = [current_probabilities[agent] for agent in sorted_agent_keys_]
                            sorted_agent_keys = random.choices(
                                sorted_agent_keys_, weights=probabilities, k=len(sorted_agent_keys_)
                            )
                        else:
                            sorted_agent_keys = sorted_agent_keys
                        # print(f"sorted_agent_keys after: {sorted_agent_keys}")
                        end_time = time.time()

        # #print(f"sorted_agent_keys: {sorted_agent_keys}")

        last_possible_agent = False

        if isinstance(sorted_agent_keys[0], list):
            for agent_key in sorted_agent_keys:
                for inner_key in agent_key:
                    if inner_key == agent_key[-1]:
                        last_possible_agent = True
                    if inner_key in scheduler._agents:
                        if self.activity_performed:
                            break
                        else:
                            current_timestamp = self.get_current_timestamp(inner_key, parallel_activity=True)
                            perform_multitask = False
                            getattr(scheduler._agents[inner_key], method)(
                                last_possible_agent,
                                parallel_activity=True,
                                current_timestamp=current_timestamp,
                                perform_multitask=perform_multitask,
                            )
        else:
            for agent_key in sorted_agent_keys:
                if agent_key == sorted_agent_keys[-1]:
                    last_possible_agent = True
                if agent_key in scheduler._agents:
                    if self.activity_performed:
                        break
                    else:
                        current_timestamp = self.get_current_timestamp(agent_key)
                        perform_multitask = False
                        getattr(scheduler._agents[agent_key], method)(
                            last_possible_agent,
                            parallel_activity=False,
                            current_timestamp=current_timestamp,
                            perform_multitask=perform_multitask,
                        )
        self.activity_performed = False

    def sort_agents_by_availability(self, sorted_agent_keys):
        # print(f"agents before sorting: {sorted_agent_keys}")
        # for agent in sorted_agent_keys:
        # #print(f"agent: {agent}, busy until: {self.model.agents_busy_until[agent]}")
        if isinstance(sorted_agent_keys[0], list):
            sorted_agent_keys_new = []
            for agent_list in sorted_agent_keys:
                sorted_agent_keys_new.append(sorted(agent_list, key=lambda x: self.model.agents_busy_until[x]))
        else:
            sorted_agent_keys_new = sorted(sorted_agent_keys, key=lambda x: self.model.agents_busy_until[x])

        # print(f"agents after sorting: {sorted_agent_keys_new}")
        return sorted_agent_keys_new

    def get_current_timestamp(self, agent_id, parallel_activity=False):
        if parallel_activity == False:
            current_timestamp = self.case.current_timestamp
        else:
            current_timestamp = self.case.timestamp_before_and_gateway

        return current_timestamp

    def get_activity_duration(self, agent, activity):

        lookup = agent

        clone_agents = self.model.simulation_parameters["duplicated_agents_mapping"].keys()
        if agent in clone_agents:
            lookup = self.model.simulation_parameters["duplicated_agents_mapping"][agent]

        activity_distribution = self.model.activity_durations_dict[lookup][activity]
        if activity_distribution.type.value == "expon":
            scale = activity_distribution.mean - activity_distribution.min
            if scale < 0.0:
                # print("Warning! Trying to generate EXPON sample with 'mean' < 'min', using 'mean' as scale value.")
                scale = activity_distribution.mean
            activity_duration = st.expon.rvs(loc=activity_distribution.min, scale=scale, size=1)[0]
        elif activity_distribution.type.value == "gamma":
            activity_duration = st.gamma.rvs(
                pow(activity_distribution.mean, 2) / activity_distribution.var,
                loc=0,
                scale=activity_distribution.var / activity_distribution.mean,
                size=1,
            )[0]
        elif activity_distribution.type.value == "norm":
            activity_duration = st.norm.rvs(loc=activity_distribution.mean, scale=activity_distribution.std, size=1)[0]
        elif activity_distribution.type.value == "uniform":
            activity_duration = st.uniform.rvs(
                loc=activity_distribution.min, scale=activity_distribution.max - activity_distribution.min, size=1
            )[0]
        elif activity_distribution.type.value == "lognorm":
            pow_mean = pow(activity_distribution.mean, 2)
            phi = math.sqrt(activity_distribution.var + pow_mean)
            mu = math.log(pow_mean / phi)
            sigma = math.sqrt(math.log(phi**2 / pow_mean))
            activity_duration = st.lognorm.rvs(sigma, loc=0, scale=math.exp(mu), size=1)[0]
        elif activity_distribution.type.value == "fix":
            activity_duration = activity_distribution.mean

        return activity_duration

    # def sample_starting_activity(self,):
    #     """
    #     sample the activity that starts the case based on the frequency of starting activities in the train log
    #     """
    #     # start_activities = self.model.data.groupby('case_id')['activity_name'].first().tolist()
    #     start_time = time.time()
    #     start_activities = (self.model.data.groupby('case_id')
    #                       .apply(lambda x: x.sort_values(['start_timestamp', 'end_timestamp'])
    #                       .iloc[0]['activity_name'])
    #                       .tolist())
    #     if "Start" in start_activities or "start" in start_activities:
    #         sampled_activity = "Start" if "Start" in start_activities else "start"
    #         #print(f"Duration of sample_starting_activity(): {time.time() - start_time:.4f} seconds")
    #         return sampled_activity
    #     # Count occurrences of each entry and create a dictionary
    #     start_count = {}
    #     for entry in start_activities:
    #         if entry in start_count:
    #             start_count[entry] += 1
    #         else:
    #             start_count[entry] = 1
    #     # #print(f"start_count: {start_count}")

    #     for key, value in start_count.items():
    #         start_count[key] = value / len(self.model.data['case_id'].unique())

    #     sampled_activity = random.choices(list(start_count.keys()), weights=start_count.values(), k=1)[0]
    #     #print(f"Duration of sample_starting_activity(): {time.time() - start_time:.4f} seconds")
    #     return sampled_activity

    def sample_starting_activity(self):
        """
        Sample the activity that starts the case based on the frequency of starting activities in the train log
        """

        # Cache the start activities if not already cached
        if not hasattr(self, "_start_activities_dist"):
            # Get first activity for each case more efficiently
            df = self.model.data
            # Sort once and get first activity for each case
            first_activities = (
                df.sort_values(["case_id", "start_timestamp", "end_timestamp"])
                .groupby("case_id")["activity_name"]
                .first()
            )

            # Handle Start/start cases
            if "Start" in first_activities.values or "start" in first_activities.values:
                self._start_activities_dist = ("Start" if "Start" in first_activities.values else "start", None)
            else:
                # Calculate frequencies
                total_cases = len(df["case_id"].unique())
                start_count = first_activities.value_counts() / total_cases
                self._start_activities_dist = (list(start_count.index), list(start_count.values))

        # Use cached distribution
        activities, weights = self._start_activities_dist
        if isinstance(activities, str):  # Handle Start/start case
            sampled_activity = activities
        else:
            sampled_activity = random.choices(activities, weights=weights, k=1)[0]

        return sampled_activity

    def check_for_other_possible_next_activity(self, next_activity):
        possible_other_next_activities = []
        for key, value in self.model.prerequisites.items():
            for i in range(len(value)):
                # if values is a single list, then only ONE of the entries must have been performed already (XOR gateway)
                if not isinstance(value[i], list):
                    if value[i] == next_activity:
                        possible_other_next_activities.append(key)
                # if value contains sublists, then all of the values in the sublist must have been performed (AND gateway)
                else:
                    # if current next_activity contained in prerequisites
                    if any(next_activity in sublist for sublist in value[i]):
                        # if all prerequisites are fulfilled
                        if all(value_ in self.case.activities_performed for value_ in value[i]):
                            possible_other_next_activities.append(key)

        return possible_other_next_activities

    def check_if_all_preceding_activities_performed(self, activity):
        # #print(f"activities_performed: {self.case.activities_performed}")
        # #print(f"prerequisites: {self.model.prerequisites}")
        # print(f"activity: {activity}")
        for key, value in self.model.prerequisites.items():
            if activity == key:
                if all(value_ in self.case.activities_performed for value_ in value):
                    return True
        return False

    def get_potential_agents(self, case):
        """
        check if there already happened activities in the current case
            if no: current activity is usual start activity
            if yes: current activity is the last activity of the current case
        """

        self.case = case
        case_ended = False

        current_timestamp = self.case.current_timestamp
        # self.case.potential_additional_agents = []
        # #print(f"activities_performed: {self.case.activities_performed}")
        # #print(f"get last activity: {self.case.get_last_activity()}")

        if case.get_last_activity() == None:  # if first activity in case
            # print("last_activity = None")
            # sample starting activity
            sampled_start_act = self.sample_starting_activity()
            current_act = sampled_start_act
            self.new_activity_index = self.activities.index(sampled_start_act)
            next_activity = sampled_start_act
            # #print(f"start activity: {next_activity}")
        else:
            # print("else")
            current_act = case.get_last_activity()
            self.current_activity_index = self.activities.index(current_act)

            prefix = self.case.activities_performed

            if self.model.central_orchestration:
                # print("if")
                while tuple(prefix) not in self.transition_probabilities.keys():
                    prefix = prefix[1:]
                    # print("while")
                # Extract activities and probabilities
                # #print(self.transition_probabilities[tuple(prefix)])
                # print(f"trans: {self.transition_probabilities}")
                activity_list = list(self.transition_probabilities[tuple(prefix)].keys())
                probabilities = list(self.transition_probabilities[tuple(prefix)].values())
                # print(f"Activity_list: {activity_list}")
                # print(f"Probabilties: {probabilities}")

                next_activity = random.choices(activity_list, weights=probabilities, k=1)[0]
                # # Sample an activity based on the probabilities
                # while True:
                #     # #print(f"activity_list: {activity_list}")
                #     # #print(f"probabilities: {probabilities}")
                #     next_activity = random.choices(activity_list, weights=probabilities, k=1)[0]
                #     # #print(f"next_activity: {next_activity}")
                #     if len(activity_list) > 1:
                #         if self.check_if_all_preceding_activities_performed(next_activity):
                #             # #print("True")
                #             break
                #         else:
                #             #print(f"Not all preceding activities performed for {next_activity}")
                #     else:
                #         break
                self.new_activity_index = self.activities.index(next_activity)
            else:
                # #print(f"{self.transition_probabilities}")
                while (
                    tuple(prefix) not in self.transition_probabilities.keys()
                    or self.case.previous_agent not in self.transition_probabilities[tuple(prefix)].keys()
                ):
                    # #print(f"prefix: {prefix}")
                    # #print(f"keys: {self.transition_probabilities.keys()}\n")
                    # #print(f"self.case.previous_agent: {self.case.previous_agent}\n")
                    # #print(f"self.transition_probabilities[tuple(prefix)].keys(): {self.transition_probabilities[tuple(prefix)].keys()}\n")

                    prefix = prefix[1:]
                # Extract activities and probabilities
                activity_list = list(self.transition_probabilities[tuple(prefix)][self.case.previous_agent].keys())

                probabilities = list(self.transition_probabilities[tuple(prefix)][self.case.previous_agent].values())

                next_activity = random.choices(activity_list, weights=probabilities, k=1)[0]

                # # Sample an activity based on the probabilities
                # time_0 = time.time()
                # while True:
                #     # #print("get next activity")
                #     # #print(f"transition_probabilities: {self.transition_probabilities}")
                #     # #print(f"prefix: {prefix}")
                #     # #print(f"previous_agent: {self.case.previous_agent}")
                #     # #print(f"activity_list: {activity_list}")
                #     # #print(f"probabilities: {probabilities}")
                #     next_activity = random.choices(activity_list, weights=probabilities, k=1)[0]
                #     if len(activity_list) > 1:
                #         if self.check_if_all_preceding_activities_performed(next_activity):
                #             # #print("True")
                #             break
                #         else:
                #             #print(f"Not all preceding activities performed for {next_activity}")
                #     else:
                #         break
                # time_1 = time.time()
                # #print(f"duration: {time_1 - time_0}")
                self.new_activity_index = self.activities.index(next_activity)

            # #print(f"current_act: {current_act}")
            # #print(f"next_activity: {next_activity}")
            # #print(self.model.prerequisites)

            # check if next activity is zzz_end
            if next_activity == "zzz_end":
                potential_agents = -1  # for handeling when no agents can preform next task
                case_ended = True
                return potential_agents, case_ended  # , None, None

            if self.model.discover_parallel_work:
                # check if next activity is allowed by looking at prerequisites
                activity_allowed = False
                for key, value in self.model.prerequisites.items():
                    if next_activity == key:
                        for i in range(len(value)):
                            # if values is a single list, then only ONE of the entries must have been performed already (XOR gateway)
                            if not isinstance(value[i], list):
                                if value[i] in self.case.activities_performed:
                                    activity_allowed = True
                                    break
                            # if value contains sublists, then all of the values in the sublist must have been performed (AND gateway)
                            else:
                                if all(value_ in self.case.activities_performed for value_ in value[i]):
                                    activity_allowed = True
                                    break
                # if activity is not specified as prerequisite, additionally check if it is a parallel one to the last activity and thus actually can be performed
                if activity_allowed == False:
                    for i in range(len(self.model.parallel_activities)):
                        if next_activity in self.model.parallel_activities[i]:
                            if self.case.activities_performed[-1] in self.model.parallel_activities[i]:
                                activity_allowed = True
            else:
                activity_allowed = True

            # additionally check if new activity was already performed
            number_occurence_of_next_activity = self.case.activities_performed.count(next_activity)
            number_occurence_of_next_activity += 1  # add 1 as it would appear one more time in the next step

            if number_occurence_of_next_activity > self.model.max_activity_count_per_case[next_activity]:
                activity_allowed = False

                # check if there is another possible activity that can be performed
                # go through prerequisites and check for which act the current next_activity is a prerequisite for
                # if it is one, then check if this other activity can be performed
                possible_other_next_activities = self.check_for_other_possible_next_activity(next_activity)
                if len(possible_other_next_activities) > 0:
                    next_activity = random.choice(possible_other_next_activities)
                    self.new_activity_index = self.activities.index(next_activity)
                    # #print(f"Changed next activity to {next_activity}")
                    activity_allowed = True

                    # check if next activity is zzz_end
                    if next_activity == "zzz_end":
                        potential_agents = -1  # for handeling when no agents can preform next task
                        case_ended = True
                        return potential_agents, case_ended
                # to avoid that simulation does not terminate
                else:

                    activity_allowed = True

            if activity_allowed == False:
                # #print(f"case_id: {self.case.case_id}: Next activity {next_activity} not allowed from current activity {current_act} with history {self.case.activities_performed}")
                # TODO: do something when activity is not allowed
                # print("Activity not allowed!!!")
                potential_agents = None
                return potential_agents, case_ended  # , [], []
            else:
                pass
                # #print(f"case_id: {self.case.case_id}: Next activity {next_activity} IS ALLOWED from current activity {current_act} with history {self.case.activities_performed}")

        # check which agents can potentially perform the next task
        potential_agents = [
            key for key, value in self.agent_activity_mapping.items() if any(next_activity == item for item in value)
        ]

        # Filter out deactivated agents
        potential_agents = [agent for agent in potential_agents if agent not in self.model.deactivated_resources]

        # Add 0 and 9999 to the beginning of the list
        potential_agents.insert(0, 9999)

        # Return None if no agents are left
        if not potential_agents:
            return None, case_ended

        return potential_agents, case_ended
