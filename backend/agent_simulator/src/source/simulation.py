import pandas as pd
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import BaseScheduler
from source.agents.contractor import ContractorAgent
from source.agents.resource import ResourceAgent
from source.utils import store_simulated_log

# Old (AS IS IN OFFICIAL REPO)
# def simulate_process(df_train, simulation_parameters, data_dir, num_simulations, num_cases):
#     start_timestamp = simulation_parameters["case_arrival_times"][0]
#     simulation_parameters["start_timestamp"] = start_timestamp
#     simulation_parameters["case_arrival_times"] = simulation_parameters["case_arrival_times"][1:]
#     for i in range(num_simulations):
#         # Create the model using the loaded data
#         business_process_model = BusinessProcessModel(df_train, simulation_parameters)

#         # define list of cases
#         case_id = 0
#         case_ = Case(case_id=case_id, start_timestamp=start_timestamp)  # first case
#         cases = [case_]

#         # Truncates the cases to the number of cases to simulate
#         business_process_model.sampled_case_starting_times = business_process_model.sampled_case_starting_times[
#             :num_cases
#         ]

#         # Run the model for a specified number of steps
#         while business_process_model.sampled_case_starting_times:  # while cases list is not empty
#             business_process_model.step(cases)

#         print(f"number of simulated cases: {len(business_process_model.past_cases)}")

#         # Record steps taken by each agent to a single CSV file
#         simulated_log = pd.DataFrame(business_process_model.simulated_events)
#         # add resource column
#         simulated_log["resource"] = simulated_log["agent"].map(simulation_parameters["agent_to_resource"])
#         # save log to csv
#         store_simulated_log(data_dir, simulated_log, i)


def simulate_process(df_train, simulation_parameters, data_dir, num_simulations, num_cases):
    # try:
    start_timestamp = simulation_parameters["case_arrival_times"][0]
    simulation_parameters["start_timestamp"] = start_timestamp
    simulation_parameters["case_arrival_times"] = simulation_parameters["case_arrival_times"][1:]
    for i in range(num_simulations):
        # Create the model using the loaded data
        business_process_model = BusinessProcessModel(df_train, simulation_parameters)

        # define list of cases
        case_id = 0
        case_ = Case(case_id=case_id, start_timestamp=start_timestamp)  # first case
        cases = [case_]

        # Truncates the cases to the number of cases to simulate
        business_process_model.sampled_case_starting_times = business_process_model.sampled_case_starting_times[
            :num_cases
        ]

        # Run the model for a specified number of steps
        while business_process_model.sampled_case_starting_times:  # while cases list is not empty
            business_process_model.step(cases)

        print(f"number of simulated cases: {len(business_process_model.past_cases)}")

        # Record steps taken by each agent to a single CSV file
        simulated_log = pd.DataFrame(business_process_model.simulated_events)
        # add resource column
        simulated_log["resource"] = simulated_log["agent"].map(simulation_parameters["agent_to_resource"])
        # save log to csv
        store_simulated_log(data_dir, simulated_log, i)

    return 0


# except Exception as e:
#     return f"Simulation error: {e}"


class Case:
    """
    represents a case, for example a patient in a medical surveillance process
    """

    def __init__(
        self,
        case_id,
        start_timestamp=None,
    ) -> None:
        self.case_id = case_id
        self.is_done = False
        self.activities_performed = []
        self.case_start_timestamp = start_timestamp
        self.current_timestamp = start_timestamp
        self.additional_next_activities = []
        self.potential_additional_agents = []
        self.timestamp_before_and_gateway = start_timestamp
        self.previous_agent = -1

    def get_last_activity(self):
        """
        get last activity that happened in the current case
        """
        if len(self.activities_performed) == 0:
            return None
        else:
            return self.activities_performed[-1]

    def add_activity_to_case(self, activity):
        self.activities_performed.append(activity)

    def update_current_timestep(self, duration):
        self.current_timestamp += pd.Timedelta(seconds=duration)


