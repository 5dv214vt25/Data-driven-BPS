/**
 * @fileoverview Simod Output API section component for the API playground
 * 
 * Provides interactive forms for managing Simod outputs including upload, 
 * retrieval, listing, updating, and deletion operations.
 */

import React, { useState } from 'react';
import {
  demoListSimodOutputs,
  demoGetSimodOutput,
  demoUploadSimodOutput,
  demoUpdateSimodOutput,
  demoDeleteSimodOutput
} from '../../api/controllerAPICallDemos/simodOutputDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the SimodOutputApiSection component
 */
interface SimodOutputApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Simod Output API Section Component
 * 
 * Renders appropriate input forms and controls based on the selected Simod output operation.
 * Supports CRUD operations for Simod outputs including file uploads and downloads.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific forms
 */
const SimodOutputApiSection: React.FC<SimodOutputApiSectionProps> = ({ operation, logResult }) => {
  /** User ID input state */
  const [userId, setUserId] = useState('');
  
  /** Scenario ID input state */
  const [scenarioId, setScenarioId] = useState('');
  
  /** Selected output file state */
  const [outputFile, setOutputFile] = useState<File | null>(null);

  /**
   * Handles output file selection from file input
   * 
   * @param e - File input change event
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setOutputFile(e.target.files[0]);
    } else {
      setOutputFile(null);
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
  case 'listSimodOutputs':
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
          <span className="w-24 text-right pr-3">Scenario ID:</span>
          <input
            type="text"
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="border rounded p-2 flex-grow max-w-md"
            placeholder="Enter Scenario ID (optional)"
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
                `Listing Simod outputs for user: ${userId}${
                  scenarioId ? `, filtered by scenario ID: ${scenarioId}` : ''
                }...`
              );
              try {
                const result = await demoListSimodOutputs(userId, scenarioId ? parseInt(scenarioId) : undefined);
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId}
          >
              List Simod Outputs
          </button>
        </div>
      </div>
    );

  case 'getSimodOutput':
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
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              logResult(`Getting Simod output for user: ${userId}, scenario ID: ${scenarioId}...`);
              try {
                const result = await demoGetSimodOutput(userId, parseInt(scenarioId));

                // Create download link
                const downloadLink = `<a href="${result.downloadUrl}" ` + 
                  `download="simod_output_${scenarioId}.json" ` + 
                  'class="text-blue-500 underline">Download Simod Output</a>';

                // Add preview
                const preview = `\n\nPreview:\n${result.preview}`;

                logResult(`Simod output retrieved successfully\n\n${downloadLink}${preview}`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !scenarioId}
          >
              Get Simod Output
          </button>
        </div>
      </div>
    );

  case 'uploadSimodOutput':
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
          <span className="w-24 text-right pr-3">Output File:</span>
          <input
            type="file"
            accept=".json,.csv,.txt"
            onChange={handleFileChange}
            className="border rounded p-2 flex-grow max-w-md"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              if (!outputFile) {
                logResult("Error: Please select an output file");
                return;
              }
              logResult(`Uploading Simod output for user: ${userId}, scenario ID: ${scenarioId}...`);
              try {
                const result = await demoUploadSimodOutput(userId, parseInt(scenarioId), outputFile);
                logResult(`Upload ${result ? 'successful' : 'failed'}`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !scenarioId || !outputFile}
          >
              Upload Simod Output
          </button>
        </div>
      </div>
    );

  case 'updateSimodOutput':
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
          <span className="w-24 text-right pr-3">Output File:</span>
          <input
            type="file"
            accept=".json,.csv,.txt"
            onChange={handleFileChange}
            className="border rounded p-2 flex-grow max-w-md"
          />
        </div>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              if (!outputFile) {
                logResult("Error: Please select an output file");
                return;
              }
              logResult(`Updating Simod output for user: ${userId}, scenario ID: ${scenarioId}...`);
              try {
                const result = await demoUpdateSimodOutput(userId, parseInt(scenarioId), outputFile);
                logResult(`Update ${result ? 'successful' : 'failed'}`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !scenarioId || !outputFile}
          >
              Update Simod Output
          </button>
        </div>
      </div>
    );

  case 'deleteSimodOutput':
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
              if (!userId) {
                logResult("Error: Please enter a user ID");
                return;
              }
              if (!scenarioId) {
                logResult("Error: Please enter a scenario ID");
                return;
              }
              logResult(`Deleting Simod output for user: ${userId}, scenario ID: ${scenarioId}...`);
              try {
                const result = await demoDeleteSimodOutput(userId, parseInt(scenarioId));
                logResult(`Delete ${result ? 'successful' : 'failed'}`);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !scenarioId}
          >
              Delete Simod Output
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select a Simod Output operation.</div>;
  }
};

export default SimodOutputApiSection; 