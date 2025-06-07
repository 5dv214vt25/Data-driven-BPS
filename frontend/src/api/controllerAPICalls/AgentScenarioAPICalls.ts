/**
 * Agent Scenario API Calls
 * 
 * This file contains functions for interacting with the Agent Scenario endpoints.
 * These endpoints handle the management of AgentSimulator scenarios.
 * 
 * Functions implemented:
 * - uploadAgentScenario: Upload a new Agent scenario
 * - getAgentScenario: Get a specific Agent scenario by ID
 * - listAgentScenarios: List all Agent scenarios for a user
 * - updateAgentScenario: Update Agent scenario information
 * - deleteAgentScenario: Delete a specific Agent scenario
 */

import JSZip from 'jszip';

/**
 * Upload Agent Scenario
 * 
 * This function uploads a new Agent scenario.
 * 
 * @param eventLogId - The event log ID of the event log to use for the scenario
 * @param name - The name of the scenario
 * @param modelPkl - The model PKL file
 * @param paramJson - The parameter JSON file
 * @param visualizationJson - The visualization JSON file
 * 
 * @returns Promise<{ success: boolean; scenarioId?: number }>
 */
export const uploadAgentScenario = async (
  eventLogId: string,
  name: string,
  modelPkl: File,
  paramJson: File,
  visualizationJson: File
): Promise<{ success: boolean; scenarioId?: number }> => {
  try {
    const formData = new FormData();
    formData.append('event_log_id', eventLogId);
    formData.append('name', name);
    formData.append('model_pkl', modelPkl);
    formData.append('param_json', paramJson);
    formData.append('visualization_json', visualizationJson);

    const response = await fetch('/storage/upload-agent-scenario', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload Agent scenario');
    }

    const data = await response.json();
    return { success: true, scenarioId: data.scenario_id };
  } catch (error) {
    console.error('Upload Agent scenario error:', error);
    return { success: false };
  }
};

/**
 * Get Agent Scenario
 * 
 * This function gets a specific Agent scenario by ID.
 * 
 * @param scenarioId - The ID of the scenario to get
 * 
 * @returns Promise<{
 *   zipBlob: Blob,
 *   modelBlob: Blob,
 *   parametersBlob: Blob,
 *   visualizationBlob: Blob,
 *   modelFilename: string,
 *   parametersFilename: string,
 *   visualizationFilename: string
 * }>
 */
export const getAgentScenario = async (scenarioId: string) => {
  try {
    // Use query params for GET request
    const url = `/storage/get-agent-scenario?id=${scenarioId}`;
    
    const response = await fetch(url, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Failed to get Agent scenario');
    }

    // Get the ZIP file as a blob
    const zipBlob = await response.blob();

    // Unzip the file
    const zip = new JSZip();
    const unzipped = await zip.loadAsync(zipBlob);

    // Extract PKL and JSON files
    let modelBlob = null;
    let parametersBlob = null;
    let visualizationBlob = null;
    let modelFilename = '';
    let parametersFilename = '';
    let visualizationFilename = '';

    for (const [filename, file] of Object.entries(unzipped.files)) {
      const zipFile = file as JSZip.JSZipObject;
      if (filename.endsWith('.pkl')) {
        modelBlob = await zipFile.async('blob');
        modelFilename = filename;
      } else if (filename.includes('param') && filename.endsWith('.json')) {
        parametersBlob = await zipFile.async('blob');
        parametersFilename = filename;
      } else if (filename.includes('visualization') && filename.endsWith('.json')) {
        visualizationBlob = await zipFile.async('blob');
        visualizationFilename = filename;
      }
    }

    return { 
      zipBlob, 
      modelBlob, 
      parametersBlob,
      visualizationBlob,
      modelFilename,
      parametersFilename,
      visualizationFilename
    };
  } catch (error) {
    console.error('Get Agent scenario error:', error);
    throw error;
  }
};

/**
 * List Agent Scenarios
 * 
 * This function lists all Agent scenarios for a user.
 * 
 * @param userId - The ID of the user to list scenarios for
 * @param eventLogId - The ID of the event log to list scenarios for
 * 
 * @returns Promise<{ scenarios: { id: number, name: string, event_log_id: string }[] }>
 */
export const listAgentScenarios = async (userId: string, eventLogId?: string) => {
  try {
    let url = `/storage/list-agent-scenarios?user_id=${userId}`;
    if (eventLogId) {
      url += `&event_log_id=${eventLogId}`;
    }

    const response = await fetch(url);

    if (!response.ok && response.status !== 404) {
      throw new Error('Failed to list Agent scenarios');
    }

    if (response.status === 404) {
      // No scenarios found
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('List Agent scenarios error:', error);
    throw error;
  }
};

/**
 * Update Agent Scenario
 * 
 * This function updates an existing Agent scenario.
 * 
 * @param scenarioId - The ID of the scenario to update
 * @param name - The name of the scenario
 * @param paramJson - The parameter JSON file
 * 
 * @returns Promise<boolean>
 */
export const updateAgentScenario = async (
  scenarioId: string,
  name?: string,
  paramJson?: File
): Promise<boolean> => {
  try {
    const formData = new FormData();
    formData.append('id', scenarioId);

    if (name) {
      formData.append('name', name);
    }

    if (paramJson) {
      formData.append('param_json', paramJson);
    } else {
      console.error("No JSON provided") 
      return false;
    }

    const response = await fetch('/storage/update-agent-scenario', {
      method: 'PUT',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to update Agent scenario');
    }

    return true;
  } catch (error) {
    console.error('Update Agent scenario error:', error);
    return false;
  }
};

/**
 * Delete Agent Scenario
 * 
 * This function deletes an existing Agent scenario.
 * 
 * @param scenarioId - The ID of the scenario to delete
 * 
 * @returns Promise<boolean>
 */
export const deleteAgentScenario = async (scenarioId: string): Promise<boolean> => {
  try {
    const url = `/storage/delete-agent-scenario?id=${scenarioId}`;

    const response = await fetch(url, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete Agent scenario');
    }

    return true;
  } catch (error) {
    console.error('Delete Agent scenario error:', error);
    return false;
  }
};
