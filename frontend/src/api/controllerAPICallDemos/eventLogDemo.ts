/**
 * Event Log Demo
 * 
 * This file contains demonstration functions for the Event Log API.
 * These functions show how to use the Event Log API functions in a realistic scenario.
 */

import {
  fetchEventLogs,
  fetchEventLog,
  uploadEventLog,
  deleteEventLog,
  deleteAllEventLogs
} from '../controllerAPICalls/EventLogAPICalls';

/**
 * Demonstrates listing all event logs for a user
 * 
 * @param userId - The user that has all saved eventlogs
 * 
 * @returns The blob containing a list of all eventlogs
 */
export const demoListEventLogs = async (userId: string) => {
  try {
    console.log(`Fetching all event logs for user: ${userId}...`);
    // Directly return the raw API response without wrapping it
    return await fetchEventLogs(userId);
  } catch (error) {
    console.error('Error in demoListEventLogs:', error);
    throw error;
  }
};

/**
 * Demonstrates retrieving a specific event log
 * 
 * @param userId - The user that has has the eventlog
 * @param eventLogId - The ID of the eventlog
 * 
 * @returns downloadUrl, preview
 */
export const demoGetEventLog = async (userId: string, eventLogId: string) => {
  try {
    console.log(`Fetching event log with ID: ${eventLogId} for user: ${userId}`);
    const eventLogBlob = await fetchEventLog(userId, Number(eventLogId));
    console.log('Event log retrieved successfully');

    // Create a temporary URL for the blob - needed for download
    const blobUrl = URL.createObjectURL(eventLogBlob);

    // Convert the blob to text
    const textContent = await eventLogBlob.text();

    // Get first 5 lines for preview
    const lines = textContent.split('\n');
    const previewLines = lines.slice(0, 5).join('\n');

    return {
      downloadUrl: blobUrl,
      preview: previewLines
    };
  } catch (error) {
    console.error('Error in demoGetEventLog:', error);
    throw error;
  }
};

/**
 * Demonstrates uploading a new event log
 * 
 * @param file - The csv file to upload
 * @param userId - The user to save it to
 */
export const demoUploadEventLog = async (file: File, userId: string) => {
  try {
    console.log(`Uploading event log for user ${userId}: ${file.name} (${file.size} bytes)`);
    // Directly return the raw API response without wrapping it
    return await uploadEventLog(file, userId);
  } catch (error) {
    console.error('Error in demoUploadEventLog:', error);
    throw error;
  }
};

/**
 * Demonstrates deleting a specific event log
 * 
 * @param userId - The user id to search the eventlog in
 * @param eventLogId - The eventlog to delete
 */
export const demoDeleteEventLog = async (userId: string, eventLogId: string) => {
  try {
    console.log(`Deleting event log with ID: ${eventLogId} for user: ${userId}`);
    // Return raw result
    return await deleteEventLog(userId, eventLogId);
  } catch (error) {
    console.error('Error in demoDeleteEventLog:', error);
    throw error;
  }
};

/**
 * Demonstrates deleting all event logs for a user
 * 
 * @param userId - The user to delete all eventlogs from
 */
export const demoDeleteAllEventLogs = async (userId: string) => {
  try {
    console.log(`Deleting all event logs for user: ${userId}`);
    // Return raw result
    return await deleteAllEventLogs(userId);
  } catch (error) {
    console.error('Error in demoDeleteAllEventLogs:', error);
    throw error;
  }
};
