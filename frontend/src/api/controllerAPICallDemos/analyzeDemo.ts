/**
 * Analyze Demo
 * 
 * This file contains demonstration functions for the Analyze API.
 * These functions show how to use the Analyze API functions in a realistic scenario.
 */

import {
  analyzeEventLog,
  analyzeSimodScenarioOutput
} from '../controllerAPICalls/AnalyzeAPICalls';

/**
 * Demonstrates event log analysis
 */
export const demoAnalyzeEventLog = async (userId: string, eventLogId: string) => {
  try {
    console.log(`Running event log analysis for user: ${userId}, event log: ${eventLogId}`);
    return await analyzeEventLog(userId, eventLogId);
  } catch (error) {
    console.error('Error in demoAnalyzeEventLog:', error);
    throw error;
  }
};

/**
 * Demonstrates simod scenario output analysis
 */
export const demoAnalyzeSimodScenarioOutput = async (userId: string, simodScenarioId: number) => {
  try {
    console.log(`Running simod scenario output analysis for user: ${userId}, simod scenario: ${simodScenarioId}`);
    return await analyzeSimodScenarioOutput(userId, simodScenarioId);
  } catch (error) {
    console.error('Error in demoAnalyzeSimodScenarioOutput:', error);
    throw error;
  }
}; 