/**
 * Event Log API Calls
 * 
 * This file contains functions for interacting with the Event Log endpoints.
 * These endpoints handle the upload, retrieval, listing, and deletion of event log files.
 * 
 * Functions included:
 * - fetchEventLogs: List all event logs for a user
 * - fetchEventLog: Get a specific event log by ID
 * - uploadEventLog: Upload a new event log
 * - deleteEventLog: Delete a specific event log
 * - deleteAllEventLogs: Delete all event logs for a user
 */

/**
 * Fetches all eventlogs belonging to a user id.
 * 
 * @param userId - The user ID
 * 
 * @returns Response in a json
 */
export const fetchEventLogs = async (userId: string) => {
  const response = await fetch(`/storage/list-event-logs?user_id=${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch event logs');
  }
  return await response.json();
};

/**
 * Fetches a specific eventlog from a user
 * 
 * @param userId - The user ID
 * @param eventLogId - The eventlog ID to fetch
 * 
 * @returns The blob containing the ID and contents
 */
export const fetchEventLog = async (userId: string, eventLogId: number) => {
  const response = await fetch(`/storage/get-event-log?user_id=${userId}&event_log_id=${eventLogId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch event log');
  }
  const blob = await response.blob(); // Get the file as a blob
  return blob;
};

/**
 * Uploads a new eventlog
 * 
 * @param file - The file to upload
 * @param userId - The user ID
 * 
 * @returns Status Message
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
 * Updates a eventlog name
 * 
 * @param userId - The user ID
 * @param eventLogId - The eventlog ID to update
 * @param updateName - The updated name
 * 
 * @returns Boolean indiciating if the update was successful
 */
export const updateEventLogName = async (userId: string, eventLogId: number, updateName: string) => {
  try {
    const response = await fetch(
      `/storage/update-event-log?user_id=${userId}&event_log_id=${eventLogId}&filename=${updateName}`,
      {
        method: 'PUT'
      }
    );
    if (!response.ok) {
      throw new Error('Failed to update event log');
    }

    return true;
  } catch (error) {
    console.error("Update event log error: ", error);
    return false;
  }
};

/**
 * Deletes a specific eventlog from a user ID
 * 
 * @param userId - The user ID 
 * @param eventLogId - The eventlog ID to delete
 * 
 * @returns Boolean indicating if the deletion was successfull
 */
export const deleteEventLog = async (userId: string, eventLogId: string): Promise<boolean> => {
  try {
    const response = await fetch(`/storage/delete-event-log?user_id=${userId}&event_log_id=${eventLogId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error('Failed to delete event log');
    }

    return true;
  } catch (error) {
    console.error('Delete error:', error);
    return false;
  }
};

/**
 * Deletes all eventlogs from a user
 * 
 * @param userId - The user ID
 * 
 * @returns Boolean indicating if the deletion was successfull
 */
export const deleteAllEventLogs = async (userId: string): Promise<boolean> => {
  try {
    const response = await fetch(`/storage/delete-all-event-logs?user_id=${userId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error('Failed to delete all event logs');
    }

    return true;
  } catch (error) {
    console.error('Delete all error:', error);
    return false;
  }
};

/**
 * Take thes xes file and converts it to a csv
 * 
 * @param file - The file to convert
 * 
 * @returns success, file, Status message
 */
export const xesToCsv = async (file: File): Promise<{ success: boolean; file?: File; message: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`/api/xes-to-csv`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to convert xes file to csv');
    }

    // Update the filename to csv
    const originalName = file.name;
    const filename = originalName.replace(/\.[^/.]+$/, '.csv');

    const blob = await response.blob();
    const csvFile = new File([blob], filename, { type: "text/csv" });

    return { success: true, file: csvFile, message: "Success" };
  } catch (error: any) {
    return { success: false, message: error?.message || 'Unknown error' };
  }
};