# class BusinessProcessModel(Model):
#    def __init__(self, data, simulation_parameters):
#        self.data = data
#        self.resources = sorted(set(self.data["agent"]))
#        activities = sorted(set(self.data["activity_name"]))
#
#        self.roles = simulation_parameters["roles"]
#        self.agents_busy_until = {key: simulation_parameters["start_timestamp"] for key in self.resources}
#        self.calendars = simulation_parameters["res_calendars"]
#        self.activity_durations_dict = simulation_parameters["activity_durations_dict"]
#        self.sampled_case_starting_times = simulation_parameters["case_arrival_times"]
#        self.past_cases = []
#        self.maximum_case_id = 0
#        self.prerequisites = simulation_parameters["prerequisites"]
#        self.max_activity_count_per_case = simulation_parameters["max_activity_count_per_case"]
#        self.timer = simulation_parameters["timers"]
#        self.activities_without_waiting_time = simulation_parameters["activities_without_waiting_time"]
#        self.agent_transition_probabilities = simulation_parameters["agent_transition_probabilities"]
#        self.central_orchestration = simulation_parameters["central_orchestration"]
#        self.discover_parallel_work = False
#        self.schedule = MyScheduler(
#            self,
#        )
#        self.contractor_agent = ContractorAgent(
#            unique_id=9999,
#            model=self,
#            activities=activities,
#            transition_probabilities=simulation_parameters["transition_probabilities"],
#            agent_activity_mapping=simulation_parameters["agent_activity_mapping"],
#        )
#        self.schedule.add(self.contractor_agent)
#
#        for agent_id in range(len(self.resources)):
#            agent = ResourceAgent(agent_id, self, self.resources[agent_id], self.timer, self.contractor_agent)
#            self.schedule.add(agent)
#
#        # Data collector to track agent activities over time
#        self.datacollector = DataCollector(agent_reporters={"Activity": "current_activity_index"})
#        self.simulated_events = []

#    def step(self, cases):
#        # check if there are still cases planned to arrive in the future
#        if len(self.sampled_case_starting_times) > 1:
#            # if there are still cases happening
#            if cases:
#                last_case = cases[-1]
#                if last_case.current_timestamp >= self.sampled_case_starting_times[0]:
#                    self.maximum_case_id += 1
#                    new_case_id = self.maximum_case_id
#                    new_case = Case(case_id=new_case_id, start_timestamp=self.sampled_case_starting_times[0])
#                    cases.append(new_case)
#                    # remove added case from sampled_case_starting_times list
#                    self.sampled_case_starting_times = self.sampled_case_starting_times[1:]
#            # if no cases are happening
#            else:
#                self.maximum_case_id += 1
#                new_case_id = self.maximum_case_id
#                new_case = Case(case_id=new_case_id, start_timestamp=self.sampled_case_starting_times[0])
#                cases.append(new_case)
#                # remove added case from sampled_case_starting_times list
#                self.sampled_case_starting_times = self.sampled_case_starting_times[1:]
#        # Sort cases by current timestamp
#        cases.sort(key=lambda x: x.current_timestamp)
#        # print(f"cases after sorting: {[case.current_timestamp for case in cases]}")
#        # print("NEW SIMULATION STEP")
#        for case in cases:
#            current_active_agents, case_ended = self.contractor_agent.get_potential_agents(case=case)
#            if case_ended:
#                self.past_cases.append(case)
#                cases.remove(case)
#                if len(self.sampled_case_starting_times) == 1 and len(cases) == 0:
#                    self.sampled_case_starting_times = self.sampled_case_starting_times[1:]
#                continue
#            if current_active_agents is None:
#                continue  # continue with next case
#            else:
#                current_active_agents_sampled = current_active_agents
#                self.schedule.step(cases=cases, current_active_agents=current_active_agents_sampled)


class MyScheduler(BaseScheduler):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

    def step(self, cases, current_active_agents=None):
        """
        Step through the agents, activating each agent in a dynamic subset.
        """
        self.do_each(method="step", agent_keys=current_active_agents, cases=cases)
        self.steps += 1
        self.time += 1

    def get_agent_count(self):
        """
        Returns the current number of active agents in the model.
        """
        return len(self._agents)

    def do_each(self, method, cases, agent_keys=None, shuffle=False):
        agent_keys_ = [agent_keys[0]]
        if agent_keys_ is None:
            agent_keys_ = self.get_agent_keys()
        if shuffle:
            self.model.random.shuffle(agent_keys_)
        for agent_key in agent_keys_:
            if agent_key in self._agents:
                getattr(self._agents[agent_key], method)(self, agent_keys, cases)
                # print(f"Agent {self._agents[agent_key].unique_id} did: {method}")


