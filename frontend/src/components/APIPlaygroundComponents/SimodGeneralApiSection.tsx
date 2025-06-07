/**
 * @fileoverview Simod General API section component for the API playground
 * 
 * Provides interactive forms for general Simod operations including 
 * discovery and simulation processes.
 */

import React, { useState } from 'react';
import {
  demoStartSimodDiscovery,
  demoStartSimodSimulation
} from '../../api/controllerAPICallDemos/simodGeneralDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the SimodGeneralApiSection component
 */
interface SimodGeneralApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Simod General API Section Component
 * 
 * Renders appropriate input forms and controls for Simod discovery and simulation operations.
 * Supports starting process discovery and simulation with various configuration options.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific forms
 */
const SimodGeneralApiSection: React.FC<SimodGeneralApiSectionProps> = ({ operation, logResult }) => {
  /** User ID input state */
  const [userId, setUserId] = useState('');
  
  /** Event log ID input state */
  const [eventLogId, setEventLogId] = useState('');
  
  /** Scenario ID input state for simulation */
  const [scenarioId, setScenarioId] = useState('');
  
  /** Whether to save the scenario after discovery */
  const [saveScenario, setSaveScenario] = useState(false);
  
  /** Whether to save the simulation results */
  const [saveSimulation, setSaveSimulation] = useState(false);
  
  /** Optional scenario name when saving */
  const [scenarioName, setScenarioName] = useState('');

  // Render the content based on the operation
  switch (operation) {
  case 'startSimodDiscovery':
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
        <div className="flex items-center">
          <span className="w-24 text-right pr-3">Save Scenario:</span>
          <input
            type="checkbox"
            checked={saveScenario}
            onChange={(e) => setSaveScenario(e.target.checked)}
            className="h-4 w-4 mr-2"
          />
        </div>
        {saveScenario && (
          <div className="flex items-center">
            <span className="w-24 text-right pr-3">Scenario Name:</span>
            <input
              type="text"
              value={scenarioName}
              onChange={(e) => setScenarioName(e.target.value)}
              className="border rounded p-2 flex-grow max-w-md"
              placeholder="Enter Scenario Name (optional)"
            />
          </div>
        )}
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
              logResult(`Running Simod Discovery demo for user: ${userId}, event log ID: ${eventLogId}...`);
              try {
                const result = await demoStartSimodDiscovery(
                  userId, 
                  eventLogId, 
                  saveScenario, 
                  scenarioName || undefined
                );

                let output = "Simod discovery completed successfully\n\n";

                // Add scenario ID if saved
                if (result.scenarioId) {
                  output += `Scenario ID: ${result.scenarioId}\n\n`;
                }

                // Add download links
                if (result.bpmnUrl) {
                  output += `<a href="${result.bpmnUrl}" download="process_model.bpmn" ` + 
                    'class="text-blue-500 underline">Download BPMN Model</a>\n\n';
                }

                if (result.parametersUrl) {
                  output += `<a href="${result.parametersUrl}" download="parameters.json" ` + 
                    'class="text-blue-500 underline">Download Parameters JSON</a>';
                }

                logResult(output);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !eventLogId}
          >
              Start Simod Discovery
          </button>
        </div>
      </div>
    );

  case 'startSimodSimulation':
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
          <span className="w-24 text-right pr-3">Save Simulation:</span>
          <input
            type="checkbox"
            checked={saveSimulation}
            onChange={(e) => setSaveSimulation(e.target.checked)}
            className="h-4 w-4 mr-2"
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
              logResult(`Running Simod Simulation demo for user: ${userId}, scenario ID: ${scenarioId}...`);
              try {
                const result = await demoStartSimodSimulation(userId, scenarioId, saveSimulation);

                let output = "Simod simulation completed successfully\n\n";

                // Add download link
                output += `<a href="${result.simulationUrl}" download="simulated_log.csv" ` + 
                  'class="text-blue-500 underline">Download Simulated Event Log</a>\n\n';

                // Add preview
                output += `Preview (first 5 lines):\n${result.preview}`;

                logResult(output);
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={!userId || !scenarioId}
          >
              Start Simod Simulation
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select a Simod General API operation.</div>;
  }
};

export default SimodGeneralApiSection; 