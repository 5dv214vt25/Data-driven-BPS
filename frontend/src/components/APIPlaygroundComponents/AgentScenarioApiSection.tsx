/**
 * @fileoverview Agent Scenario API section component for the API playground
 * 
 * Provides interactive forms for managing agent scenarios including upload, 
 * retrieval, listing, updating, and deletion operations.
 */

import React, { useState } from 'react';
import {
  demoUploadAgentScenario,
  demoGetAgentScenario,
  demoListAgentScenarios,
  demoUpdateAgentScenario,
  demoDeleteAgentScenario
} from '../../api/controllerAPICallDemos/agentScenarioDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the AgentScenarioApiSection component
 */
interface AgentScenarioApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Agent Scenario API Section Component
 * 
 * Renders appropriate input forms and controls based on the selected agent scenario operation.
 * Supports CRUD operations for agent scenarios including file uploads and downloads.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific forms
 */
const AgentScenarioApiSection: React.FC<AgentScenarioApiSectionProps> = ({ operation, logResult }) => {
  /** User ID input state */
  const [userId, setUserId] = useState('');
  
  /** Event log ID input state */
  const [eventLogId, setEventLogId] = useState('');
  
  /** Scenario ID input state */
  const [scenarioId, setScenarioId] = useState('');
  
  /** Scenario name input state */
  const [scenarioName, setScenarioName] = useState('');
  
  /** Selected model file (.pkl) state */
  const [modelFile, setModelFile] = useState<File | null>(null);
  
  /** Selected parameters JSON file state */
  const [paramFile, setParamFile] = useState<File | null>(null);
  
  /** Selected visualization JSON file state */
  const [visualizationFile, setVisualizationFile] = useState<File | null>(null);

  /**
   * Handles model file selection from file input
   * 
   * @param e - File input change event
   */
  const handleModelFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setModelFile(e.target.files[0]);
    } else {
      setModelFile(null);
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
   * Handles visualization file selection from file input
   * 
   * @param e - File input change event
   */
  const handleVisualizationFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setVisualizationFile(e.target.files[0]);
    } else {
      setVisualizationFile(null);
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
  case 'uploadAgentScenario':
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
          <span className="w-24 text-right pr-3">Model File:</span>
          <input
            type="file"
            accept=".pkl"
            onChange={handleModelFileChange}
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
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Visualization:</span>
          <input
            type="file"
            accept=".json"
            onChange={handleVisualizationFileChange}
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
              if (!modelFile) {
                logResult("Error: Please select a model file");
                return;
              }
              if (!paramFile) {
                logResult("Error: Please select a parameters JSON file");
                return;
              }
              if (!visualizationFile) {
                logResult("Error: Please select a visualization JSON file");
                return;
              }
              logResult(`Uploading Agent scenario for event log ID: ${eventLogId}...`);
              try {
                const result = await demoUploadAgentScenario(
                  eventLogId,
                  scenarioName,
                  modelFile,
                  paramFile,
                  visualizationFile
                );
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!eventLogId || !scenarioName || !modelFile || !paramFile || !visualizationFile}
          >
              Upload Agent Scenario
          </button>
        </div>
      </div>
    );

  case 'getAgentScenario':
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
              logResult(`Fetching Agent scenario with ID: ${scenarioId}...`);
              try {
                const result = await demoGetAgentScenario(scenarioId);
                
                // Create HTML with all download links
                let outputHtml = "Agent scenario retrieved successfully\n\n";
                
                // Full zip download
                outputHtml += `<a href="${result.scenarioUrl}" download="${result.fileName}" ` +
                  'class="text-blue-500 underline">Download Complete Scenario ZIP</a>\n\n';
                
                // Model file download if available
                if (result.modelUrl) {
                  outputHtml += `<a href="${result.modelUrl}" download="${result.modelFilename}" ` +
                    'class="text-blue-500 underline">Download Model File</a>\n\n';
                }
                
                // Parameters download if available
                if (result.parametersUrl) {
                  outputHtml += `<a href="${result.parametersUrl}" download="${result.parametersFilename}" ` +
                    'class="text-blue-500 underline">Download Parameters JSON</a>\n\n';
                }
                
                // Visualization download if available
                if (result.visualizationUrl) {
                  outputHtml += `<a href="${result.visualizationUrl}" download="${result.visualizationFilename}" ` +
                    'class="text-blue-500 underline">Download Visualization JSON</a>';
                }
                
                logResult(outputHtml);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!scenarioId}
          >
              Get Agent Scenario
          </button>
        </div>
      </div>
    );

  case 'listAgentScenarios':
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
                `Listing Agent scenarios for user: ${userId}${
                  eventLogId ? `, event log ID: ${eventLogId}` : ''
                }...`
              );
              try {
                const result = await demoListAgentScenarios(userId, eventLogId || undefined);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId}
          >
              List Agent Scenarios
          </button>
        </div>
      </div>
    );

  case 'updateAgentScenario':
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
              logResult(`Updating Agent scenario with ID: ${scenarioId}...`);
              try {
                const result = await demoUpdateAgentScenario(
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
              Update Agent Scenario
          </button>
        </div>
      </div>
    );

  case 'deleteAgentScenario':
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
              logResult(`Deleting Agent scenario with ID: ${scenarioId}...`);
              try {
                const result = await demoDeleteAgentScenario(scenarioId);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!scenarioId}
          >
              Delete Agent Scenario
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select an Agent Scenario operation.</div>;
  }
};

export default AgentScenarioApiSection; 