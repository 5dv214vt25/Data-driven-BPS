import { useState } from 'react';
import { listAgentScenarios, uploadAgentScenario } from "../api/controllerAPICalls/AgentScenarioAPICalls";
import { listSimodScenarios, uploadSimodScenario } from '../api/controllerAPICalls/SimodScenarioAPICalls';

interface Scenario {
  scenarioId: string;
  scenarioName: string;
  eventLogId: string;
  eventLogName: string;
}

/**
 * Custom React hook to manage scenarios: fetching scenario lists and uploading new scenarios.
 *
 * @returns {Object} An object containing functions to get scenarios, upload Simod and Agent scenarios,
 *                  as well as state variables for scenario names, scenario details, and loading status.
 */
export const useScenario = () => {
  const [scenarioNames, setScenarioNames] = useState<string[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(false);

  /**
   * Fetches scenarios for a user based on the selected approach.
   *
   * @param {string} userId - The user ID.
   * @param {string} approach - The discovery approach ('Simod' or other).
   * @returns {Promise<Object>} Result object with success status and scenario names.
   */
  const runGetScenarios = async (userId: string, approach: string) => {
    setLoading(true);
    try {
      const jsonResponse = approach === 'Simod'
        ? await listSimodScenarios(userId)
        : await listAgentScenarios(userId);

      /* Return empty data */
      if (!jsonResponse || jsonResponse.length === 0) {
        console.error('No scenarios found');
        setScenarioNames([]);
        setScenarios([]);
        return { success: true, names: [] };
      }

      if (approach === 'Simod') {
        const scenarios = jsonResponse.map((item: any) => ({
          scenarioId: item.scenario_id,
          scenarioName: item.scenario_name,
          eventLogId: item.event_log_id,
          eventLogName: item.event_log_name,
        }));
        setScenarios(scenarios);
        console.log('Scenarios in useScenario:', scenarios);
      } else {
        const scenarios = jsonResponse.map((item: any) => ({
          scenarioId: item.id,
          eventLogId: item.event_log_id,
          scenarioName: item.name,
        }));
        setScenarios(scenarios);
        console.log('Scenarios in useScenario:', scenarios);
      }

      let names: string[] = [];
      if (approach === 'Simod') {
        names = jsonResponse.map((item: any) => item.scenario_name);}
      else {
        names = jsonResponse.map((item: any) => item.name);
      }
      setScenarioNames(names);

      return { success: true, names };
    } catch (error) {
      console.error('Get scenario names failed:', error);
      return { success: false, scenarioNames: null };
    } finally {
      setLoading(false);
    }
  };


  /**
   * Uploads a Simod scenario.
   *
   * @param {string} userId - The user ID.
   * @param {Object} data - The scenario data including files.
   * @returns {Promise<Object>} Result object with success status and optional response.
   */
  const runUploadSimodScenario  = async (
    userId: string,
    data: {
      eventLogId: string;
      name: string;
      fileBpmn: File;
      paramJson: File;
    }
  ) => {
    try {
      const response = await uploadSimodScenario(userId, data.name, data.fileBpmn, data.paramJson);
      return { success: true, response };
    } catch (error) {
      console.error('Upload scenario failed:', error);
      return { success: false };
    }
  };

  /**
   * Uploads an AgentSimulator scenario.
   *
   * @param {string} eventLogId - Event log ID.
   * @param {string} name - Scenario name.
   * @param {File} modelPkl - Model pickle file.
   * @param {File} paramJson - Parameter JSON file.
   * @param {File} visualizationJson - Visualization JSON file.
   * @returns {Promise<Object>} Result object with success status and optional scenario ID.
   */
  const runUploadAgentScenario = async (
    eventLogId: string,
    name: string,
    modelPkl: File,
    paramJson: File,
    visualizationJson: File
  ) => {
    try {
      const { success, scenarioId } = await uploadAgentScenario(
        eventLogId,
        name,
        modelPkl,
        paramJson,
        visualizationJson
      );

      if (success) {
        return { success: true, scenarioId };
      } else {
        return { success: false };
      }
    } catch (error) {
      console.error('Upload Agent scenario failed:', error);
      return { success: false };
    }
  };

  return { runGetScenarios, runUploadSimodScenario, runUploadAgentScenario, scenarioNames, scenarios, loading };
};