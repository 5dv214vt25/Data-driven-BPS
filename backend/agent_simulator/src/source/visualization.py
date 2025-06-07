import json
import os
import random
from collections import defaultdict

import debug_config
import networkx as nx
from pyvis.network import Network
from source.agent_types.calendar_discovery_parameters import int_week_days

# This entire code was given to us be Elizabeth, a PHD stundent at SAP
# This is not used anymore, it only generates a static HTML file that vizualises the discovery phase
# Some of this code is used in the file generate_discovery_data.py
# See the comments about limitations in said file


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


def get_role_informatation(
    sorted_roles,
    agents,
    agent_for_role,
    agent_transition_probabilities,
    agent_to_resource,
):
    role_information = {}
    for role in sorted_roles:
        role_information[role] = {}
        activities_str = get_all_activities_for_role_as_string(
            agents, role, agent_for_role, agent_transition_probabilities
        )
        role_information[role]["activities"] = activities_str
        resources = []
        for agent, agents_role in agent_for_role.items():
            if agents_role == role:
                resource = agent_to_resource.get(int(agent))
                resources.append(resource)
        role_information[role]["resources"] = "\n".join(resources)
    role_information = dict(sorted(role_information.items()))
    return role_information


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


def generate_legend_html(activity_colors):
    # Create the legend HTML with checkboxes for each activity
    legend_html = """
    <div id="legend" style="position: absolute; top: 10px; right: 10px; background-color: white; padding: 10px; display:none">
        <h3 style="font-size: 16px; margin-top: 0; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px;"><b>Activities</b></h3>
        <div style="margin-bottom: 10px;">
            <button id="select-all-activities" class="legend-button">Select All</button>
            <button id="deselect-all-activities" class="legend-button">Deselect All</button>
        </div>
        <ul style="list-style-type: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto;">
    """

    # Add checkbox for each activity
    for activity, color in activity_colors.items():
        legend_html += f"""
            <li style="margin-bottom: 5px;">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" class="activity-checkbox" data-activity="{activity}" checked style="margin-right: 5px;">
                    <span style="display: inline-block; width: 15px; height: 15px; background-color: {color}; margin-right: 8px; border: 1px solid #ddd;"></span>
                    <span>{activity}</span>
                </label>
            </li>
        """

    legend_html += f"""
        </ul>
        <div style="margin-top: 10px; font-size: 0.8em; color: #666;">
            <p style="margin: 0;">Selected: <span id="selected-activities-count">{len(activity_colors)}</span>/{len(activity_colors)}</p>
        </div>
    </div>

    <style>
        .legend-button {{
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 3px 8px;
            font-size: 0.8em;
            cursor: pointer;
            margin-right: 5px;
        }}
        .legend-button:hover {{
            background-color: #e0e0e0;
        }}
        #legend ul::-webkit-scrollbar {{
            width: 6px;
        }}
        #legend ul::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        #legend ul::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 3px;
        }}
        #legend ul::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
    </style>
    """

    # Add the JavaScript to handle the interactivity
    legend_script = """
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const activityCheckboxes = document.querySelectorAll('.activity-checkbox');
            const selectAllBtn = document.getElementById('select-all-activities');
            const deselectAllBtn = document.getElementById('deselect-all-activities');
            const selectedCountEl = document.getElementById('selected-activities-count');
            const totalActivities = activityCheckboxes.length;

            // Initialize visibility of edges based on checkboxes
            function updateEdgeVisibility() {
                const selectedActivities = Array.from(document.querySelectorAll('.activity-checkbox:checked'))
                    .map(checkbox => checkbox.getAttribute('data-activity'));

                // Update the selected count display
                selectedCountEl.textContent = selectedActivities.length;

                // Filter edges based on selected activities
                if (window.network && window.network.body)  {
                    const edges = window.network.body.data.edges.get();

                    // Update edge visibility in the network
                    edges.forEach(edge => {
                        const edgeObj = window.network.body.data.edges.get(edge.id);
                        if (edgeObj) {
                            const isVisible = selectedActivities.includes(edgeObj.activity);
                            window.network.body.data.edges.update({
                                id: edge.id,
                                hidden: !isVisible
                            });
                        }
                    });
                }
            }

            // Add event listeners to checkboxes
            activityCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', updateEdgeVisibility);
            });

            // Select all button
            selectAllBtn.addEventListener('click', function() {
                activityCheckboxes.forEach(checkbox => {
                    checkbox.checked = true;
                });
                updateEdgeVisibility();
            });

            // Deselect all button
            deselectAllBtn.addEventListener('click', function() {
                activityCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                updateEdgeVisibility();
            });
        });
    </script>
    """

    return legend_html, legend_script


