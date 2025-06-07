import { useState } from 'react';

import { startAgentDiscovery } from '../api/controllerAPICalls/AgentGeneralAPICalls';
import { startSimodDiscovery } from "../api/controllerAPICalls/SimodGeneralAPICalls";
import { AgentSimulatorSettings } from '../types/AgentSimulatorTypes';
import { SimodSimulatorSettings } from '../types/SimodSimulatorTypes';

interface bpmnProps {
  bpmnBlob: Blob | null;
  setBpmnBlob: (value: Blob | null) => void;
}

/**
 * Hook to run process discovery using either Simod or AgentSimulator.
 * Manages discovery results like BPMN, ZIP, and extracted parameters.
 *
 * @param {bpmnProps} props - Contains the current BPMN blob and its setter function.
 * @returns {Object} Discovery results, loading state, and the runDiscovery function.
 */
export const useDiscovery = ({bpmnBlob, setBpmnBlob}: bpmnProps) => {
  const [parameters, setParameters] = useState<object | null>(null);
  const [scenarioId, setScenarioId] = useState<string | null>(null);
  const [zipBlob, setZipBlob] = useState<Blob | null>(null);
  const [loading, setLoading] = useState(false);

  /**
   * Runs the selected discovery approach and stores the result in local state.
   *
   * @param {string} userId - The ID of the user initiating the discovery.
   * @param {string} eventLogId - The ID of the event log to use for discovery.
   * @param {string} approach - The discovery method: 'Simod' or 'AgentSimulator'.
   * @param {string} [name] - Optional name of the discovered model or simulation.
   * @param {AgentSimulatorSettings} [agentSimulatorParameterSettings] - Optional parameters for AgentSimulator.
   * @param {SimodSimulatorSettings} [simodSimulatorParameterSettings] - Optional parameters for Simod.
   *
   * @returns {Promise<Object>} Discovery result including success flag and any result data.
   */
  const runDiscovery = async (userId: string, eventLogId: string, approach: string, name?: string,
    agentSimulatorParameterSettings?: AgentSimulatorSettings, 
    simodSimulatorParameterSettings?: SimodSimulatorSettings) => {
    setLoading(true);
    try {
      if (approach === 'Simod') {
        console.log("Starting Simod discovery");
        console.log("userId:", userId);
        console.log("eventLogId:", eventLogId);
        console.log("name:", name);

        const result = await startSimodDiscovery(userId, eventLogId, true, name, simodSimulatorParameterSettings);

        if (typeof result !== 'object' || result instanceof Blob) {
          throw new Error('Unexpected Simod result type');
        }

        setBpmnBlob(result.bpmnBlob);
        setParameters(result.parameters || null);
        setScenarioId(result.scenarioId || null);

        return {
          success: true,
          bpmnBlob: result.bpmnBlob,
          parameters: result.parameters,
          scenarioId: result.scenarioId
        };

      } else if (approach === 'AgentSimulator') {
        const { zipBlob, scenarioId } = await startAgentDiscovery(userId, eventLogId, true, name,
          agentSimulatorParameterSettings);

        if (!zipBlob) {
          throw new Error('No ZIP returned from Agent discovery');
        }

        setZipBlob(zipBlob);
        setScenarioId(scenarioId || null);

        return { success: true, zipBlob, scenarioId };
      } else {
        throw new Error('Unknown discovery approach');
      }
    } catch (error: unknown) {
      console.error('Discovery failed:', error);
      return { success: false };
    } finally {
      setLoading(false);
    }
  };

  return {
    runDiscovery,
    bpmnBlob,
    parameters,
    scenarioId,
    zipBlob,
    loading
  };
};