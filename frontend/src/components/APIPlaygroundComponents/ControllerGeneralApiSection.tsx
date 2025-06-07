/**
 * @fileoverview Controller General API section component for the API playground
 * 
 * Provides interactive forms for general controller operations including 
 * health checks, test messages, and demo requests.
 */

import React from 'react';
import {
  demoHealthCheck,
  demoGetTestMessage,
  demoSimodRequest,
  demoAgentSimulatorRequest
} from '../../api/controllerAPICallDemos/controllerGeneralDemo';
import { ApiOperation } from '../../pages/APIPlayground';

/**
 * Props for the ControllerGeneralApiSection component
 */
interface ControllerGeneralApiSectionProps {
  /** The selected API operation to display */
  operation: ApiOperation;
  /** Callback function to log results and errors */
  logResult: (message: string) => void;
}

/**
 * Controller General API Section Component
 * 
 * Renders appropriate controls for general controller operations that don't require parameters.
 * Supports health checks, test messages, and demo requests for system validation.
 * 
 * @component
 * @param props - The component props
 * @returns JSX element with operation-specific controls
 */
const ControllerGeneralApiSection: React.FC<ControllerGeneralApiSectionProps> = ({ operation, logResult }) => {
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
  case 'healthCheck':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <p className="text-gray-600">
            Check the health status of the controller. No parameters needed.
        </p>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              logResult('Checking controller health...');
              try {
                const result = await demoHealthCheck();
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
              Check Health
          </button>
        </div>
      </div>
    );

  case 'getTestMessageFromController':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <p className="text-gray-600">
            Get a test message from the controller. No parameters needed.
        </p>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              logResult('Getting test message from controller...');
              try {
                const result = await demoGetTestMessage();
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
              Get Test Message
          </button>
        </div>
      </div>
    );

  case 'simodDemoRequest':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <p className="text-gray-600">
            Send a Simod demo request to the controller. No parameters needed.
        </p>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              logResult('Sending Simod demo request...');
              try {
                const result = await demoSimodRequest();
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
              Send Simod Demo Request
          </button>
        </div>
      </div>
    );

  case 'agentSimulatorDemoRequest':
    return (
      <div className="flex flex-col space-y-6 mt-6">
        <p className="text-gray-600">
            Send an agent simulator demo request to the controller. No parameters needed.
        </p>
        <div className="flex justify-end mt-6">
          <button
            onClick={async () => {
              logResult('Sending agent simulator demo request...');
              try {
                const result = await demoAgentSimulatorRequest();
                logResult(formatJsonOutput(result));
              } catch (error) {
                logResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
              }
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
              Send Agent Simulator Demo Request
          </button>
        </div>
      </div>
    );

  default:
    return <div>Please select a Controller General API operation.</div>;
  }
};

export default ControllerGeneralApiSection; 