/**
 * @fileoverview Simod Scenario API section component for the API playground
 * 
 * Provides interactive forms for managing Simod scenarios including upload, 
 * retrieval, listing, updating, and deletion operations.
 */

import React, { useState } from 'react';
import {
  demoUploadSimodScenario,
  demoGetSimodScenario,
  demoListSimodScenarios,
  demoUpdateSimodScenario,
  demoDeleteSimodScenario
} from '../../api/controllerAPICallDemos/simodScenarioDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the SimodScenarioApiSection component
 */
interface SimodScenarioApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Simod Scenario API Section Component
 * 
 * Renders appropriate input forms and controls based on the selected Simod scenario operation.
 * Supports CRUD operations for Simod scenarios including file uploads and downloads.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific forms
 */
const SimodScenarioApiSection: React.FC<SimodScenarioApiSectionProps> = ({ operation, logResult }) => {
  /** User ID input state */
  const [userId, setUserId] = useState('');
  
  /** Event log ID input state */
  const [eventLogId, setEventLogId] = useState('');
  
  /** Scenario ID input state */
  const [scenarioId, setScenarioId] = useState('');
  
  /** Scenario name input state */
  const [scenarioName, setScenarioName] = useState('');
  
  /** Selected BPMN file state */
  const [bpmnFile, setBpmnFile] = useState<File | null>(null);
  
  /** Selected parameters JSON file state */
  const [paramFile, setParamFile] = useState<File | null>(null);

  /**
   * Handles BPMN file selection from file input
   * 
   * @param e - File input change event
   */
  const handleBpmnFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setBpmnFile(e.target.files[0]);
    } else {
      setBpmnFile(null);
    }
  };

  /**
   * Handles parameters file selection from file input
   * 
   * @param e - File input change event
   */
  const handleParamFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setParamFile(e.target.files[0]);
    } else {
      setParamFile(null);
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
  case 'uploadSimodScenario':
    return (
      <div className="flex flex-col space-y-6 mt-6">
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
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Scenario Name:</span>
          <input
            type="text"
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Scenario Name"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">BPMN File:</span>
          <input
            type="file"
            accept=".bpmn,.xml"
            onChange={handleBpmnFileChange}
            className="border rounded p-2 flex-grow max-w-md"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Parameters:</span>
          <input
            type="file"
            accept=".json"
            onChange={handleParamFileChange}
            className="border rounded p-2 flex-grow max-w-md"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!eventLogId) {
                logResult("Error: Please enter an event log ID");
                return;
              }
              if (!scenarioName) {
                logResult("Error: Please enter a scenario name");
                return;
              }
              if (!bpmnFile) {
                logResult("Error: Please select a BPMN file");
                return;
              }
              if (!paramFile) {
                logResult("Error: Please select a parameters JSON file");
                return;
              }
              logResult(`Uploading Simod scenario for event log ID: ${eventLogId}...`);
              try {
                const result = await demoUploadSimodScenario(
                  eventLogId,
                  scenarioName,
                  bpmnFile,
                  paramFile
                );
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!eventLogId || !scenarioName || !bpmnFile || !paramFile}
          >
              Upload Simod Scenario
          </button>
        </div>
      </div>
    );

  case 'getSimodScenario':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Scenario ID:</span>
          <input
            type="text"
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Scenario ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              logResult(`Fetching Simod scenario with ID: ${scenarioId}...`);
              try {
                const result = await demoGetSimodScenario(scenarioId);
                
                // Create HTML with all download links
                let outputHtml = "Simod scenario retrieved successfully\n\n";
                
                // Full zip download
                outputHtml += `<a href="${result.scenarioUrl}" download="${result.fileName}" ` +
                  'class="text-blue-500 underline">Download Complete Scenario ZIP</a>\n\n';
                
                // BPMN model download if available
                if (result.bpmnUrl) {
                  outputHtml += `<a href="${result.bpmnUrl}" download="${result.bpmnFilename}" ` +
                    'class="text-blue-500 underline">Download BPMN Model</a>\n\n';
                }
                
                // Parameters download if available
                if (result.parametersUrl) {
                  outputHtml += `<a href="${result.parametersUrl}" download="${result.parametersFilename}" ` +
                    'class="text-blue-500 underline">Download Parameters JSON</a>';
                }
                
                logResult(outputHtml);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!scenarioId}
          >
              Get Simod Scenario
          </button>
        </div>
      </div>
    );

  case 'listSimodScenarios':
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
            placeholder="Enter Event Log ID (optional)"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              logResult(
                `Listing Simod scenarios for user: ${userId}${
                  eventLogId ? `, event log ID: ${eventLogId}` : ''
                }...`
              );
              try {
                const result = await demoListSimodScenarios(userId, eventLogId || undefined);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId}
          >
              List Simod Scenarios
          </button>
        </div>
      </div>
    );

  case 'updateSimodScenario':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Scenario ID:</span>
          <input
            type="text"
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Scenario ID"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">New Name:</span>
          <input
            type="text"
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter New Scenario Name (optional)"
          />
        </div>
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">New Params:</span>
          <input
            type="file"
            accept=".json"
            onChange={handleParamFileChange}
            className="border rounded p-2 flex-grow max-w-md"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              if (!scenarioName && !paramFile) {
                logResult("Error: Please provide either a new name or new parameters file");
                return;
              }
              logResult(`Updating Simod scenario with ID: ${scenarioId}...`);
              try {
                const result = await demoUpdateSimodScenario(
                  scenarioId,
                  scenarioName || undefined,
                  paramFile || undefined
                );
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!scenarioId || (!scenarioName && !paramFile)}
          >
              Update Simod Scenario
          </button>
        </div>
      </div>
    );

  case 'deleteSimodScenario':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Scenario ID:</span>
          <input
            type="text"
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Scenario ID"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              logResult(`Deleting Simod scenario with ID: ${scenarioId}...`);
              try {
                const result = await demoDeleteSimodScenario(scenarioId);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!scenarioId}
          >
              Delete Simod Scenario
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select a Simod Scenario operation.</div>;
  }
};

export default SimodScenarioApiSection; 