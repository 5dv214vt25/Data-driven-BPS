/**
 * Controller General Demo
 * 
 * This file contains demonstration functions for the Controller General API.
 * These functions show how to use the Controller API functions in a realistic scenario.
 */

import {
  healthCheck,
  getTestMessageFromController,
  simodDemoRequest,
  agentSimulatorDemoRequest
} from '../controllerAPICalls/ControllerGeneralAPICalls';

/**
 * Demonstrates checking the health of the controller
 */
export const demoHealthCheck = async () => {
  try {
    console.log('Checking controller health...');
    return await healthCheck();
  } catch (error) {
    console.error('Error in demoHealthCheck:', error);
    throw error;
  }
};

/**
 * Demonstrates getting a test message from the controller
 */
export const demoGetTestMessage = async () => {
  try {
    console.log('Getting test message from controller...');
    return await getTestMessageFromController();
  } catch (error) {
    console.error('Error in demoGetTestMessage:', error);
    throw error;
  }
};

/**
 * Demonstrates sending a Simod demo request
 */
export const demoSimodRequest = async () => {
  try {
    console.log('Sending Simod demo request...');
    return await simodDemoRequest();
  } catch (error) {
    console.error('Error in demoSimodRequest:', error);
    throw error;
  }
};

/**
 * Demonstrates sending an agent simulator demo request
 */
export const demoAgentSimulatorRequest = async () => {
  try {
    console.log('Sending agent simulator demo request...');
    return await agentSimulatorDemoRequest();
  } catch (error) {
    console.error('Error in demoAgentSimulatorRequest:', error);
    throw error;
  }
};
