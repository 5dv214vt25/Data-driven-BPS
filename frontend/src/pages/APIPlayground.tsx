/**
 * @fileoverview API Playground - A CLI-like interface for testing backend API calls
 * 
 * This module provides a comprehensive web-based interface that functions similarly to a 
 * command-line interface (CLI) for interacting with the backend API. It allows developers
 * and users to test, experiment with, and demonstrate various API operations without 
 * needing to write separate scripts or use external tools like Postman or curl. 
 */

import { useState } from 'react';
import EventLogApiSection from '../components/APIPlaygroundComponents/EventLogApiSection';
import SimodOutputApiSection from '../components/APIPlaygroundComponents/SimodOutputApiSection';
import SimodGeneralApiSection from '../components/APIPlaygroundComponents/SimodGeneralApiSection';
import SimodScenarioApiSection from '../components/APIPlaygroundComponents/SimodScenarioApiSection';
import ControllerGeneralApiSection from '../components/APIPlaygroundComponents/ControllerGeneralApiSection';
import AgentGeneralApiSection from '../components/APIPlaygroundComponents/AgentGeneralApiSection';
import AgentScenarioApiSection from '../components/APIPlaygroundComponents/AgentScenarioApiSection';
import AnalyzeApiSection from '../components/APIPlaygroundComponents/AnalyzeApiSection';

/**
 * Union type representing all available API operations in the playground.
 * 
 * Operations are grouped by functionality:
 * - Event Log operations: Handle event log management
 * - Simod operations: Handle Simod discovery and simulation
 * - Simod Scenario operations: Manage Simod scenarios
 * - Simod Output operations: Manage Simod outputs
 * - Agent operations: Handle agent discovery and simulation
 * - Agent Scenario operations: Manage agent scenarios
 * - Controller operations: General controller utilities
 * - Analyze operations: Analysis and reporting functions
 */
export type ApiOperation = 
  | 'listEventLogs' 
  | 'getEventLog' 
  | 'uploadEventLog' 
  | 'deleteEventLog' 
  | 'deleteAllEventLogs'
  | 'listSimodOutputs'
  | 'getSimodOutput'
  | 'uploadSimodOutput'
  | 'updateSimodOutput'
  | 'deleteSimodOutput'
  | 'startSimodDiscovery'
  | 'startSimodSimulation'
  | 'uploadSimodScenario'
  | 'getSimodScenario'
  | 'listSimodScenarios'
  | 'updateSimodScenario'
  | 'deleteSimodScenario'
  | 'uploadAgentScenario'
  | 'getAgentScenario'
  | 'listAgentScenarios'
  | 'updateAgentScenario'
  | 'deleteAgentScenario'
  | 'healthCheck'
  | 'getTestMessageFromController'
  | 'simodDemoRequest'
  | 'agentSimulatorDemoRequest'
  | 'startAgentDiscovery'
  | 'startAgentSimulation'
  | 'analyzeEventLog'
  | 'analyzeSimodScenarioOutput';

/**
 * Determines if the given operation is related to event log management.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is an event log operation, false otherwise
 */
function isEventLogOperation(operation: ApiOperation): boolean {
  return [
    'listEventLogs',
    'getEventLog',
    'uploadEventLog',
    'deleteEventLog',
    'deleteAllEventLogs'
  ].includes(operation);
}

/**
 * Determines if the given operation is a general Simod operation.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is a Simod discovery or simulation operation, false otherwise
 */
const isSimodOperation = (operation: ApiOperation): boolean => {
  return [
    'startSimodDiscovery', 
    'startSimodSimulation'
  ].includes(operation);
};

/**
 * Determines if the given operation is related to Simod scenario management.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is a Simod scenario operation, false otherwise
 */
const isSimodScenarioOperation = (operation: ApiOperation): boolean => {
  return [
    'uploadSimodScenario', 
    'getSimodScenario', 
    'listSimodScenarios', 
    'updateSimodScenario', 
    'deleteSimodScenario'
  ].includes(operation);
};

