/**
 * Simod Output Demo
 * 
 * This file contains demonstration functions for the Simod Output API.
 * These functions show how to use the Simod Output API functions in a realistic scenario.
 */

import {
  fetchSimodOutputs,
  fetchSimodOutput,
  uploadSimodOutput,
  updateSimodOutput,
  deleteSimodOutput
} from '../controllerAPICalls/SimodOutputAPICalls';

/**
 * Demo function to list Simod outputs
 * 
 * @param userId - The ID of the user
 * @param scenarioId - Optional scenario ID to filter outputs
 * @returns List of Simod outputs
 */
export const demoListSimodOutputs = async (userId: string, scenarioId?: number) => {
  console.log(`DEMO: Listing Simod outputs for user ${userId}${scenarioId ? ` with scenario ID ${scenarioId}` : ''}`);
  
  try {
    return await fetchSimodOutputs(userId, scenarioId);
  } catch (error) {
    console.error('Error in demoListSimodOutputs:', error);
    throw error;
  }
};

/**
 * Demonstrates retrieving a specific Simod output
 * 
 * @param userId - The ID of the user
 * @param scenarioId - Optional scenario ID to filter outputs
 * 
 * @returns downloadUrl, preview
 */
export const demoGetSimodOutput = async (userId: string, scenarioId: number) => {
  try {
    console.log(`Fetching Simod output for user: ${userId}, scenario ID: ${scenarioId}`);
    const outputBlob = await fetchSimodOutput(scenarioId);

    // Convert blob to text for preview
    const textContent = await outputBlob.text();
    const previewText = textContent.length > 500 ? textContent.substring(0, 500) + '...' : textContent;

    // Create download URL
    const downloadUrl = URL.createObjectURL(outputBlob);

    return {
      downloadUrl,
      preview: previewText
    };
  } catch (error) {
    console.error('Error in demoGetSimodOutput:', error);
    throw error;
  }
};

/**
 * Demonstrates uploading a new Simod output
 * 
 * @param userId - The ID of the user
 * @param scenarioId - Optional scenario ID to filter outputs
 * @param file - The file output to upload
 * 
 * @returns Status message
 */
export const demoUploadSimodOutput = async (userId: string, scenarioId: number, file: File) => {
  try {
    console.log(`Uploading Simod output for user: ${userId}, scenario ID: ${scenarioId}, file: ${file.name}`);
    return await uploadSimodOutput(scenarioId, file);
  } catch (error) {
    console.error('Error in demoUploadSimodOutput:', error);
    throw error;
  }
};

/**
 * Demonstrates updating an existing Simod output
 * 
 * @param userId - The ID of the user
 * @param scenarioId - Optional scenario ID to filter outputs
 * @param file - The file output to update with
 * 
 * @returns Status message
 */
export const demoUpdateSimodOutput = async (userId: string, scenarioId: number, file: File) => {
  try {
    console.log(`Updating Simod output for user: ${userId}, scenario ID: ${scenarioId}, file: ${file.name}`);
    return await updateSimodOutput(scenarioId, file);
  } catch (error) {
    console.error('Error in demoUpdateSimodOutput:', error);
    throw error;
  }
};

/**
 * Demonstrates deleting a specific Simod output
 * 
 * @param userId - The ID of the user
 * @param scenarioId - Optional scenario ID to filter outputs
 * 
 * @returns - Status message
 */
export const demoDeleteSimodOutput = async (userId: string, scenarioId: number) => {
  try {
    console.log(`Deleting Simod output for user: ${userId}, scenario ID: ${scenarioId}`);
    return await deleteSimodOutput(scenarioId);
  } catch (error) {
    console.error('Error in demoDeleteSimodOutput:', error);
    throw error;
  }
};