def generate_dropdown_menu_starting_agents(agents, agent_to_resource, transition_probabilities, starting_activity):
    starting_agents = get_starting_agents(transition_probabilities, starting_activity)
    sorted_starting_agents = sorted(starting_agents, key=lambda x: int(x))

    dropdown_html = """
    <div id="dropdown" style="position: absolute; top: 10px; right: 10px; background-color: white; padding: 10px; border-radius: 5px; display: none;">
        <div style="margin-bottom: 10px;">
            <label for="starting-agent-select"><strong>Select Starting Agent:</strong> </label>
            <select id="starting-agent-select" style="padding: 5px; border-radius: 3px; border: 1px solid #ccc;">
                <option value=""> Show All Edges</option>
    """

    for agent in sorted_starting_agents:
        resource_name = agent_to_resource[int(agent)]
        dropdown_html += f'<option value="{agent}">{resource_name} (Agent {agent})</option>\n'

    dropdown_html += """
            </select>
        </div>
    </div>
    """

    dropdown_script = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        var startingAgentSelect = document.getElementById("starting-agent-select");
        var currentView = "activity";
            function updateActivityNetwork() {
            var selectedAgent = startingAgentSelect.value;

            if (!selectedAgent) {
                activityEdges.forEach(function(edge) {
                    network.body.data.edges.update({
                        id: edge.id,
                        hidden: false,
                        label: edge.originalLabel,
                        title: edge.originalTitle,
                        font: {
                            size: 14,
                            color: "black"
                        }
                    });
                });
                network.body.data.nodes.get().forEach(function(node) {
                    network.body.data.nodes.update({id: node.id, hidden: false});
                });
            } else {
                    var agentFlow = window.activityFlowsByAgent[selectedAgent];

                    network.body.data.edges.get().forEach(function(edge) {
                        var sourceActivity = edge.from.replace("activity_", "");
                        var targetActivity = edge.to.replace("activity_", "");

                        var isInFlow = false;
                        for (var i = 0; i < agentFlow.length - 1; i++) {
                            if (agentFlow[i] === sourceActivity && agentFlow[i+1] === targetActivity) {
                                isInFlow = true;
                                break;
                            }
                        }

                        if (!edge.hasOwnProperty('originalLabel')) {
                            edge.originalLabel = edge.label;
                        }

                        if (!edge.hasOwnProperty('originalTitle')) {
                            edge.originalTitle = edge.title;
                        }

                        network.body.data.edges.update({
                            id: edge.id,
                            hidden: !isInFlow,
                            font: {
                                size: isInFlow ? 0 : 14,
                                color: isInFlow ? "transparent" : "black"
                            }

                        });
                    });

                    // Show/hide activity nodes
                    network.body.data.nodes.get().forEach(function(node) {
                        var activity = node.id.replace("activity_", "");
                        var isInFlow = agentFlow.includes(activity);
                        network.body.data.nodes.update({id: node.id, hidden: !isInFlow});
                    });
                    network.redraw();
                }
            }

        startingAgentSelect.addEventListener("change", function() {
            if (currentView === "activity") {
                updateActivityNetwork();
            }
        });

        var toggleNetworkViewButton = document.getElementById("toggle-network-view");
        var toggleAgentViewButton = document.getElementById("toggle-agent-view");

        if (toggleNetworkViewButton) {
            toggleNetworkViewButton.addEventListener("change", function(event) {
                currentView = event.target.checked ? "role" : "activity";
            });
        }

        if (toggleAgentViewButton) {
            toggleAgentViewButton.addEventListener("change", function(event) {
                currentView = event.target.checked ? "agent" : "activity";
                if (currentView === "activity") {
                    updateActivityNetwork();
                } else {
                    // Reset activity network to show all edges and nodes
                    network.body.data.edges.get().forEach(function(edge) {
                        network.body.data.edges.update({
                            id: edge.id,
                            hidden: false,
                            label: edge.originalLabel, // Restore original label
                            title: edge.originalTitle  // Restore original title
                        });
                    });
                    network.body.data.nodes.get().forEach(function(node) {
                        network.body.data.nodes.update({id: node.id, hidden: false});
                    });
                }
            });
        }
    });
    </script>
    """

    return dropdown_html, dropdown_script


def generate_role_info_component_html(role_information):
    role_info_html = """
        <div id="role-info-card" class="role-card" style="display:none">
            <div class="role-card-header">
                <h3><b>Role Information</b></h3>
            </div>
            <div class="role-card-content">
                <div id="role-dropdown" class="select-menu-role">
                        <div class="select-btn-role">
                            <span class="sBtn-text-role">Select a Role</span>
                            <i class="fa fa-chevron-down dropdown-arrow-role">^</i>
                        </div>
                        <div class="options-role">
                            <!-- Options will be dynamically populated here -->
                        </div>
                </div>
                <div class="container-content-role">
                    <div class="stat-row-role">
                        <span class="stat-label-role">Resources:</span>
                        <span id="resources-value" class="stat-value-role">-</span>
                    </div>
                    <div class="stat-row-role">
                        <span class="stat-label-role">Tasks:</span>
                        <div id="activities-container-role" class="activities-container-role">-</div>
                    </div>
                </div>
            </div>
        </div>
        <style>
            .container-content-role {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                grid-template-rows: auto auto;
                grid-column-gap: 15px;
                grid-row-gap: 10px;
            }
            .select-menu-role {
                width: 100%;
                margin: 0 0 20px 0;
                position: relative;
            }
            .select-menu-role .select-btn-role {
                display: flex;
                height: 45px;
                background: #fff;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: 400;
                border-radius: 8px;
                align-items: center;
                cursor: pointer;
                justify-content: space-between;
                box-shadow: 0 0 5px rgba(0,0,0,0.1);
                border: 1px solid #e1e4e8;
            }
            .dropdown-arrow-role {
                font-size: 16px;
                transform: rotate(180deg);
                transition: transform 0.3s ease;
            }
            .select-menu-role .options-role {
                position: absolute;
                width: 100%;
                padding: 10px 0;
                margin-top: 10px;
                border-radius: 8px;
                background: #fff;
                box-shadow: 0 0 10px rgba(0,0,0,0.2);
                display: none;
                z-index: 10;
                max-height: 200px;
                overflow-y: auto;
            }
            .select-menu-role.active .options-role {
                display: block;
            }
            .options-role .option-role {
                display: flex;
                height: 45px;
                cursor: pointer;
                padding: 0 16px;
                border-radius: 0;
                align-items: center;
                background: #fff;
            }
            .options-role .option-role:hover {
                background: #F2F2F2;
            }
            .option-role .option-text-role {
                font-size: 16px;
                color: #333;
            }
            .role-card {
                position: fixed;
                bottom: 10px;
                left: 20px;
                right: 20px;
                width: auto;
                margin: 0;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 1000;
                font-family: Arial, sans-serif;
                transition: height 0.3s ease;
                overflow: hidden;
            }
            .role-card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                background-color: #f0f2f5;
                border-bottom: 1px solid #e1e4e8;
                border-radius: 8px 8px 0 0;
            }
            .role-card-header h3 {
                margin: 0;
                font-size: 16px;
                color: #24292e;
            }
            .role-card-content {
                padding: 16px;
                max-height: 300px;
                overflow-y: auto;
            }
            .stat-row-role {
                display: flex;
                flex-direction: column;
                margin-bottom: 12px;
                padding: 8px;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            .stat-label-role {
                color: #000;
                font-size: 11pt;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .stat-value-role {
                font-size: 13px;
                white-space: pre-line;
                line-height: 1.4;
            }
            .activities-container-role {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .activity-item-role {
                background-color: #e9ecef;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 13px;
            }
        </style>
        """
    role_info_script = (
        """
            <script>
        document.addEventListener("DOMContentLoaded", function() {
            const selectBtn = document.querySelector(".select-btn-role");
            const selectMenu = document.querySelector(".select-menu-role");
            const options = document.querySelector(".options-role");
            const sBtn_text = document.querySelector(".sBtn-text-role");

            // Role information
            const roles = """
        + str(role_information)
        + """;

            // Populate dropdown options with correct role-specific classes
            Object.keys(roles).forEach(roleName => {
                const optionElement = document.createElement("div");
                optionElement.className = "option-role";  // Fixed class name
                optionElement.innerHTML = `<span class="option-text-role">${roleName}</span>`;  // Fixed class name
                optionElement.setAttribute("data-role-name", roleName);
                options.appendChild(optionElement);
            });

            // Toggle dropdown when select button is clicked
            selectBtn.addEventListener("click", function(e) {
                e.preventDefault();
                e.stopPropagation();
                selectMenu.classList.toggle("active");
            });

            // Close dropdown when clicking outside
            document.addEventListener("click", function(e) {
                if (!selectMenu.contains(e.target)) {
                    selectMenu.classList.remove("active");
                }
            });

            // Handle option selection with correct selectors
            const optionsList = document.querySelectorAll(".option-role");  // Fixed selector

            optionsList.forEach(option => {
                option.addEventListener("click", function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const roleName = this.getAttribute("data-role-name");

                    // Update dropdown text with selected role
                    sBtn_text.textContent = roleName;
                    selectMenu.classList.remove("active");

                    // Update role information display
                    updateRoleInfo(roleName);

                    // Dispatch custom event for other components
                    const event = new CustomEvent("roleSelected", {
                        detail: { roleName: roleName }
                    });
                    document.dispatchEvent(event);
                });
            });

            function updateRoleInfo(roleName) {
                if (roles[roleName]) {
                    const roleData = roles[roleName];

                    // Update resources (fixed ID)
                    document.getElementById("resources-value").innerHTML =
                        roleData.resources ? roleData.resources.replace(/\\n/g, "<br>") : "-";

                    // Update activities list (fixed ID)
                    const activitiesContainer = document.getElementById("activities-container-role");
                    activitiesContainer.innerHTML = "";

                    if (roleData.activities) {
                        roleData.activities.split("\\n").forEach(activity => {
                            if (activity.trim()) {
                                const activityElement = document.createElement("div");
                                activityElement.className = "activity-item-role";
                                activityElement.textContent = activity;
                                activitiesContainer.appendChild(activityElement);
                            }
                        });
                    } else {
                        activitiesContainer.textContent = "No tasks assigned";
                    }
                }
            }

            // Function to update role info externally
            window.updateRoleInfo = function(roleName) {
                if (roles[roleName]) {
                    sBtn_text.textContent = roleName;
                    updateRoleInfo(roleName);
                }
            };

            // Initialize with the first available role if present
            const firstRole = Object.keys(roles)[0];
            if (firstRole) {
                sBtn_text.textContent = firstRole;
                updateRoleInfo(firstRole);
            } else {
                console.warn("No roles available");
            }
        });
        </script>
    """
    )
    return role_info_html, role_info_script


def generate_resource_info_component_html(resource_information):
    resource_info_html = """
    <div id="resource-info-card" class="resource-card" style="display:none">
        <div class="resource-card-header">
            <h3><b>Resource Information</b></h3>
        </div>
        <div class="resource-card-content">
            <div id="resource-dropdown" class="select-menu">
                    <div class="select-btn">
                        <span class="sBtn-text">Select a Resource</span>
                        <i class="fa fa-chevron-down dropdown-arrow">^</i>
                    </div>
                    <div class="options">
                        <!-- Options will be dynamically populated here -->
                    </div>
            </div>
            <div class="container-content-resource">
                <div class="stat-row">
                    <span class="stat-label">Calendar:</span>
                    <span id="calendar-value" class="stat-value calendar-format">-</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Tasks:</span>
                    <div id="activities-container" class="activities-container">-</div>
                </div>
                <div class="right-column">
                    <div class="stat-row">
                        <span class="stat-label">Role:</span>
                        <span id="role-value" class="stat-value">-</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Interacting Resources:</span>
                        <span id="interacting-resources-value" class="stat-value calendar-format">-</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <style>
        .select-menu {
            width: 100%;
            margin: 0 0 20px 0;
            position: relative;
        }
        .select-menu .select-btn {
            display: flex;
            height: 45px;
            background: #fff;
            padding: 10px 15px;
            font-size: 16px;
            font-weight: 400;
            border-radius: 8px;
            align-items: center;
            cursor: pointer;
            justify-content: space-between;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
            border: 1px solid #e1e4e8;
        }

        .dropdown-arrow {
            font-size: 16px;
            transform: rotate(180deg);
            transition: transform 0.3s ease;
        }

        .select-menu .options {
            position: absolute;
            width: 100%;
            padding: 10px 0;
            margin-top: 10px;
            border-radius: 8px;
            background: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            display: none;
            z-index: 10;
            max-height: 200px;
            overflow-y: auto;
        }
        .select-menu.active .options {
            display: block;
        }
        .options .option {
            display: flex;
            height: 45px;
            cursor: pointer;
            padding: 0 16px;
            border-radius: 0;
            align-items: center;
            background: #fff;
        }
        .options .option:hover {
            background: #F2F2F2;
        }
        .option i {
            font-size: 20px;
            margin-right: 12px;
        }
        .option .option-text {
            font-size: 16px;
            color: #333;
        }
        .resource-card {
            position: fixed;
            bottom: 10px;
            left: 20px;
            right: 20px;
            width: auto;
            margin: 0;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            font-family: Arial, sans-serif;
            transition: height 0.3s ease;
            overflow: hidden;
        }
        .resource-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background-color: #f0f2f5;
            border-bottom: 1px solid #e1e4e8;
            border-radius: 8px 8px 0 0;
        }
        .resource-card-header h3 {
            margin: 0;
            font-size: 16px;
            color: #24292e;
        }
        .resource-card-content {
            padding: 16px;
            max-height: 300px;
            overflow-y: auto;
        }
        .stat-row {
            display: flex;
            flex-direction: column;
            margin-bottom: 12px;
            padding: 8px;
            border-radius: 4px;
            background-color: #f8f9fa;
        }
        .stat-label {
            color: #000;
            font-size: 11pt;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 13px;
        }
        .calendar-format {
            white-space: pre-line;
            font-size: 13px;
            line-height: 1.4;
        }
        .container-content-resource {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            grid-template-rows: auto auto;
            grid-column-gap: 15px;
            grid-row-gap: 10px;
        }
        .right-column {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .activities-container {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .activity-item {
            background-color: #e9ecef;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 13px;
        }
    </style>
    """
    resource_info_script = (
        """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        // Get dropdown elements
        const selectBtn = document.querySelector(".select-btn");
        const selectMenu = document.querySelector(".select-menu");
        const options = document.querySelector(".options");
        const sBtn_text = document.querySelector(".sBtn-text");

        // Resource information
        const resources = """
        + str(resource_information)
        + """;

        // Populate dropdown options
        Object.keys(resources).forEach(agentName => {
            const optionElement = document.createElement("div");
            optionElement.className = "option";
            optionElement.innerHTML = `<span class="option-text">${agentName}</span>`;
            optionElement.setAttribute("data-agent-name", agentName);
            options.appendChild(optionElement);
        });

        // Toggle dropdown when select button is clicked
        selectBtn.addEventListener("click", function() {
            selectMenu.classList.toggle("active");
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", function(e) {
            if (!selectMenu.contains(e.target)) {
                selectMenu.classList.remove("active");
            }
        });

        // Handle option selection
        const optionsList = document.querySelectorAll(".option");
        optionsList.forEach(option => {
            option.addEventListener("click", function() {
                const agentName = this.getAttribute("data-agent-name");

                // Update dropdown text with selected agent
                sBtn_text.textContent = agentName;
                selectMenu.classList.remove("active");

                // Update agent information display
                updateAgentInfo(agentName);

                // Dispatch custom event for other components to use
                const event = new CustomEvent("resourceSelected", {
                    detail: { agentName: agentName }
                });
                document.dispatchEvent(event);
            });
        });

        // Function to update agent info
        function updateAgentInfo(agentName) {
            if (resources[agentName]) {
                const agentData = resources[agentName];

                // Update calendar and role
                document.getElementById("calendar-value").textContent = agentData.calendar || "-";
                document.getElementById("role-value").textContent = agentData.role || "-";
                document.getElementById("interacting-resources-value").textContent = agentData.interacting_resources || "-";


                // Update activities
                const activitiesContainer = document.getElementById("activities-container");
                activitiesContainer.innerHTML = "";

                if (agentData.activities && Object.keys(agentData.activities).length > 0) {
                    Object.entries(agentData.activities).forEach(([activity, timeInfo]) => {
                        const activityElement = document.createElement("div");
                        activityElement.className = "activity-item";

                        // Split the timeInfo at "Performer:"
                        const parts = timeInfo.split("Performer:");
                        const timeData = parts[0].trim();

                        // Extract performer info and determine color
                        let performerInfo = "";
                        if (parts.length > 1) {
                            const performerText = parts[1].trim();
                            let performerColor = "black";

                            // Determine color based on performer type
                            if (performerText.includes("High")) {
                                performerColor = "green";
                            } else if (performerText.includes("Low")) {
                                performerColor = "red";
                            }

                            performerInfo = `<span style="color: ${performerColor};">${performerText}</span>`;
                        }

                        // Combine everything with performer on a new line
                        activityElement.innerHTML = `<b>${activity}:</b><br>${timeData}<br>${performerInfo}`;
                        activitiesContainer.appendChild(activityElement);
                    });
                } else {
                    activitiesContainer.textContent = "The resource has no tasks";
                }
            }
        }

        // Function to update resource info from external calls
        window.updateResourceInfo = function(agentName) {
            if (resources[agentName]) {
                sBtn_text.textContent = agentName;
                updateAgentInfo(agentName);
            }
        };

        // Initialize with the first agent if available
        const firstAgent = Object.keys(resources)[0];
        if (firstAgent) {
            sBtn_text.textContent = firstAgent;
            updateAgentInfo(firstAgent);
        }
    });
    </script>
    """
    )

    return resource_info_html, resource_info_script


def generate_edge_probability_filter_html():
    edge_probability_filter_html = """
    """

    edge_probability_filter_script = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const edgeCountSelector = document.getElementById('edge-count-selector');

        if (typeof window.currentView === 'undefined') {
            window.currentView = "activity";
        }

        let originalEdgeData = {
            activity: null,
            agent: null,
            role: null
        };

        function getCurrentOriginalEdges() {

            if (!window.network || !window.network.body) {
                console.error("Network not initialized");
                return [];
            }

            if (window.currentView === "activity") {
                if (!originalEdgeData.activity) {
                    originalEdgeData.activity = [...window.network.body.data.edges.get()];
                }
                return originalEdgeData.activity;
            } else if (window.currentView === "agent") {
                if (!originalEdgeData.agent) {
                    originalEdgeData.agent = [...window.network.body.data.edges.get()];
                }
                return originalEdgeData.agent;
            } else if (window.currentView === "role") {
                if (!originalEdgeData.role) {
                    originalEdgeData.role = [...window.network.body.data.edges.get()];
                }
                return originalEdgeData.role;
            }
            return [];
        }

        function getEdgeProbability(edge) {
            if (edge.probability !== undefined) {
                return parseFloat(edge.probability);
            }

            if (edge.label) {
                const probMatch = edge.label.match(/(\d+\.\d+)%/);
                if (probMatch && probMatch[1]) {
                    return parseFloat(probMatch[1]);
                }
            }

            console.warn("Could not extract probability for edge:", edge);
            return 0;
        }

        function filterEdges(topCount) {

            if (!window.network || !window.network.body) {
                console.error("Network not initialized");
                return;
            }

            const originalEdgeSet = getCurrentOriginalEdges();

            if (topCount === 'all') {

                const updateData = originalEdgeSet.map(edge => ({
                    id: edge.id,
                    hidden: false
                }));
                window.network.body.data.edges.update(updateData);
                return;
            }

            topCount = parseInt(topCount);

            const specialEdges = originalEdgeSet.filter(edge => {
                const probValue = getEdgeProbability(edge);
                return probValue === 100;
            });

            const specialEdgeIds = new Set(specialEdges.map(edge => edge.id));

            const edgesBySource = {};
            originalEdgeSet.forEach(edge => {
                if (specialEdgeIds.has(edge.id)) {
                    return;
                }

                if (!edgesBySource[edge.from]) {
                    edgesBySource[edge.from] = [];
                }
                edgesBySource[edge.from].push(edge);
            });

            const edgesToShow = [...specialEdges];

            Object.keys(edgesBySource).forEach(source => {
                const edgesWithProbs = edgesBySource[source].map(edge => {
                    const probValue = getEdgeProbability(edge);
                    return { edge, probValue };
                });

                edgesWithProbs.sort((a, b) => b.probValue - a.probValue);

                let cutoffProbability = null;
                for (let i = 0; i < edgesWithProbs.length; i++) {
                    if (i < topCount || (cutoffProbability !== null && edgesWithProbs[i].probValue === cutoffProbability)) {
                        edgesToShow.push(edgesWithProbs[i].edge);
                        cutoffProbability = edgesWithProbs[i].probValue;
                    } else {
                        break;
                    }
                }
            });

            const edgeIdsToShow = new Set(edgesToShow.map(edge => edge.id));

            const updateData = originalEdgeSet.map(edge => ({
                id: edge.id,
                hidden: !edgeIdsToShow.has(edge.id)
            }));

            window.network.body.data.edges.update(updateData);
        }

        if (edgeCountSelector) {
            edgeCountSelector.addEventListener('change', function() {

                const toggleEdgeButton = document.getElementById("toggle-edges");
                if (toggleEdgeButton) {
                    toggleEdgeButton.checked = false;
                }

                filterEdges(this.value);
            });
        } else {
            console.error("Edge count selector not found");
        }

        function registerViewChangeListeners() {
            const toggleNetworkViewButton = document.getElementById("toggle-network-view");
            const toggleAgentViewButton = document.getElementById("toggle-agent-view");

            function resetDropdown() {
                if (edgeCountSelector) {
                    edgeCountSelector.value = "all";
                }
            }

            if (toggleNetworkViewButton) {
                toggleNetworkViewButton.addEventListener("change", function(event) {
                    if (event.target.checked) {
                        originalEdgeData.role = null;
                        window.currentView = "role";

                        if (edgeCountSelector) {
                            edgeCountSelector.value = "all";
                        }
                    } else {
                        originalEdgeData.activity = null;
                        window.currentView = "activity";
                    }
                    resetDropdown();
                });
            }

            if (toggleAgentViewButton) {
                toggleAgentViewButton.addEventListener("change", function(event) {
                    if (event.target.checked) {
                        originalEdgeData.agent = null;
                        window.currentView = "agent";

                        if (edgeCountSelector) {
                            edgeCountSelector.value = "all";
                        }
                    } else {
                        // Reset edge data for the activity view when switching back
                        originalEdgeData.activity = null;
                        window.currentView = "activity";
                    }
                    resetDropdown();
                });
            }
        }

        window.filterEdges = filterEdges;

        setTimeout(registerViewChangeListeners, 500);
    });
    </script>
    """
    return edge_probability_filter_html, edge_probability_filter_script


def generate_toggle_buttons_html():
    toggle_buttons_html = """
        <div style="position: absolute; top: 10px; left: 10px; background-color: white; padding: 10px;">

            <div id="edge-probability-filter" style="margin-bottom: 20px;">
                <label for="edge-count-selector">Show top edges per node:</label>
                <select id="edge-count-selector">
                    <option value="all">All edges</option>
                    <option value="1">Top 1 edge</option>
                    <option value="2">Top 2 edges</option>
                    <option value="3">Top 3 edges</option>
                </select>
                <div id="tooltip">
                    <span id="tooltipText">Filter to show only the top N most probable edges leaving each node, based on probability percentage.</span>
                    <img src="question-circle.svg" alt="Info"/>
                </div>
            </div>

            <div style="margin-bottom: 10px;">
                <label class="switch">
                    <input type="checkbox" id="toggle-network-view">
                    <span class="slider round"></span>
                </label>
                <span>Switch to Role View</span>
                <div id="tooltip">
                    <span id="tooltipText">This view displays how the different roles interact with each other. The nodes represent the roles. One role can contain multiple resources and the edges represent the activities that the role performs and the probability with which the next role will take over.</span>
                    <img src="question-circle.svg" alt="Info"/>
                </div>
            </div>
            <div>
                <label class="switch">
                    <input type="checkbox" id="toggle-agent-view">
                    <span class="slider round"></span>
                </label>
                <span>Switch to Resource View</span>
                <div id="tooltip">
                    <span id="tooltipText">This view displays how the resources interact with each other. The nodes represent the resources, and the edges represent the activity and the probability with which the next resource will take over.</span>
                    <img src="question-circle.svg" alt="Info"/>
                </div>

            </div>
        <style>
            .card {
                width: 100%;
                height: 100vh;
            }

            img {
                margin-left: 10px;
            }

            #tooltip {
                position: relative;
                display: inline-block;
                cursor: pointer;
            }

            span {
                font-size: 11pt
            }

            #tooltipText {
                position: absolute;
                font-size: 11pt;
                left: 100%;
                top: 50%;
                transform: translateY(-50%);
                background-color: #fff;
                color: #000;
                padding: 10px 15px;
                visibility: hidden;
                opacity: 0;
                width: 600px;
                white-space: normal;
                word-wrap: break-word;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                margin-left: 10px;
                z-index: 10;
            }

            #tooltipText::before{
                content: "";
                position: absolute;
                left: -10px;
                top: 50%;
                transform: translateY(-50%);
            }

            #tooltip:hover #tooltipText{
                visibility: visible;
                opacity: 1;
            }

            .switch {
                position: relative;
                display: inline-block;
                width: 40px;
                height: 20px;
                margin-right: 10px;
                vertical-align: middle;
            }

            .switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }

            .switch + span {
                vertical-align: middle;
                display: inline-block;
            }

            .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                -webkit-transition: .4s;
                transition: .4s;
            }

            .slider:before {
                position: absolute;
                content: "";
                height: 16px;
                width: 16px;
                left: 2px;
                bottom: 2px;
                background-color: white;
                -webkit-transition: .4s;
                transition: .4s;
            }

            input:checked + .slider {
                background-color: #2196F3;
            }

            input:focus + .slider {
                box-shadow: 0 0 1px #2196F3;
            }

            input:checked + .slider:before {
                -webkit-transform: translateX(20px);
                -ms-transform: translateX(20px);
                transform: translateX(20px);
            }

            .slider.round {
                border-radius: 20px;
            }

            .slider.round:before {
                border-radius: 50%;
            }
        </style>
    </div>
    """

    toggle_script = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
    var toggleEdgeButton = document.getElementById("toggle-edges");
    var toggleNetworkViewButton = document.getElementById("toggle-network-view");
    var toggleAgentViewButton = document.getElementById("toggle-agent-view");
    var agentDropdown = document.getElementById('dropdown');
    var legend = document.getElementById('legend');
    var resourceInfoCard = document.getElementById('resource-info-card')
    var roleInfoCard = document.getElementById('role-info-card')

    var currentView = "activity";

    toggleNetworkViewButton.checked = false;
    toggleAgentViewButton.checked = false;
    agentDropdown.style.display = 'block';
    legend.style.display = 'none'

    var agentNetwork = {
        nodes: agentNodes,
        edges: agentEdges
    };

    var roleNetwork = {
        nodes: roleNodes,
        edges: roleEdges
    };

    var activityNetwork = {
        nodes: network.body.data.nodes.get(),
        edges: network.body.data.edges.get()
    };

    // Filter and mark max probability edges for agents
    var maxProbabilityEdges = agentNetwork.edges.filter(function(edge) {
        return edge.isMaxProbability === true;
    });

    // Calculate and mark max probability edges for roles
    var roleTransitions = {};
    roleEdges.forEach(function(edge) {
        var sourceId = edge.from;
        var targetId = edge.to;
        if (!roleTransitions[sourceId]) {
        roleTransitions[sourceId] = [];
        }
        roleTransitions[sourceId].push({
        target: targetId,
        probability: parseFloat(edge.label),
        id: edge.id
        });
    });

    // For each source role, find the target with highest probability
    var maxProbabilityRoleEdges = [];
    for (var sourceId in roleTransitions) {
        if (roleTransitions[sourceId].length > 0) {
        roleTransitions[sourceId].sort(function(a, b) {
            return b.probability - a.probability;
        });
        var maxEdge = roleTransitions[sourceId][0];
        maxProbabilityRoleEdges.push(maxEdge.id);
        }
    }

    // Add isMaxProbability flag to role edges
    roleNetwork.edges.forEach(function(edge) {
        if (maxProbabilityRoleEdges.includes(edge.id)) {
        edge.isMaxProbability = true;
        } else {
        edge.isMaxProbability = false;
        }
    });

    // Calculate and mark max probability edges for activities
    var activityTransitions = {};
    activityEdges.forEach(function(edge) {
        var sourceId = edge.from;
        var targetId = edge.to;
        if (!activityTransitions[sourceId]) {
        activityTransitions[sourceId] = [];
        }
        activityTransitions[sourceId].push({
        target: targetId,
        probability: parseFloat(edge.label),
        id: edge.id
        });
    });

    // For each source activity, find the target with highest probability
    var maxProbabilityActivityEdges = [];
    for (var sourceId in activityTransitions) {
        if (activityTransitions[sourceId].length > 0) {
        activityTransitions[sourceId].sort(function(a, b) {
            return b.probability - a.probability;
        });
        var maxEdge = activityTransitions[sourceId][0];
        maxProbabilityActivityEdges.push(maxEdge.id);
        }
    }

    // Add isMaxProbability flag to activity edges
    activityNetwork.edges.forEach(function(edge) {
        if (maxProbabilityActivityEdges.includes(edge.id)) {
        edge.isMaxProbability = true;
        } else {
        edge.isMaxProbability = false;
        }
    });

    toggleNetworkViewButton.addEventListener("change", function(event) {
        var isChecked = event.target.checked;
        if (isChecked) {
            currentView = "role";
            toggleAgentViewButton.checked = false;
            network.body.data.nodes.clear();
            network.body.data.edges.clear();
            network.body.data.nodes.add(roleNetwork.nodes);
            network.body.data.edges.add(roleNetwork.edges);
            legend.style.display = "none";
            agentDropdown.style.display = "none";
            resourceInfoCard.style.display = "none";
            roleInfoCard.style.display = "block"
            toggleEdgeButton.checked = false;
            toggleEdgeButton.disabled = false;
        } else {
            currentView = "activity";
            network.body.data.nodes.clear();
            network.body.data.edges.clear();
            network.body.data.nodes.add(activityNetwork.nodes);
            network.body.data.edges.add(activityNetwork.edges);
            legend.style.display = "none";
            agentDropdown.style.display = 'block';
            resourceInfoCard.style.display = "none";
            roleInfoCard.style.display = "none"
            toggleEdgeButton.disabled = false;
        }
        network.redraw();
        network.fit();
    });

    toggleAgentViewButton.addEventListener("change", function(event) {
        var isChecked = event.target.checked;
        if (isChecked) {
            currentView = "agent";
            toggleNetworkViewButton.checked = false;
            network.body.data.nodes.clear();
            network.body.data.edges.clear();
            network.body.data.nodes.add(agentNetwork.nodes);
            network.body.data.edges.add(agentNetwork.edges);
            legend.style.display = "block";
            agentDropdown.style.display = 'none';
            resourceInfoCard.style.display = "block";
            roleInfoCard.style.display = "none"
            toggleEdgeButton.checked = false;
            toggleEdgeButton.disabled = false;
        } else {
            currentView = "activity";
            network.body.data.nodes.clear();
            network.body.data.edges.clear();
            network.body.data.nodes.add(activityNetwork.nodes);
            network.body.data.edges.add(activityNetwork.edges);
            legend.style.display = "none";
            agentDropdown.style.display = 'block';
            resourceInfoCard.style.display = "none";
            roleInfoCard.style.display = "none"
            toggleEdgeButton.disabled = false;
        }
        network.redraw();
        network.fit();
    });
});
    </script>

    """
    return toggle_buttons_html, toggle_script


def create_interactive_network(discovered_simulation_parameters, starting_activity, html_filename):

    roles = discovered_simulation_parameters["roles"]
    agent_transition_probabilities = discovered_simulation_parameters["agent_transition_probabilities"]
    agent_to_resource = discovered_simulation_parameters["agent_to_resource"]
    resource_calendars = discovered_simulation_parameters["res_calendars"]
    activity_duration_dict = discovered_simulation_parameters["activity_durations_dict"]

    max_activity_count_per_case = discovered_simulation_parameters["max_activity_count_per_case"]

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

    resource_information = get_resource_information(
        resource_calendars,
        activity_duration_dict,
        agent_for_role,
        agent_to_resource,
        agent_transition_probabilities,
    )

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

    role_information = get_role_informatation(
        sorted_roles,
        list(agent_transition_probabilities.keys()),
        agent_for_role,
        agent_transition_probabilities,
        agent_to_resource,
    )

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

    activity_transitions = defaultdict(lambda: defaultdict(int))

    for agent in agent_transition_probabilities.keys():
        for source_activity, targets in agent_transition_probabilities[agent].items():
            for target_agent, activity_probs in targets.items():
                for target_activity, prob in activity_probs.items():
                    activity_transitions[source_activity][target_activity] += 1

    for source_activity, targets in activity_transitions.items():
        total_transitions = sum(targets.values())

        for target_activity, count in targets.items():
            probability = (count / total_transitions) * 100

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

    # Generate the toggle buttons and legend
    toggle_buttons_html, toggle_script = generate_toggle_buttons_html()
    legend_html, legend_script = generate_legend_html(activity_colors)
    agent_dropdown_html, agent_dropdown_script = generate_dropdown_menu_starting_agents(
        agents, agent_to_resource, agent_transition_probabilities, starting_activity
    )
    resource_info_html, resource_info_script = generate_resource_info_component_html(resource_information)
    role_info_html, role_info_script = generate_role_info_component_html(role_information)
    edge_probability_filter_html, edge_probability_filter_script = generate_edge_probability_filter_html()

    # Pass role network data to JavaScript
    agent_nodes_json = json.dumps(agent_nodes_data)
    agent_edges_json = json.dumps(agent_edges_data)
    role_nodes_json = json.dumps(role_nodes_data)
    role_edges_json = json.dumps(role_edges_data)
    activity_nodes_json = json.dumps(activity_nodes_data)
    activity_edges_json = json.dumps(activity_edges_data)

    activity_flow_json = json.dumps(activity_flow_for_starting_agent)

    activity_flow_init_script = f"""
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            window.activityFlowsByAgent = {activity_flow_json};
        }});
    </script>
    """

    data_script = f"""
    <script>
        var roleNodes = {role_nodes_json};
        var roleEdges = {role_edges_json};
        var activityNodes = {activity_nodes_json};
        var activityEdges = {activity_edges_json};
        var agentNodes = {agent_nodes_json};
        var agentEdges = {agent_edges_json};

        network.body.data.edges.forEach(function(edge) {{
            var matchingEdge = {json.dumps(edges_between_agents)}.find(function(e) {{
                return e[0] === edge.from && e[1] === edge.to && Math.abs(e[4] - edge.probability) < 0.01;
            }});

            if (matchingEdge) {{
                edge.activity = matchingEdge[2];
                edge.transActivity = matchingEdge[3];
            }}
        }});
    </script>
    """

    # Generate the HTML
    html_content = net.generate_html()
    html_content = html_content.replace("</head>", f"{data_script}</head>")
    html_content = html_content.replace(
        "</body>",
        f"{toggle_buttons_html}{toggle_script}{legend_html}{legend_script}{agent_dropdown_html}{agent_dropdown_script}{activity_flow_init_script}{resource_info_html}{resource_info_script}{role_info_html}{role_info_script}{edge_probability_filter_html}{edge_probability_filter_script}</body>",
    )

    output_path = os.path.join(os.getcwd(), "source", f"{html_filename}.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    if debug_config.debug:
        print(f"Wrote HTML discovery file to {html_filename}")

    return html_content
