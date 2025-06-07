/**
 * Simod General Demo
 * 
 * This file contains demonstration functions for the Simod General API.
 * These functions show how to use the Simod API functions in a realistic scenario.
 */

import {
  startSimodDiscovery,
  startSimodSimulation
} from '../controllerAPICalls/SimodGeneralAPICalls';

/**
 * Demonstrates starting a Simod discovery process
 * 
 * @param userId - The user ID of the user performing the discovery
 * @param eventLogId - The event log ID of the event log to use for discovery
 * @param saveScenario - Whether to save the scenario
 * @param name - The name of the scenario
 * 
 * @returns bpmnUrl, parametersUrl, scenarioId
 */
export const demoStartSimodDiscovery = async (
  userId: string,
  eventLogId: string,
  saveScenario: boolean = false,
  name?: string
) => {
  try {
    console.log(`Starting Simod discovery with event log ID: ${eventLogId}`);
    console.log(`Save scenario: ${saveScenario}, Name: ${name || 'Not specified'}`);

    const result = await startSimodDiscovery(userId, eventLogId, saveScenario, name);

    // Create URLs for the BPMN and parameters files
    const bpmnUrl = result.bpmnBlob ? URL.createObjectURL(result.bpmnBlob) : null;

    // Convert parameters to blob and URL
    const parametersJson = JSON.stringify(result.parameters, null, 2);
    const parametersBlob = new Blob([parametersJson], { type: 'application/json' });
    const parametersUrl = URL.createObjectURL(parametersBlob);

    return {
      bpmnUrl,
      parametersUrl,
      scenarioId: result.scenarioId
    };
  } catch (error) {
    console.error('Error in demoStartSimodDiscovery:', error);
    throw error;
  }
};

/**
 * Demonstrates starting a Simod simulation process
 * 
 * @param userId - The user ID of the user performing the discovery
 * @param scenarioId - The scenario ID use for discovery
 * @param saveSimulation - Whether to save the simualtion
 * 
 * @returns 
 */
export const demoStartSimodSimulation = async (
  userId: string,
  scenarioId: string,
  saveSimulation: boolean = false
) => {
  try {
    console.log(`Starting Simod simulation with scenario ID: ${scenarioId}`);
    console.log(`Save simulation: ${saveSimulation}`);

    const simulationBlob = await startSimodSimulation(userId, scenarioId, saveSimulation);

    // Create a URL for the simulation blob
    const simulationUrl = URL.createObjectURL(simulationBlob);

    // Extract first 5 lines for preview
    const text = await simulationBlob.text();
    const lines = text.split('\n');
    const preview = lines.slice(0, 5).join('\n');

    return {
      simulationUrl,
      preview
    };
  } catch (error) {
    console.error('Error in demoStartSimodSimulation:', error);
    throw error;
  }
};

