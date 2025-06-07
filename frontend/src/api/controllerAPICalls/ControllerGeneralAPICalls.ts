/**
 * Controller Demo API Calls
 * 
 * This file contains functions for interacting with the Demo endpoints.
 * These endpoints are primarily used for testing and demonstration purposes.
 * 
 * Functions to implement:
 * - healthCheck: Check the health of the controller
 * - getTestMessageFromController: Get a test message from the controller
 * - simodDemoRequest: Send a Simod demo request
 * - agentSimulatorDemoRequest: Send an agent simulator demo request
 */

/**
 * Checks the status of the database
 * 
 * @returns Status Message
 */
export const healthCheck = async () => {
  try {
    const response = await fetch('/api/health-check');
    if (!response.ok) {
      throw new Error('Failed to check health');
    }
    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

/**
 * Gets a test message from the controller to check if the api is functioning
 * 
 * @returns Response Message
 */
export const getTestMessageFromController = async () => {
  try {
    const response = await fetch('/api/get-test-message-from-controller');

    if (!response.ok) {
      throw new Error('Failed to get test message');
    }

    return await response.json();
  } catch (error) {
    console.error('Get test message error:', error);
    throw error;
  }
};

/**
 * Demonstration of the simod request call
 * 
 * @returns Response Message
 */
export const simodDemoRequest = async () => {
  try {
    const response = await fetch('/api/simod-demo-request');

    if (!response.ok) {
      throw new Error('Failed to send Simod demo request');
    }

    return await response.json();
  } catch (error) {
    console.error('Simod demo request error:', error);
    throw error;
  }
};

/**
 * Demonstration of the agent request call
 * 
 * @returns Response Message
 */
export const agentSimulatorDemoRequest = async () => {
  try {
    const response = await fetch('/api/agent-simulator-demo-request');

    if (!response.ok) {
      throw new Error('Failed to send agent simulator demo request');
    }

    return await response.json();
  } catch (error) {
    console.error('Agent simulator demo request error:', error);
    throw error;
  }
};