# Taken from PHD code
class BusinessProcessModel(Model):
    def __init__(self, data, simulation_parameters):
        self.simulation_parameters = simulation_parameters  # For simplicity, and to be able to access this from model

        self.data = data
        self.resources = sorted(set(self.data["agent"]))
        self.deactivated_resources = simulation_parameters["deactivated_resources"]
        self.duplicated_agents = simulation_parameters["duplicated_agents"]

        activities = sorted(set(self.data["activity_name"]))

        self.roles = simulation_parameters["roles"]
        self.agents_busy_until = {key: simulation_parameters["start_timestamp"] for key in self.resources}
        self.calendars = simulation_parameters["res_calendars"]
        self.activity_durations_dict = simulation_parameters["activity_durations_dict"]
        self.sampled_case_starting_times = simulation_parameters["case_arrival_times"]
        self.past_cases = []
        self.maximum_case_id = 0
        self.prerequisites = simulation_parameters["prerequisites"]
        self.max_activity_count_per_case = simulation_parameters["max_activity_count_per_case"]
        self.timer = simulation_parameters["timers"]
        self.activities_without_waiting_time = simulation_parameters["activities_without_waiting_time"]
        self.agent_transition_probabilities = simulation_parameters["agent_transition_probabilities"]
        self.central_orchestration = simulation_parameters["central_orchestration"]
        self.discover_parallel_work = False
        self.schedule = MyScheduler(
            self,
        )
        self.agent_activity_mapping = simulation_parameters["agent_activity_mapping"]
        self.contractor_agent = ContractorAgent(
            unique_id=9999,
            model=self,
            activities=activities,
            transition_probabilities=simulation_parameters["transition_probabilities"],
            agent_activity_mapping=simulation_parameters["agent_activity_mapping"],
        )
        self.schedule.add(self.contractor_agent)

        self.transition_probabilities = simulation_parameters["transition_probabilities_autonomous"]

        self.case_arrival_times = simulation_parameters["case_arrival_times"]

        # These are used for defining duration of an activity
        self.activity_filter = simulation_parameters["activity_filter"]
        self.new_activity_duration = simulation_parameters["new_activity_duration"]

        # TODO: NOTE: Everything below this is a clusterfuck I'm sorry if this is ever refactored or
        # touched again. Majority of this is done to add & remove agents, which was a much greated task
        # than what was thought. Currently it works, however the "cloned" agent is way to coupled with the
        # base agent. Which makes the cloned agent basically not configureble when it comes to trasnition
        # probabilites, activity_mapping, times, etc.. The same could be said when the base agent is updated,
        # then some funcitonality in the cloned agent is changed. This is also highly nestled in the
        # simulation_parameters, ResourceAgent and Contractor agent. If this is further developed in the future
        # I think it is best to entirely rely on the simulation parameters, so basically "cheat" and make up the
        # probabilities on the new agents. This was the first idea that was tested when it came to adding
        # agents, but to no availe.
        # Changes revolving this are located in contractor step() in step 3),

        # Good Luck & Sorry :) - Kev

        # Adds the keys
        keys = self.simulation_parameters["agent_to_resource"].keys()
        for key in keys:
            if key not in self.resources:
                self.resources.append(key)

        # Re do this one with the new agents
        self.agents_busy_until = {key: simulation_parameters["start_timestamp"] for key in self.resources}

        # mapping = self.simulation_parameters["agent_activity_mapping"]
        agent_mapping = simulation_parameters["duplicated_agents_mapping"]
        # print(f"\n=============\n\nself.resources: {self.resources}")
        # print(f"\n=============\n\nagent_activity_mapping: {mapping}")
        # print(f"\n=============\n\nagent_mapping: {agent_mapping}")

        for agent_id in range(len(self.resources)):
            is_clone_of = None

            # Lookup if the agent to create is a clone, is fo specify the clone num
            if agent_id in agent_mapping.keys():
                is_clone_of = agent_mapping[agent_id]
                # print(f"Agent: {agent_id} is clone of {is_clone_of}")

            # Deactivate if specified in the params
            is_deactivated = agent_id in self.deactivated_resources
            agent = ResourceAgent(
                agent_id,
                self,
                self.resources[agent_id],
                self.timer,
                is_deactivated,
                is_clone_of,  # int (parent agents)
                self.contractor_agent,
            )
            # print(f"Created agent: {agent_id}, deactivated: {is_deactivated}")
            self.schedule.add(agent)

        # Data collector to track agent activities over time
        self.datacollector = DataCollector(agent_reporters={"Activity": "current_activity_index"})
        self.simulated_events = []

    def print_model_parameters(self):
        """
        Prints all the important parameters and configurations of the Business Process Model
        """
        print("=== Business Process Model Parameters ===\n")

        print("Resources:", self.resources)
        print("\nRoles:", self.roles)
        print("\nAgent Busy Status:", self.agents_busy_until)
        print("\n=== Resource Calendars ===")
        for resource_id, calendar in self.calendars.items():
            print(f"\nResource {resource_id} Calendar:")
            calendar.print_calendar_info()
        print("\nActivity Durations:", self.activity_durations_dict)
        print("\nAgent Activity Mapping", self.agent_activity_mapping)
        print("\nPrerequisites:", self.prerequisites)
        print("\nMax Activities Per Case:", self.max_activity_count_per_case)
        print("\nTimers:", self.timer)
        print("\nActivities Without Waiting Time:", self.activities_without_waiting_time)
        print("\nAgent Transition Probabilities:", self.agent_transition_probabilities)
        print("\nTransition Probabilities", self.transition_probabilities)
        print("\nCase Arrival Time", self.case_arrival_times)
        print("\nCentral Orchestration:", self.central_orchestration)
        print("\nTotal Number of Agents:", self.schedule.get_agent_count())
        print("\nPlanned Case Start Times:", self.sampled_case_starting_times)
        print("\nCompleted Cases:", len(self.past_cases))

    def step(self, cases):
        # check if there are still cases planned to arrive in the future

        if len(self.sampled_case_starting_times) > 1:
            # if there are still cases happening
            if cases:
                last_case = cases[-1]
                if last_case.current_timestamp >= self.sampled_case_starting_times[0]:
                    self.maximum_case_id += 1
                    new_case_id = self.maximum_case_id
                    new_case = Case(
                        case_id=new_case_id,
                        start_timestamp=self.sampled_case_starting_times[0],
                    )
                    cases.append(new_case)
                    # remove added case from sampled_case_starting_times list
                    self.sampled_case_starting_times = self.sampled_case_starting_times[1:]
            # if no cases are happening
            else:
                self.maximum_case_id += 1
                new_case_id = self.maximum_case_id
                new_case = Case(
                    case_id=new_case_id,
                    start_timestamp=self.sampled_case_starting_times[0],
                )
                cases.append(new_case)
                # remove added case from sampled_case_starting_times list
                self.sampled_case_starting_times = self.sampled_case_starting_times[1:]
        # Sort cases by current timestamp
        cases.sort(key=lambda x: x.current_timestamp)

        for case in cases:
            current_active_agents, case_ended = self.contractor_agent.get_potential_agents(case=case)
            if current_active_agents is None or current_active_agents == -1:  # -1 for when activity  = zzz_end

                if current_active_agents is None:

                    # index = 0

                    # TODO: Outcommented (took other route to print activity, maybe do this in the future)

                    # if self.contractor_agent.current_activity_index is not None:
                    # index = self.contractor_agent.current_activity_index
                    # activity = self.contractor_agent.activities[index]
                    # next_activity = self.contractor_agent.activities[self.contractor_agent.current_activity_index]

                    self.simulated_events.append(
                        {
                            "case_id": self.contractor_agent.case.case_id,
                            "agent": "?",
                            "activity_name": f"Could not finish case: {case.case_id} (No agents to preform activity)",
                            # This does not 100% accurately calculate the activity which was not completed
                            # "activity_name": f"DID NOT COMPLETE ACTIVITY: {activity}",
                            "start_timestamp": case.current_timestamp,
                            "end_timestamp": self.contractor_agent.case.current_timestamp,
                            "TimeStep": self.schedule.steps,
                        }
                    )
                    # TODO:
                case_ended = True

            if case_ended:
                self.past_cases.append(case)
                cases.remove(case)
                if len(self.sampled_case_starting_times) == 1 and len(cases) == 0:
                    self.sampled_case_starting_times = self.sampled_case_starting_times[1:]
                continue  # continue with next case

            else:
                # print("step"*)
                current_active_agents_sampled = current_active_agents
                self.schedule.step(cases=cases, current_active_agents=current_active_agents_sampled)
