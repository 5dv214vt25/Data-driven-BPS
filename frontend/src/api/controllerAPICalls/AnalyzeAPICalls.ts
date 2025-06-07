/**
 * Analyze API Calls
 * 
 * This file contains functions for interacting with the Analyze endpoints.
 * These endpoints handle the analysis operations for event logs and Simod scenario outputs.
 */


/**
 * Analyze event log
 * 
 * @param userId - The user ID
 * @param eventLogId - The eventlog ID
 * 
 * @returns JSON response message
 */
export const analyzeEventLog = async (userId: string, eventLogId: string) => {
  try {
    // Use relative path
    const url = `/analyze/event-log?user_id=${userId}&event_log_id=${eventLogId}`;
    console.log('Calling API URL:', url);

    const response = await fetch(url);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`Failed to analyze event log: ${response.status} ${response.statusText}`);
    }

    // Get response as text first to debug potential issues
    const responseText = await response.text();
    console.log('Raw response text:', responseText.substring(0, 200) + '...');

    // If the response is empty, return an appropriate message
    if (!responseText.trim()) {
      return { status: "error", message: "Empty response received from server" };
    }

    try {
      // Then try to parse as JSON
      return JSON.parse(responseText);
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      console.error('Raw response:', responseText);
      throw new Error(`Failed to parse response as JSON. Raw response: ${responseText.substring(0, 100)}...`);
    }
  } catch (error) {
    console.error('Analyze event log error:', error);
    throw error;
  }
};

/**
 * Analyze event log
 * 
 * @param userId - The user ID
 * @param simodScenarioId - The simod scenario ID
 * 
 * @returns JSON response message
 */
export const analyzeSimodScenarioOutput = async (userId: string, simodScenarioId: number) => {
  try {
    // Use relative path
    const url = `/analyze/simod-scenario-output?user_id=${userId}&simod_scenario_id=${simodScenarioId}`;
    console.log('Calling API URL:', url);

    const response = await fetch(url);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`Failed to analyze simod scenario output: ${response.status} ${response.statusText}`);
    }

    // Get response as text first to debug potential issues
    const responseText = await response.text();
    console.log('Raw response text:', responseText.substring(0, 200) + '...');

    // If the response is empty, return an appropriate message
    if (!responseText.trim()) {
      return { status: "error", message: "Empty response received from server" };
    }

    try {
      // Then try to parse as JSON
      return JSON.parse(responseText);
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      console.error('Raw response:', responseText);
      throw new Error(`Failed to parse response as JSON. Raw response: ${responseText.substring(0, 100)}...`);
    }
  } catch (error) {
    console.error('Analyze simod scenario output error:', error);
    throw error;
  }
};

/**
 * Analyze event log
 * 
 * @param userId - The user ID
 * @param agentScenarioId - The agent scenario ID
 * 
 * @returns JSON response message
 */
export const analyzeAgentScenarioOutput = async (userId: string, agentScenarioId: number) => {
  try {
    // Use relative path
    const url = `/analyze/agent-scenario-output?user_id=${userId}&agent_scenario_id=${agentScenarioId}`;
    console.log('Calling API URL:', url);

    const response = await fetch(url);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`Failed to analyze agent scenario output: ${response.status} ${response.statusText}`);
    }

    // Get response as text first to debug potential issues
    const responseText = await response.text();
    console.log('Raw response text:', responseText.substring(0, 200) + '...');

    // If the response is empty, return an appropriate message
    if (!responseText.trim()) {
      return { status: "error", message: "Empty response received from server" };
    }

    try {
      // Then try to parse as JSON
      return JSON.parse(responseText);
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      console.error('Raw response:', responseText);
      throw new Error(`Failed to parse response as JSON. Raw response: ${responseText.substring(0, 100)}...`);
    }
  } catch (error) {
    console.error('Analyze agent scenario output error:', error);
    throw error;
  }
};
