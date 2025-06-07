/**
 * Simod General API Calls
 * 
 * This file contains functions for interacting with the general Simod endpoints.
 * These endpoints handle Simod discovery and simulation processes.
 * 
 * Functions to implement:
 * - startSimodDiscovery: Start Simod discovery using an event log
 * - startSimodSimulation: Start Simod simulation using an event log
 */

import JSZip from 'jszip';
import { SimodSimulatorSettings } from '../../types/SimodSimulatorTypes';

/**
 * Start Simod discovery (only send parameters if user toggled a switch on)
 * 
 * @param userId - The user ID
 * @param eventLogId - The eventlog ID
 * @param saveScenario - Boolean indiciating if scenario should be saved
 * @param name - The scenario name
 * @param simodSimulatorParameterSettings - The parameters settings to use
 * 
 * @returns bpmnBlob, parameters, scenarioId
 */
export const startSimodDiscovery = async (
  userId: string,
  eventLogId: string,
  saveScenario: boolean = false,
  name?: string,
  simodSimulatorParameterSettings?: SimodSimulatorSettings
) => {
  try {
    let url = `/api/start-simod-discovery?user_id=${userId}&event_log_id=${eventLogId}`;

    if (saveScenario) {
      url += `&save_boolean=true`;
      if (name) {
        url += `&name=${encodeURIComponent(name)}`;
      }
    }

    const fetchOptions: RequestInit = { method: 'POST' };

    // Only attach a JSON payload if at least one flag is true
    if (
      simodSimulatorParameterSettings?.disableExtraneousDelays === true ||
      simodSimulatorParameterSettings?.setSplitMinerV1      === true
    ) {
      const transformed = {

        // disable_extraneous_delay: true → disable delays
        // eslint-disable-next-line
        disable_extraneous_delay: simodSimulatorParameterSettings.disableExtraneousDelays,

        // set_split_miner_v1: true → use Split Miner V1
        // eslint-disable-next-line
        set_split_miner_v1:      simodSimulatorParameterSettings.setSplitMinerV1,
      };
      const formData = new FormData();
      formData.append(
        'parameters',
        new Blob([JSON.stringify(transformed)], { type: 'application/json' }),
        'params.json'
      );
      fetchOptions.body = formData;
    }

    const response = await fetch(url, fetchOptions);
    if (!response.ok) {
      throw new Error('Simod discovery failed');
    }

    const scenarioId = response.headers.get('X-Scenario-ID');
    const zipBlob = await response.blob();

    const zip = await new JSZip().loadAsync(zipBlob);
    let bpmnBlob: Blob | null = null;
    let parameters: any = null;

    for (const [filename, file] of Object.entries(zip.files)) {
      if (filename.endsWith('.bpmn')) {
        bpmnBlob = await (file as JSZip.JSZipObject).async('blob');
      } else if (filename.endsWith('.json')) {
        const content = await (file as JSZip.JSZipObject).async('string');
        parameters = JSON.parse(content);
      }
    }

    if (!bpmnBlob || !parameters) {
      throw new Error('Missing files in the discovery result');
    }

    return { bpmnBlob, parameters, scenarioId };
  } catch (error) {
    console.error('Simod discovery error:', error);
    throw error;
  }
};

/**
 * Starts the simod simulation
 * 
 * @param userId - The user ID
 * @param scenarioId - The scenario ID
 * @param saveSimulation - Boolean indiciating if scenario should be saved
 * 
 * @returns The blob containing the response
 */
export const startSimodSimulation = async (
  userId: string,
  scenarioId: string,
  saveSimulation: boolean = false
) => {
  try {
    let url = `/api/start-simod-simulation?user_id=${userId}&scenario_id=${scenarioId}`;

    if (saveSimulation) {
      url += `&save_boolean=true`;
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Simod simulation failed');
    }

    return await response.blob();
  } catch (error) {
    console.error('Simod simulation error:', error);
    throw error;
  }
};
