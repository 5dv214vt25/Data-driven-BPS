/**
 * @fileoverview Event Log API section component for the API playground
 * 
 * Provides interactive forms for managing event logs including upload, 
 * retrieval, listing, and deletion operations.
 */

import React, { useState } from 'react';
import {
  demoListEventLogs,
  demoGetEventLog,
  demoUploadEventLog,
  demoDeleteEventLog,
  demoDeleteAllEventLogs
} from '../../api/controllerAPICallDemos/eventLogDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the EventLogApiSection component
 */
interface EventLogApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Event Log API Section Component
 * 
 * Renders appropriate input forms and controls based on the selected event log operation.
 * Supports CRUD operations for event logs including file uploads and downloads.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific forms
 */
const EventLogApiSection: React.FC<EventLogApiSectionProps> = ({ operation, logResult }) => {
  /** User ID input state */
  const [userId, setUserId] = useState('');
  
  /** Event log ID input state */
  const [eventLogId, setEventLogId] = useState('');
  
  /** Selected event log file state */
  const [eventLogFile, setEventLogFile] = useState<File | null>(null);

  /**
   * Handles event log file selection from file input
   * 
   * @param e - File input change event
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setEventLogFile(e.target.files[0]);
    } else {
      setEventLogFile(null);
    }
  };

  /**
   * Formats JSON data for display with proper indentation
   * 
   * @param data - Data to format as JSON string
   * @returns Formatted JSON string
   */
  const formatJsonOutput = (data: any) => {
    return JSON.stringify(data, null, 2);
  };

  // Render the content based on the operation
  switch (operation) {
  case 'listEventLogs':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">User ID:</span>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter User ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              logResult(`Running List Event Logs demo for user: ${userId}...`);
              try {
                const result = await demoListEventLogs(userId);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId}
          >
              List Event Logs
          </button>
        </div>
      </div>
    );

  case 'getEventLog':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">User ID:</span>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter User ID"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Event Log ID:</span>
          <input
            type="text"
            value={eventLogId}
            onChange={(e) => setEventLogId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Event Log ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!eventLogId) {
                logResult("Error: Please enter an event log ID");
                return;
              }
              logResult(`Running Get Event Log demo for user: ${userId}, log ID: ${eventLogId}...`);
              try {
                const result = await demoGetEventLog(userId, eventLogId);

                // Create download link HTML
                const downloadLink = `<a href="${result.downloadUrl}" download="event_log_${eventLogId}.csv" ` + 
                  'class="text-blue-500 underline">Download Event Log</a>';

                // Add preview section
                const preview = `\n\nPreview (first 5 lines):\n${result.preview}`;

                // Show minimal output
                logResult(`Event log retrieved successfully\n\n${downloadLink}${preview}`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !eventLogId}
          >
              Get Event Log
          </button>
        </div>
      </div>
    );

  case 'uploadEventLog':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">User ID:</span>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter User ID"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">File:</span>
          <div className="flex flex-grow max-w-md items-center">
            <input
              type="file"
              onChange={handleFileChange}
              className="border p-2"
            />
            {eventLogFile && (
              <span className="text-sm text-gray-600 ml-2">
                {eventLogFile.name}
              </span>
            )}
          </div>
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!eventLogFile) {
                logResult("Error: Please select a file first");
                return;
              }
              logResult(`Running Upload Event Log demo for user: ${userId}, file: ${eventLogFile.name}...`);
              try {
                const result = await demoUploadEventLog(eventLogFile, userId);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !eventLogFile}
          >
              Upload Event Log
          </button>
        </div>
      </div>
    );

  case 'deleteEventLog':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">User ID:</span>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter User ID"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Event Log ID:</span>
          <input
            type="text"
            value={eventLogId}
            onChange={(e) => setEventLogId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Event Log ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!eventLogId) {
                logResult("Error: Please enter an event log ID");
                return;
              }
              logResult(`Running Delete Event Log demo for user: ${userId}, log ID: ${eventLogId}...`);
              try {
                const result = await demoDeleteEventLog(userId, eventLogId);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !eventLogId}
          >
              Delete Event Log
          </button>
        </div>
      </div>
    );

  case 'deleteAllEventLogs':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">User ID:</span>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter User ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              logResult(`Running Delete All Event Logs demo for user: ${userId}...`);
              try {
                const result = await demoDeleteAllEventLogs(userId);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId}
          >
              Delete All Event Logs
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select an Event Log operation.</div>;
  }
};

export default EventLogApiSection; 