/**
 * Determines if the given operation is related to Simod output management.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is a Simod output operation, false otherwise
 */
const isSimodOutputOperation = (operation: ApiOperation): boolean => {
  return [
    'listSimodOutputs', 
    'getSimodOutput', 
    'uploadSimodOutput', 
    'updateSimodOutput', 
    'deleteSimodOutput'
  ].includes(operation);
};

/**
 * Determines if the given operation is a general controller operation.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is a controller operation, false otherwise
 */
const isControllerOperation = (operation: ApiOperation): boolean => {
  return [
    'healthCheck', 
    'getTestMessageFromController', 
    'simodDemoRequest', 
    'agentSimulatorDemoRequest'
  ].includes(operation);
};

/**
 * Determines if the given operation is a general agent operation.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is an agent discovery or simulation operation, false otherwise
 */
const isAgentOperation = (operation: ApiOperation): boolean => {
  return [
    'startAgentDiscovery', 
    'startAgentSimulation'
  ].includes(operation);
};

/**
 * Determines if the given operation is related to agent scenario management.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is an agent scenario operation, false otherwise
 */
const isAgentScenarioOperation = (operation: ApiOperation): boolean => {
  return [
    'uploadAgentScenario', 
    'getAgentScenario', 
    'listAgentScenarios', 
    'updateAgentScenario', 
    'deleteAgentScenario'
  ].includes(operation);
};

/**
 * Determines if the given operation is related to analysis and reporting.
 * 
 * @param operation - The API operation to check
 * @returns True if the operation is an analysis operation, false otherwise
 */
const isAnalyzeOperation = (operation: ApiOperation): boolean => {
  return [
    'analyzeEventLog',
    'analyzeSimodScenarioOutput'
  ].includes(operation);
};

/**
 * API Playground Component
 * 
 * A comprehensive interface for testing and demonstrating API operations.
 * Provides a dropdown selector for all available API operations and displays
 * the appropriate input form based on the selected operation type.
 * 
 * Features:
 * - Single dropdown interface for all API operations
 * - Context-aware input forms that show only relevant fields
 * - Real-time results display with logging capability
 * - Clear results functionality for better user experience
 * - Organized operation groups for better navigation
 * 
 * @component
 * @returns JSX element representing the API playground interface
 */
