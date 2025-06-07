import JSZip from 'jszip';

/**
 * This an old API, Its currently used in different files 4/5 2025.
 * 
 * If possible do not use this and instead use the API from 
 * folder 'controllerAPICalls'.
 */

/**
 * Fetches the list of event logs for a given user.
 *
 * @param {string} userId - The user's ID.
 * @returns {Promise<any>} - A promise resolving to the list of event logs.
 * @throws {Error} - If the request fails.
 */
export const fetchEventLogs = async (userId: string) => {
  const response = await fetch(`storage/list-event-logs?user_id=${userId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch event logs');
  }
  return await response.json();
};

/**
 * Fetches a specific event log file as a Blob.
 *
 * @param {string} userId - The user's ID.
 * @param {number} eventLogId - The ID of the event log to fetch.
 * @returns {Promise<Blob>} - A promise resolving to the event log as a Blob.
 * @throws {Error} - If the request fails.
 */
export const fetchEventLog = async (userId: string, eventLogId: number) => {
  const response = await fetch(`/storage/get-event-log?user_id=${userId}&event_log_id=${eventLogId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch event logs');
  }
  const blob = await response.blob();
  return blob;
};

/**
 * Uploads an event log file.
 *
 * @param {File} file - The file to upload.
 * @param {string} userId - The user's ID.
 * @returns {Promise<{ success: boolean; eventLogId?: string; message?: string }>} - Upload result.
 */
export const uploadEventLog = async (
  file: File,
  userId: string
): Promise<{ success: boolean; eventLogId?: string; message?: string; }> => {
  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('file', file);

  try {
    const response = await fetch('/storage/upload-event-log', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      return { success: true, eventLogId: data.event_log_id };
    } else {
      const errorData = await response.json();
      return { success: false, message: errorData.message };
    }
  } catch (error) {
    console.error('Upload error:', error);
    return { success: false, message: 'An error occurred during upload.' };
  }
};

/**
 * Starts a Simod discovery process and extracts BPMN and JSON files from the returned ZIP blob.
 *
 * @param {string} userId - The user's ID.
 * @param {string} eventLogId - The ID of the event log to process.
 * @returns {Promise<{ bpmnBlob: Blob, parameters: object, scenarioId: string | null }>}
 *          - An object containing the extracted BPMN Blob, parameters JSON object, and scenario ID.
 * @throws {Error} - If the request or file extraction fails.
 */
export const startSimodDiscovery = async (userId: string, eventLogId: string) => {
  const response = await fetch(`/api/start-simod-discovery?user_id=${userId}&event_log_id=${eventLogId}&name="hej"`);

  if (!response.ok) {
    throw new Error('Simod discovery failed');
  }

  const scenarioId = response.headers.get('X-Scenario-ID');

  const zipBlob = await response.blob();

  const zip = new JSZip();
  const unzipped = await zip.loadAsync(zipBlob);

  let bpmnBlob: Blob | null = null;
  let parameters: object | null = null;

  for (const [filename, file] of Object.entries(unzipped.files)) {
    if (filename.endsWith('.bpmn')) {
      bpmnBlob = await file.async('blob');
    } else if (filename.endsWith('.json')) {
      const content = await file.async('string');
      parameters = JSON.parse(content);
    }
  }

  if (!bpmnBlob) {
    throw new Error('BPMN file not found in ZIP');
  }

  if (!parameters) {
    throw new Error('JSON file not found or invalid in ZIP');
  }

  return { bpmnBlob, parameters, scenarioId };
};

/**
 * Starts an agent simulator discovery process.
 *
 * @param {string} userId - The user's ID.
 * @param {string} eventLogId - The ID of the event log.
 * @returns {Promise<Blob>} - A promise resolving to the discovery result as a Blob.
 * @throws {Error} - If the request fails.
 */
export const startAgentDiscovery = async (userId: string, eventLogId: string) => {
  const response = await fetch(`/api/start-agent-discovery?user_id=${userId}&event_log_id=${eventLogId}`);
  if (!response.ok) {
    throw new Error('Agent discovery failed');
  }
  return await response.blob();
};

/**
 * Starts a Simod simulation process.
 *
 * @param {string} userId - The user's ID.
 * @param {string} scenarioId - The scenario ID to simulate.
 * @param {boolean} save - Whether to save the result.
 * @returns {Promise<Blob>} - The simulation output as a Blob.
 * @throws {Error} - If the simulation fails.
 */
export const startSimodSimulation = async (userId: string, scenarioId: string, save: boolean) => {
  const url = `/api/start-simod-simulation?user_id=${userId}&scenarioId=${scenarioId}&save_boolean=${save}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Simod simulation failed');
  }
  return await response.blob();
};

/**
 * Starts an agent simulator simulation process.
 *
 * @param {string} userId - The user's ID.
 * @param {string} eventLogId - The event log ID to simulate.
 * @returns {Promise<Blob>} - Simulation output as a Blob.
 * @throws {Error} - If the simulation fails.
 */
export const startAgentSimulation = async (userId: string, eventLogId: string) => {
  const response = await fetch(`/api/start-agent-simulation?user_id=${userId}&event_log_id=${eventLogId}`);
  if (!response.ok) {
    throw new Error('Agent simulation failed');
  }
  return await response.blob();
};

/**
 * Fetches the list of saved Simod scenarios.
 *
 * @param {string} userId - The user's ID.
 * @returns {Promise<any[]>} - An array of scenarios.
 * @throws {Error} - If the request fails.
 */
export const startGetSimodScenarios = async (userId: string) => {
  const url = `/storage/list-simod-scenarios?user_id=${userId}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get scenario list: ${response.statusText}`);
  }
  if (response.status === 201) {
    console.log("User have no logs");
    return [];
  } else {
    const data = await response.json();
    return data;
  }
};

/**
 * Uploads a Simod scenario consisting of BPMN and parameter files.
 *
 * @param {string} userId - The user's ID.
 * @param {Object} params - Upload data.
 * @param {string} params.eventLogId - Event log ID.
 * @param {string} params.name - Scenario name.
 * @param {File} params.fileBpmn - BPMN file.
 * @param {File} params.paramJson - JSON parameters file.
 * @returns {Promise<{ success: boolean; scenarioId?: string }>} - Upload result.
 */
export const uploadSimodScenario = async (
  userId: string,
  {
    eventLogId,
    name,
    fileBpmn,
    paramJson,
  }: {
    eventLogId: string;
    name: string;
    fileBpmn: File;
    paramJson: File;
  }
): Promise<{ success: boolean; scenarioId?: string; }> => {
  const formData = new FormData();
  formData.append('event_log_id', eventLogId);
  formData.append('name', name);
  formData.append('file_bpmn', fileBpmn);
  formData.append('param_json', paramJson);

  try {
    const response = await fetch(`/storage/upload-simod-scenario?user_id=${userId}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to upload scenario: ${response.statusText}`);
    }

    const data = await response.json();
    if (data.status === 'success') {
      return { success: true, scenarioId: data.scenarioId };
    } else {
      throw new Error('Upload failed: Invalid response status');
    }
  } catch (error) {
    console.error('Upload scenario failed:', error);
    return { success: false };
  }
};

/**
 * Fetches a list of agent simulator scenarios for the given user.
 *
 * @param {string} userId - The user's ID.
 * @returns {Promise<any[]>} - Array of agent scenarios.
 * @throws {Error} - If the request fails.
 */
export const startGetAgentScenarios = async (userId: string) => {
  const url = `/storage/list-agent-scenarios?user_id=${userId}`;
  const response = await fetch(url);

  if (response.status === 404) {
    console.log("User have no logs");
    return [];
  }

  if (!response.ok) {
    throw new Error(`Failed to get scenario list: ${response.statusText}`);
  }

  const data = await response.json();
  return data;
};

/**
 * Downloads the output of a completed Simod simulation scenario.
 *
 * @param {string} scenarioId - The scenario ID.
 * @returns {Promise<Blob | null>} - Simulation output Blob or null if not available.
 * @throws {Error} - If the request fails.
 */
export const startGetSimodOutput = async (scenarioId: string) => {
  const response = await fetch(`/storage/get-simod-output?simod_scenario_id=${scenarioId}`);

  if (response.status === 404) {
    console.log("This scenario doesn't simulate");
    return null;
  }


  if (!response.ok) {
    throw new Error('Simod simulation failed');
  }
  return await response.blob();
};