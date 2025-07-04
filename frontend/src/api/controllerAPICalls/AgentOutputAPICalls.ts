/**
 * Agent Output API Calls
 * 
 * This file contains functions for interacting with the Agent Output endpoints.
 * These endpoints handle the management of output files generated by agent simulations.
 * 
 * Functions to implement:
 * - uploadAgentOutput: Upload agent simulation output
 * - fetchAgentOutput: Get a agent output by ID
 * - listAgentOutputs: List all agent outputs for a user and optional scenario ID
 * - updateAgentOutput: Update agent output information
 * - deleteAgentOutput: Delete a agent output by ID
 */

/**
 * Upload Agent Output
 * 
 * This function uploads a new Agent output.
 * 
 * @param scenarioId - The ID of the scenario
 * @param file - The file to upload
 * 
 * @returns Promise<boolean>
 */
export const uploadAgentOutput = async (scenarioId: number, file: File): Promise<boolean> => {
  console.log(`API: Uploading Agent output for scenario ID ${scenarioId}`);

  const formData = new FormData();
  formData.append('agent_scenario_id', scenarioId.toString());
  formData.append('file', file);

  const response = await fetch('/storage/upload-agent-output', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to upload Agent output');
  }

  const data = await response.json();
  return data.status === 'success';
};

/**
 * Fetch Agent Output
 * 
 * This function fetches a specific Agent output by ID.
 * 
 * @param scenarioId - The ID of the scenario
 * 
 * @returns Promise<Blob>
 */
export const fetchAgentOutput = async (scenarioId: number): Promise<Blob> => {
  console.log(`API: Fetching Agent output for scenario ID ${scenarioId}`);

  let url = `/storage/get-agent-output?agent_scenario_id=${scenarioId}`;

  // url.searchParams.append('Agent_scenario_id', scenarioId.toString());

  const response = await fetch(url.toString());

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to fetch Agent output');
  }

  return response.blob();
};


/**
 * Fetch all Agent outputs for a user, optionally filtered by scenario ID
 * 
 * @param userId - The ID of the user
 * @param eventLogId - Optional ID to filter outputs (actually used as scenario_id)
 * @returns List of Agent outputs
 */
export const fetchAgentOutputs = async (userId: string, eventLogId?: number) => {
  console.log(`API: Fetching Agent outputs for user ${userId}${eventLogId ? ` with scenario ID ${eventLogId}` : ''}`);

  const url = new URL('/storage/list-agent-outputs', window.location.origin);
  url.searchParams.append('user_id', userId);
  if (eventLogId) {
    url.searchParams.append('scenario_id', eventLogId.toString());
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    let errorMessage = 'Failed to fetch Agent outputs';
    try {
      const errorData = await response.json();
      errorMessage = errorData.message || errorMessage;
    } catch {
      // Ignore JSON parse error
    }

    const error = new Error(errorMessage) as Error & { status?: number };
    error.status = response.status;
    throw error;
  }

  return response.json();
};

/**
 * List Agent Outputs
 * 
 * This function lists all Agent outputs for a user and optional scenario ID.
 * 
 * @param userId - The ID of the user 
 * @param scenarioId - The ID of the scenario (optional)
 * 
 * @returns Promise<List<AgentOutput>>
 */
export const listAgentOutputs = async (userId: string, scenarioId?: number) => {
  console.log(`API: Listing Agent outputs for user ${userId}${scenarioId ? ` with scenario ID ${scenarioId}` : ''}`);

  let url = `/storage/list-agent-outputs?user_id=${userId}`;

  if (scenarioId) {
    url += `&agent_scenario_id=${scenarioId}`;
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to list Agent outputs');
  }

  const data = await response.json();
  if (data.status === 'error') {
    throw new Error(data.message || 'Failed to list Agent outputs');
  }

  return data;
};

/**
 * Update Agent Output
 * 
 * This function updates an existing Agent output.
 * 
 * @param scenarioId - The ID of the scenario
 * @param file - The file to update
 * 
 * @returns Success status (boolean)
 */
export const updateAgentOutput = async (scenarioId: number, file: File): Promise<boolean> => {
  console.log(`API: Updating Agent output for scenario ID ${scenarioId}`);

  const url = new URL('/storage/update-agent-output', window.location.origin);
  url.searchParams.append('agent_scenario_id', scenarioId.toString());

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(url.toString(), {
    method: 'PUT',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to update Agent output');
  }

  const data = await response.json();
  return data.status === 'success';
};

/**
 * Delete Agent Output
 * 
 * This function deletes an existing Agent output.
 * 
 * @param scenarioId - The ID of the scenario
 * 
 * @returns Success status (boolean)
 */
export const deleteAgentOutput = async (scenarioId: number): Promise<boolean> => {
  console.log(`API: Deleting Agent output for scenario ID ${scenarioId}`);

  const url = new URL('/storage/delete-agent-output', window.location.origin);
  url.searchParams.append('agent_scenario_id', scenarioId.toString());

  const response = await fetch(url.toString(), {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to delete Agent output');
  }

  const data = await response.json();
  return data.status === 'success';
};
