/**
 * Simod Scenario API Calls
 * 
 * This file contains functions for interacting with the Simod Scenario endpoints.
 * These endpoints handle the management of Simod simulation scenarios.
 * 
 * Functions to implement:
 * - uploadSimodScenario: Upload a new Simod scenario
 * - getSimodScenario: Get a specific Simod scenario by ID
 * - listSimodScenarios: List all Simod scenarios for a user
 * - updateSimodScenario: Update Simod scenario information
 * - deleteSimodScenario: Delete a specific Simod scenario
 */

import JSZip from 'jszip';

/**
 * Uploads the simod scenario
 * 
 * @param eventLogId - The eventlog ID
 * @param name - The name of the scenario
 * @param fileBpmn - The bpmn file to upload
 * @param paramJson - The parameters to that bpmn model
 * @returns 
 */
export const uploadSimodScenario = async (
  eventLogId: string,
  name: string,
  fileBpmn: File,
  paramJson: File
): Promise<{ success: boolean; scenarioId?: string }> => {
  try {
    const formData = new FormData();
    formData.append('event_log_id', eventLogId);
    formData.append('name', name);
    formData.append('file_bpmn', fileBpmn);
    formData.append('param_json', paramJson);

    const response = await fetch('/storage/upload-simod-scenario', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload Simod scenario');
    }

    const data = await response.json();
    return { success: true, scenarioId: data.scenario_id };
  } catch (error) {
    console.error('Upload Simod scenario error:', error);
    return { success: false };
  }
};

/**
 * Fetches a specific scenario
 * 
 * @param scenarioId - The scenario ID to fetch
 * 
 * @returns zipBlob, bpmnBlob, parametersBlob, bpmnFilename, parametersFilename
 */
export const getSimodScenario = async (scenarioId: string) => {
  try {
    // Use query params instead of FormData for GET request
    const url = `/storage/get-simod-scenario?scenario_id=${scenarioId}`;

    const response = await fetch(url, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Failed to get Simod scenario');
    }

    // Get the ZIP file as a blob
    const zipBlob = await response.blob();

    // Unzip the file
    const zip = new JSZip();
    const unzipped = await zip.loadAsync(zipBlob);

    // Extract BPMN and JSON files
    let bpmnBlob = null;
    let parametersBlob = null;
    let bpmnFilename = '';
    let parametersFilename = '';

    for (const [filename, file] of Object.entries(unzipped.files)) {
      const zipFile = file as JSZip.JSZipObject;
      if (filename.endsWith('.bpmn') || filename.endsWith('.xml')) {
        bpmnBlob = await zipFile.async('blob');
        bpmnFilename = filename;
      } else if (filename.endsWith('.json')) {
        parametersBlob = await zipFile.async('blob');
        parametersFilename = filename;
      }
    }

    return {
      zipBlob,
      bpmnBlob,
      parametersBlob,
      bpmnFilename,
      parametersFilename
    };
  } catch (error) {
    console.error('Get Simod scenario error:', error);
    throw error;
  }
};

/**
 * Lists all simod scenarios
 * 
 * @param userId - The user ID
 * @param eventLogId - The eventlog ID
 * 
 * @returns Response as a Json
 */
export const listSimodScenarios = async (userId: string, eventLogId?: string) => {
  try {
    let url = `/storage/list-simod-scenarios?user_id=${userId}`;
    if (eventLogId) {
      url += `&event_log_id=${eventLogId}`;
    }

    const response = await fetch(url);

    if (!response.ok && response.status !== 201) {
      throw new Error('Failed to list Simod scenarios');
    }

    if (response.status === 204) {
      // No scenarios found
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('List Simod scenarios error:', error);
    throw error;
  }
};

/**
 * Updates a simod scenario
 * 
 * @param scenarioId - The scenario ID to updtae
 * @param name - The name of the scenario
 * @param paramJson - The parameter file
 * @returns 
 */
export const updateSimodScenario = async (
  scenarioId: string,
  name?: string,
  paramJson?: File
): Promise<boolean> => {
  try {
    const formData = new FormData();
    formData.append('scenario_id', scenarioId);

    if (name) {
      formData.append('name', name);
    }

    if (paramJson) {
      formData.append('param_json', paramJson);
    }

    const response = await fetch('/storage/update-simod-scenario', {
      method: 'PUT',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to update Simod scenario');
    }

    return true;
  } catch (error) {
    console.error('Update Simod scenario error:', error);
    return false;
  }
};

/**
 * Deletes a specific simod scenario
 * 
 * @param scenarioId - The scenario ID to delete
 * 
 * @returns Boolean indicating if the deletion was successfull
 */
export const deleteSimodScenario = async (scenarioId: string): Promise<boolean> => {
  try {
    const formData = new FormData();
    formData.append('scenario_id', scenarioId);

    const response = await fetch('/storage/delete-simod-scenario', {
      method: 'DELETE',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to delete Simod scenario');
    }

    return true;
  } catch (error) {
    console.error('Delete Simod scenario error:', error);
    return false;
  }
};