function APIPlayground() {
  /** Currently selected API operation */
  const [activeOperation, setActiveOperation] = useState<ApiOperation>('listEventLogs');
  
  /** Accumulated results from API operations */
  const [results, setResults] = useState<string>('');

  /**
   * Logs a result message by appending it to the results state and console.
   * 
   * @param message - The message to log
   */
  const logResult = (message: string) => {
    setResults(prev => `${prev}\n${message}`);
    console.log(message);
  };

  /**
   * Clears all accumulated results from the display.
   */
  const clearResults = () => {
    setResults('');
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">API Playground</h1>
      
      {/* Description */}
      <p className="mb-6 text-gray-700">
        This is a playground for testing, experimenting and demoing API calls to the controller in the backend <br />
        Select an operation from the dropdown below, provide the required inputs, <br />
        and click the corresponding button to see the results.
      </p>
      
      {/* Operation Selector */}
      <div className="mb-4">
        <label htmlFor="operation-selector" className="block mb-2 font-medium">
          Select API Operation:
        </label>
        <select 
          id="operation-selector"
          value={activeOperation}
          onChange={(e) => setActiveOperation(e.target.value as ApiOperation)}
          className="border rounded p-2 w-full max-w-md"
        >
          <optgroup label="Controller General Operations">
            <option value="healthCheck">Health Check</option>
            <option value="getTestMessageFromController">Get Test Message</option>
            <option value="simodDemoRequest">Simod Demo Request</option>
            <option value="agentSimulatorDemoRequest">Agent Simulator Demo Request</option>
          </optgroup>
          <optgroup label="Event Log Operations">
            <option value="listEventLogs">List Event Logs</option>
            <option value="getEventLog">Get Event Log</option>
            <option value="uploadEventLog">Upload Event Log</option>
            <option value="deleteEventLog">Delete Event Log</option>
            <option value="deleteAllEventLogs">Delete All Event Logs</option>
          </optgroup>
          <optgroup label="Simod General Operations">
            <option value="startSimodDiscovery">Start Simod Discovery</option>
            <option value="startSimodSimulation">Start Simod Simulation</option>
          </optgroup>
          <optgroup label="Simod Scenario Operations">
            <option value="uploadSimodScenario">Upload Simod Scenario</option>
            <option value="getSimodScenario">Get Simod Scenario</option>
            <option value="listSimodScenarios">List Simod Scenarios</option>
            <option value="updateSimodScenario">Update Simod Scenario</option>
            <option value="deleteSimodScenario">Delete Simod Scenario</option>
          </optgroup>
          <optgroup label="Simod Output Operations">
            <option value="listSimodOutputs">List Simod Outputs</option>
            <option value="getSimodOutput">Get Simod Output</option>
            <option value="uploadSimodOutput">Upload Simod Output</option>
            <option value="updateSimodOutput">Update Simod Output</option>
            <option value="deleteSimodOutput">Delete Simod Output</option>
          </optgroup>
          <optgroup label="Agent General Operations">
            <option value="startAgentDiscovery">Start Agent Discovery</option>
            <option value="startAgentSimulation">Start Agent Simulation</option>
          </optgroup>
          <optgroup label="Agent Scenario Operations">
            <option value="uploadAgentScenario">Upload Agent Scenario</option>
            <option value="getAgentScenario">Get Agent Scenario</option>
            <option value="listAgentScenarios">List Agent Scenarios</option>
            <option value="updateAgentScenario">Update Agent Scenario</option>
            <option value="deleteAgentScenario">Delete Agent Scenario</option>
          </optgroup>
          <optgroup label="Analyze Operations">
            <option value="analyzeEventLog">Event Log Analysis</option>
            <option value="analyzeSimodScenarioOutput">Simod Scenario Output Analysis</option>
          </optgroup>
        </select>
      </div>
      
      {/* Add very explicit spacing */}
      <div className="h-16 w-full"></div>
      
      {/* Operation Content */}
      <div className="p-4 border rounded bg-gray-50 mb-6">
        {isEventLogOperation(activeOperation) ? (
          <EventLogApiSection operation={activeOperation} logResult={logResult} />
        ) : isSimodOperation(activeOperation) ? (
          <SimodGeneralApiSection operation={activeOperation} logResult={logResult} />
        ) : isAgentOperation(activeOperation) ? (
          <AgentGeneralApiSection operation={activeOperation} logResult={logResult} />
        ) : isSimodScenarioOperation(activeOperation) ? (
          <SimodScenarioApiSection operation={activeOperation} logResult={logResult} />
        ) : isSimodOutputOperation(activeOperation) ? (
          <SimodOutputApiSection operation={activeOperation} logResult={logResult} />
        ) : isControllerOperation(activeOperation) ? (
          <ControllerGeneralApiSection operation={activeOperation} logResult={logResult} />
        ) : isAgentScenarioOperation(activeOperation) ? (
          <AgentScenarioApiSection operation={activeOperation} logResult={logResult} />
        ) : isAnalyzeOperation(activeOperation) ? (
          <AnalyzeApiSection operation={activeOperation} logResult={logResult} />
        ) : (
          <div>Unknown operation type</div>
        )}
      </div>
      
      {/* Results Display */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-medium">Results:</h3>
          <button 
            onClick={clearResults}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-3 py-1 rounded text-sm"
          >
            Clear Results
          </button>
        </div>
        <pre 
          className="bg-gray-100 p-4 rounded max-h-80 overflow-auto whitespace-pre-wrap border"
          dangerouslySetInnerHTML={{ __html: results || "Run a demo to see results here..." }}
        />
      </div>
    </div>
  );
}

export default APIPlayground;