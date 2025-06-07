/**
 * Agent Scenario Demo
 * 
 * This file contains demonstration functions for the Agent Scenario API.
 * These functions show how to use the Agent Scenario API functions in a realistic scenario.
 */

import {
  uploadAgentScenario,
  getAgentScenario,
  listAgentScenarios,
  updateAgentScenario,
  deleteAgentScenario
} from '../controllerAPICalls/AgentScenarioAPICalls';

/**
 * Demonstrates uploading a new Agent scenario
 * 
 * @param eventLogId  - The event log ID of the event log to use for discovery
 * @param name - The name of the scenario
 * @param modelPkl - PKL file containing bpmn model
 * @param paramJson - Json file containing set parameters
 * @param visualizationJson - Visualization Json file
 */
export const demoUploadAgentScenario = async (
  eventLogId: string,
  name: string,
  modelPkl: File,
  paramJson: File,
  visualizationJson: File
) => {
  try {
    console.log(`Uploading Agent scenario for event log ID: ${eventLogId}, name: ${name}`);
    return await uploadAgentScenario(eventLogId, name, modelPkl, paramJson, visualizationJson);
  } catch (error) {
    console.error('Error in demoUploadAgentScenario:', error);
    throw error;
  }
};

/**
 * Demonstrates getting a specific Agent scenario
 * 
 * @param scenarioId - The specified scenario ID
 * 
 * @returns scenarioUrl, fileName, modelUrl, modelFilename, parametersUrl, parametersFilename, 
 *          visualizationUrl, visualizationFilename
 */
export const demoGetAgentScenario = async (scenarioId: string) => {
  try {
    console.log(`Fetching Agent scenario with ID: ${scenarioId}`);
    const result = await getAgentScenario(scenarioId);

    // Create URLs for each blob
    const scenarioUrl = URL.createObjectURL(result.zipBlob);
    const modelUrl = result.modelBlob ? URL.createObjectURL(result.modelBlob) : null;
    const parametersUrl = result.parametersBlob ? URL.createObjectURL(result.parametersBlob) : null;
    const visualizationUrl = result.visualizationBlob ? URL.createObjectURL(result.visualizationBlob) : null;

    return {
      scenarioUrl,
      fileName: `agent_scenario_${scenarioId}.zip`,
      modelUrl,
      modelFilename: result.modelFilename,
      parametersUrl,
      parametersFilename: result.parametersFilename,
      visualizationUrl,
      visualizationFilename: result.visualizationFilename
    };
  } catch (error) {
    console.error('Error in demoGetAgentScenario:', error);
    throw error;
  }
};

/**
 * Demonstrates listing all Agent scenarios for a user
 */
export const demoListAgentScenarios = async (userId: string, eventLogId?: string) => {
  try {
    console.log(`Listing Agent scenarios for user: ${userId}${eventLogId ? `, event log ID: ${eventLogId}` : ''}`);
    return await listAgentScenarios(userId, eventLogId);
  } catch (error) {
    console.error('Error in demoListAgentScenarios:', error);
    throw error;
  }
};

/**
 * Demonstrates updating an Agent scenario
 */
export const demoUpdateAgentScenario = async (
  scenarioId: string,
  name?: string,
  paramJson?: File
) => {
  try {
    console.log(`Updating Agent scenario with ID: ${scenarioId}`);
    const success = await updateAgentScenario(scenarioId, name, paramJson);

    return {
      success,
      scenarioId
    };
  } catch (error) {
    console.error('Error in demoUpdateAgentScenario:', error);
    throw error;
  }
};

/**
 * Demonstrates deleting an Agent scenario
 */
export const demoDeleteAgentScenario = async (scenarioId: string) => {
  try {
    console.log(`Deleting Agent scenario with ID: ${scenarioId}`);
    const success = await deleteAgentScenario(scenarioId);

    return {
      success,
      scenarioId
    };
  } catch (error) {
    console.error('Error in demoDeleteAgentScenario:', error);
    throw error;
  }
}; 