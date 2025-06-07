/**
 * @fileoverview Analyze API section component for the API playground
 * 
 * Provides interactive forms for analysis operations including event log 
 * analysis and Simod scenario output analysis.
 */

import React, { useState } from 'react';
import {
  demoAnalyzeEventLog,
  demoAnalyzeSimodScenarioOutput
} from '../../api/controllerAPICallDemos/analyzeDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the AnalyzeApiSection component
 */
interface AnalyzeApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Analyze API Section Component
 * 
 * Renders appropriate input forms and controls for analysis operations.
 * Supports event log analysis and Simod scenario output analysis with downloadable results.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific forms
 */
const AnalyzeApiSection: React.FC<AnalyzeApiSectionProps> = ({ operation, logResult }) => {
  /** User ID input state */
  const [userId, setUserId] = useState('');
  
  /** Event log ID input state */
  const [eventLogId, setEventLogId] = useState('');
  
  /** Simod scenario ID input state */
  const [simodScenarioId, setSimodScenarioId] = useState('');

  /**
   * Creates a downloadable blob URL for JSON data
   * 
   * @param data - Data to convert to downloadable JSON blob
   * @returns Blob URL for downloading the JSON data
   */
  const createDownloadLink = (data: any) => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    return URL.createObjectURL(blob);
  };

  // Render the content based on the operation
  switch (operation) {
  case 'analyzeEventLog':
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
              logResult(`Running Event Log Analysis for user: ${userId}, log ID: ${eventLogId}...`);
              try {
                const result = await demoAnalyzeEventLog(userId, eventLogId);
                logResult(`Event Log ID: ${result.event_log_id}`);
                const downloadLink = createDownloadLink(result.analysis_result);
                logResult(`Download Analysis Result: <a href="${downloadLink}" 
                  download="analysis_result.json">Click here</a>`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !eventLogId}
          >
            Analyze Event Log
          </button>
        </div>
      </div>
    );

  case 'analyzeSimodScenarioOutput':
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
          <span className="w-24 text-right pr-3">Simod Scenario ID:</span>
          <input
            type="text"
            value={simodScenarioId}
            onChange={(e) => setSimodScenarioId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Simod Scenario ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!simodScenarioId) {
                logResult("Error: Please enter a simod scenario ID");
                return;
              }
              logResult(`Running Simod Scenario Output Analysis for user: ${userId},
                simod scenario ID: ${simodScenarioId}...`);
              try {
                const result = await demoAnalyzeSimodScenarioOutput(userId, parseInt(simodScenarioId));
                logResult(`Event Log ID: ${result.event_log_id}`);
                const downloadLink = createDownloadLink(result.analysis_result);
                logResult(`Download Analysis Result: <a href="${downloadLink}" 
                  download="analysis_result.json">Click here</a>`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !simodScenarioId}
          >
            Analyze Simod Scenario Output
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select an Analyze operation.</div>;
  }
};

export default AnalyzeApiSection; 