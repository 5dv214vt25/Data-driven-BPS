/**
 * Agent General Demo
 * 
 * This file contains demonstration functions for the Agent General API.
 * These functions show how to use the Agent API functions in a realistic scenario.
 */

import {
  startAgentDiscovery,
  startAgentSimulation
} from '../controllerAPICalls/AgentGeneralAPICalls';
import JSZip from 'jszip';

/**
 * This function starts the agent discovery process using an event log.
 * 
 * @param userId - The user ID of the user performing the discovery
 * @param eventLogId - The event log ID of the event log to use for discovery
 * @param saveScenario - Whether to save the scenario
 * @param name - The name of the scenario
 * 
 * @returns Promise<{ zipBlob: Blob, scenarioId: string }>
 */
export const demoStartAgentDiscovery = async (
  userId: string,
  eventLogId: string,
  saveScenario: boolean = false,
  name?: string
) => {
  try {
    console.log(`Starting Agent discovery with event log ID: ${eventLogId}`);
    console.log(`Save scenario: ${saveScenario}, Name: ${name || 'Not specified'}`);

    const result = await startAgentDiscovery(userId, eventLogId, saveScenario, name);

    // Create URL for the ZIP file
    const zipUrl = URL.createObjectURL(result.zipBlob);

    // Extract the contents of the zip for preview
    const zip = new JSZip();
    const unzipped = await zip.loadAsync(result.zipBlob);
    
    // Create a preview of the files in the zip
    const filesList = Object.keys(unzipped.files).join('\n');

    return {
      zipUrl,
      filesList,
      scenarioId: result.scenarioId
    };
  } catch (error) {
    console.error('Error in demoStartAgentDiscovery:', error);
    throw error;
  }
};

/**
 * Demonstrates starting an Agent simulation process
 * 
 * @param userId - The user ID of the user performing the discovery
 * @param eventLogId - The event log ID of the event log to use for discovery
 * @param saveScenario - Whether to save the scenario
 * 
 * @returns simulationUrl, fileList, preview
 */
export const demoStartAgentSimulation = async (
  userId: string,
  scenarioId: string,
  saveSimulation: boolean = false
) => {
  try {
    console.log(`Starting Agent simulation with scenario ID: ${scenarioId}`);
    console.log(`Save simulation: ${saveSimulation}`);

    const simulationBlob = await startAgentSimulation(userId, scenarioId, saveSimulation);

    // Create a URL for the simulation ZIP blob
    const simulationUrl = URL.createObjectURL(simulationBlob);

    // Extract the contents of the zip for preview
    const zip = new JSZip();
    const unzipped = await zip.loadAsync(simulationBlob);
    
    // Create a preview of the files in the zip
    const filesList = Object.keys(unzipped.files).join('\n');

    // Try to extract and preview a CSV or text file if present
    let preview = "";
    for (const [filename, file] of Object.entries(unzipped.files)) {
      if (filename.endsWith('.csv') || filename.endsWith('.txt')) {
        const content = await (file as JSZip.JSZipObject).async('string');
        const lines = content.split('\n');
        preview = lines.slice(0, 5).join('\n');
        break;
      }
    }

    return {
      simulationUrl,
      filesList,
      preview
    };
  } catch (error) {
    console.error('Error in demoStartAgentSimulation:', error);
    throw error;
  }
}; 