/**
 * Simod Scenario Demo
 * 
 * This file contains demonstration functions for the Simod Scenario API.
 * These functions show how to use the Simod Scenario API functions in a realistic scenario.
 */

import {
  uploadSimodScenario,
  getSimodScenario,
  listSimodScenarios,
  updateSimodScenario,
  deleteSimodScenario
} from '../controllerAPICalls/SimodScenarioAPICalls';

/**
 * Demonstrates uploading a new Simod scenario
 * 
 * @param eventLogId - The eventlog ID
 * @param name - The name of the scneraio
 * @param fileBpmn - The bpmn file
 * @param paramJson - The parameters to that bpmn modle
 * 
 * @returns Status message
 */
export const demoUploadSimodScenario = async (
  eventLogId: string,
  name: string,
  fileBpmn: File,
  paramJson: File
) => {
  try {
    console.log(`Uploading Simod scenario for event log ID: ${eventLogId}, name: ${name}`);
    return await uploadSimodScenario(eventLogId, name, fileBpmn, paramJson);
  } catch (error) {
    console.error('Error in demoUploadSimodScenario:', error);
    throw error;
  }
};

/**
 * Demonstrates getting a specific Simod scenario
 * 
 * @param scenarioId - The scenario ID to fetch
 * 
 * @returns scenarioUrl, fileName, bpmnUrl, bpmnFilename,
      parametersUrl, parametersFilename
 */
export const demoGetSimodScenario = async (scenarioId: string) => {
  try {
    console.log(`Fetching Simod scenario with ID: ${scenarioId}`);
    const result = await getSimodScenario(scenarioId);

    // Create URLs for each blob
    const scenarioUrl = URL.createObjectURL(result.zipBlob);
    const bpmnUrl = result.bpmnBlob ? URL.createObjectURL(result.bpmnBlob) : null;
    const parametersUrl = result.parametersBlob ? URL.createObjectURL(result.parametersBlob) : null;

    return {
      scenarioUrl,
      fileName: `scenario_${scenarioId}.zip`,
      bpmnUrl,
      bpmnFilename: result.bpmnFilename,
      parametersUrl,
      parametersFilename: result.parametersFilename
    };
  } catch (error) {
    console.error('Error in demoGetSimodScenario:', error);
    throw error;
  }
};

/**
 * Demonstrates listing all Simod scenarios for a user
 * 
 * @param userId - The user ID 
 * @param eventLogId - The eventlog ID to fetch
 * 
 * @returns Status Message
 */
export const demoListSimodScenarios = async (userId: string, eventLogId?: string) => {
  try {
    console.log(`Listing Simod scenarios for user: ${userId}${eventLogId ? `, event log ID: ${eventLogId}` : ''}`);
    return await listSimodScenarios(userId, eventLogId);
  } catch (error) {
    console.error('Error in demoListSimodScenarios:', error);
    throw error;
  }
};

/**
 * Demonstrates updating a Simod scenario
 * 
 * @param scenarioId - The scenario ID to update 
 * @param name - The name of the scenario
 * @param paramJson - The parameters of said scenario
 * 
 * @returns Status message and the updated ID 
 */
export const demoUpdateSimodScenario = async (
  scenarioId: string,
  name?: string,
  paramJson?: File
) => {
  try {
    console.log(`Updating Simod scenario with ID: ${scenarioId}`);
    const success = await updateSimodScenario(scenarioId, name, paramJson);

    return {
      success,
      scenarioId
    };
  } catch (error) {
    console.error('Error in demoUpdateSimodScenario:', error);
    throw error;
  }
};

/**
 * Demonstrates deleting a Simod scenario
 * 
 * @param scenarioId - The scenario ID to delete
 * 
 * @returns Status message and the removed scenario ID?
 */
export const demoDeleteSimodScenario = async (scenarioId: string) => {
  try {
    console.log(`Deleting Simod scenario with ID: ${scenarioId}`);
    const success = await deleteSimodScenario(scenarioId);

    return {
      success,
      scenarioId
    };
  } catch (error) {
    console.error('Error in demoDeleteSimodScenario:', error);
    throw error;
  }
};
