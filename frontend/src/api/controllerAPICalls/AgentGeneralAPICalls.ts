/**
 * Agent General API Calls
 * 
 * This file contains functions for interacting with the general Agent endpoints.
 * These endpoints handle Agent discovery and simulation processes.
 * 
 * Functions to implement:
 * - startAgentDiscovery: Start Agent discovery using an event log
 * - startAgentSimulation: Start Agent simulation using a scenario
 * - updateAgentParameters: Update agent parameters
 */
import { AgentSimulatorSettings }  from '../../types/AgentSimulatorTypes';
/**
 * Start Agent Discovery
 * 
 * This function starts the agent discovery process using an event log.
 * 
 * @param userId - The user ID of the user performing the discovery
 * @param eventLogId - The event log ID of the event log to use for discovery
 * @param saveScenario - Whether to save the scenario
 * @param name - The name of the scenario
 * 
 * @returns Promise<{ zipBlob: Blob, scenarioId: string }>
 */
export const startAgentDiscovery = async (
  userId: string,
  eventLogId: string,
  saveScenario: boolean = false,
  name?: string,
  agentSimulatorParameterSettings?: AgentSimulatorSettings
) => {
  try {
    let url = `/api/start-agent-discovery?user_id=${userId}&event_log_id=${eventLogId}`;

    if (saveScenario) {
      url += `&save_boolean=true`;
      if (name) {
        url += `&name=${encodeURIComponent(name)}`;
      }
    }

    var transformedSettings = null;

    // Changing the object to use snake case instead of camelCase to make the json correct
    if (agentSimulatorParameterSettings){
      transformedSettings = {
        // eslint-disable-next-line
        extr_delays: agentSimulatorParameterSettings.extraneousDelays,
        // eslint-disable-next-line
        central_orchestration: agentSimulatorParameterSettings.centralOrchestration,
        // eslint-disable-next-line
        determine_automatically: agentSimulatorParameterSettings.determineAutomatically,
      };
    } else {
      transformedSettings = {
        // eslint-disable-next-line
        extr_delays: false,
        // eslint-disable-next-line
        central_orchestration: false,
        // eslint-disable-next-line
        determine_automatically: false
      };
    }

    const agentSimulatorInitialParameters = JSON.stringify(transformedSettings);

    // Convert JSON string to a Blob and append to FormData
    const formData = new FormData();
    const file = new Blob([agentSimulatorInitialParameters], { type: 'application/json' });
    formData.append("parameters", file, "params.json");

    const response = await fetch(url, {
      method: "POST", // Required for sending FormData
      body: formData 
    });

    if (!response.ok) {
      throw new Error('Agent discovery failed');
    }

    // Extract the scenario ID from headers if saved
    const scenarioId = response.headers.get('X-Scenario-ID');

    // Get the ZIP file as a blob
    const zipBlob = await response.blob();

    return { zipBlob, scenarioId };
  } catch (error) {
    console.error('Agent discovery error:', error);
    throw error;
  }
};

/**
 * Start Agent Simulation
 * 
 * This function starts the agent simulation process using a scenario.
 * 
 * @param userId - The user ID of the user performing the simulation
 * @param scenarioId - The scenario ID of the scenario to use for simulation
 * @param saveSimulation - Whether to save the simulation
 * 
 * @returns Promise<Blob>
 */
export const startAgentSimulation = async (
  userId: string,
  scenarioId: string,
  saveSimulation: boolean = false
) => {
  try {
    let url = `/api/start-agent-simulation?user_id=${userId}&scenario_id=${scenarioId}`;

    if (saveSimulation) {
      url += `&save_boolean=true`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Agent simulation failed');
    }

    return await response.blob();
  } catch (error) {
    console.error('Agent simulation error:', error);
    throw error;
  }
};

/**
 * Update Agent Parameters
 * 
 * This function updates the agent parameters using a JSON file.
 * 
 * @param userId - The user ID of the user performing the update
 * @param scenarioId - The scenario ID of the scenario to use for update
 * @param jsonFile - The JSON file to use for update
 * @param name - The name of the scenario
 * 
 * @returns Promise<{ zipBlob: Blob, scenarioId: string }>
 */
export const updateAgentParameters = async (
  userId: string,
  scenarioId: string,
  jsonFile: File,
  name?: string
) => {

  const params = new URLSearchParams();
  params.append('user_id', userId);
  params.append('scenario_id', scenarioId);
  if (name) {
    params.append('name', name);
  }

  const formData = new FormData();
  formData.append('changed_parameters', jsonFile, "params.json");

  const response = await fetch(
    `/api/update-agent-parameters?${params.toString()}`,
    {
      method: 'POST',
      body: formData
    }
  );

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    console.error('Agent parameter update failed:', errorBody || response.statusText);
    throw new Error(errorBody?.message || `HTTP ${response.status}`);
  }

  const newScenarioId = response.headers.get('X-Scenario-ID');
  const zipBlob       = await response.blob();
  return { zipBlob, scenarioId: newScenarioId };
};
