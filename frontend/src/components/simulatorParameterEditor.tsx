import { useState, useEffect } from 'react';
import { useImperativeHandle, forwardRef } from 'react';
import { useUser } from '../context/userContext';
import { TabContainer, Tab, Label, Input, DateTimePicker } from '@ui5/webcomponents-react';
import BpmnDiagram from './BpmnDiagram.tsx';
import EventsTab from '../components/top-panel/EventsTab';
import ResourcesTab from '../components/top-panel/ResourcesTab';
import FormComponent from '../components/form-component/FormComponent';
import { State } from '../components/form-component/types';
import ProbabilitiesTab from '../components/top-panel/ProbabilitiesTab';
import GeneralSimulationParamtersEditor from '../components/properties-panel/GeneralSimulationParametersEditor';
import { getSimodScenario } from '../api/controllerAPICalls/SimodScenarioAPICalls';
import { getAgentScenario } from '../api/controllerAPICalls/AgentScenarioAPICalls';
import { updateAgentParameters } from '../api/controllerAPICalls/AgentGeneralAPICalls';

import AgentSimulatorNetwork from '../components/agentSimulatorNetwork.tsx';

import '../assets/styles/SimConfig.css';
import { JsonDataSimod } from '../types/JsonDataSimod.tsx';

type Scenario = {
  scenarioId: string;
  scenarioName: string;
  scenarioType: 'Simod' | 'Agent';
};

interface Props {
  scenario: Scenario | null;
  isParaChange?: (isEditing: boolean) => void;
}

let externalReload: (() => void) | null = null; // For external access
export type SimulatorParameterEditorHandle = {
  sendParameters: () => Promise<void>;
};


/**
 * Displays the parameter editor view in the Simulation page
 */

const SimulatorParameterEditor = forwardRef<SimulatorParameterEditorHandle, Props>(
  ({ scenario, isParaChange }, ref) => {
    // The graph data for Simod
    const [bpmnFileContent, setBpmnFileContent] = useState<string>('');
    const [selectedTab, setSelectedTab] = useState<string>('bpmn');
    // The mode for the AgentSimulator NetworkGraph
    const [mode, setMode] = useState<'agent' | 'role' | 'activity'>('agent');
    const [diffs, setDiffs] = useState<{ [label: string]: Partial<State> }>({});
    const [label, setLabel] = useState("");
    // Graph data for agentsimulator NetworkGraph
    const [jsonDataAgentSim, setJsonDataAgentSim] = useState<any>(null);
    // Data for the agentsimulator parameters
    const [simParamAgentSim, setSimParamAgentSim] = useState<any>(null);
    // The amount of edges to filter from the NetworkGraph
    const [topEdgeCount, setTopEdgeCount] = useState<number | 'all'>(1);
    const [reloadKey, setReloadKey] = useState(0);
    const [formStates, setFormStates] = useState<{ [label: string]: State }>({});
    const [numSimulations, setNumSimulations] = useState<number>(1);
    const [numCases, setNumCases] = useState<any>(null);
    const [agentSimStartTime, setStartTime] = useState<any>(null);
    const { userSettings } = useUser();

    const [jsonDataSimod, setJsonDataSimod] = useState<JsonDataSimod>(() => {
      const savedData = localStorage.getItem('bpmn_json_data');
      if (savedData && savedData !== "undefined") {
        try {
          return JSON.parse(savedData);
        } catch (e) {
          console.error("Failed to parse localStorage data", e);
          return ({} as JsonDataSimod);
        }
      }
      return ({} as JsonDataSimod);
    });
    useEffect(() => {
      localStorage.setItem('bpmn_json_data', JSON.stringify(jsonDataSimod));
    }, [jsonDataSimod]);

    const handleChange = (label: string, changes: Partial<State>) => {
      setDiffs((prev) => ({
        ...prev,
        [label]: {
          ...prev[label],
          ...changes
        }
      }));
      console.log("diffs: " + diffs)
    };

    function toSnakeCase(obj: any): any {
      if (Array.isArray(obj)) {
        return obj.map(toSnakeCase);
      } else if (obj !== null && typeof obj === 'object') {
        return Object.fromEntries(
          Object.entries(obj).map(([key, value]) => [
            key.replace(/([A-Z])/g, "_$1").toLowerCase(),
            toSnakeCase(value),
          ])
        );
      }
      return obj;
    }

    function getAllActivities() {
      const activityNodesStr = jsonDataAgentSim.activity_nodes;
      const activityNodes = JSON.parse(activityNodesStr);
      const activities = activityNodes.map((node: any) => node.label);
      return activities;
    }

    function getAllAgents() {
      const agentNodesStr = jsonDataAgentSim.agent_nodes;
      const agentNodes = JSON.parse(agentNodesStr);
      const agents = agentNodes.map((node: any) => node.label);
      return agents;
    }

    function getAgentId(label: string): string {
      const agentMap = simParamAgentSim.simulation_parameters.agent_to_resource;
      const agentID = Object.entries(agentMap).find(([, v]) => v === label)?.[0];
      if (!agentID) { throw new Error("agentID is undefined"); }
      return agentID
    }


    function addAgentToRole(agentId: string, role: string, dataToSend: any) {
      if (!dataToSend.params.roles) {
        dataToSend.params.roles = {};
      }

      if (!dataToSend.params.roles[role]) {
        dataToSend.params.roles[role] = {};
      }

      if (!dataToSend.params.roles[role].agents) {
        dataToSend.params.roles[role].agents = [];
      }

      if (!dataToSend.params.roles[role].agents.includes(agentId)) {
        dataToSend.params.roles[role].agents.push(agentId);
      }

      return dataToSend;
    }


    function simplifyCalendar(agentId: number, calendarData: any): any {
      const groupedByDay: { [key: string]: [string, string][] } = {};

      for (const period of calendarData) {
        const day = period.from; // Vi antar from = to
        if (!groupedByDay[day]) {
          groupedByDay[day] = [];
        }
        groupedByDay[day].push([period.beginTime, period.endTime]);
      }

      const dayOrder = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"];
      const days = dayOrder.filter(day => groupedByDay[day]);

      const schedule = days.map(day => groupedByDay[day]);

      return {
        agent_id: agentId.toString(), // eslint-disable-line camelcase
        days: days,
        schedule: schedule
      };
    }

    // Parses the form and creates an object (dataToSend) that later is converted to JSON for posting the changes
    function parseFormState(roles: string[], activities: string[], agents: string[], dataToSend: any): any {
      let numberOfAgents = 0;
      for (const label in formStates) {
        if (roles.includes(label)) {

          if (!dataToSend.params.roles) {
            dataToSend.params.roles = {};
          }
          dataToSend.params.roles[label] = {};
          dataToSend.params.roles[label].calendar = formStates[label].calendar

        } else if (agents.includes(label)) {
          const agentId = getAgentId(label)
          const role = typeof formStates[label].role === 'string' ? formStates[label].role : '';


          if (!dataToSend.params.agentActivityMapping) {
            dataToSend.params.agentActivityMapping = {};
          }
          if (!dataToSend.params.activityDurationsDict) {
            dataToSend.params.activityDurationsDict = {};
          }
          if (!dataToSend.params.resCalendars) {
            dataToSend.params.resCalendars = []
          }
          if (!dataToSend.params.new_resource_name) {
            dataToSend.params.newResourceName = {}
          }

          addAgentToRole(agentId, role, dataToSend);
          dataToSend.params.resCalendars.push(simplifyCalendar(Number(agentId), formStates[label].calendar))

          numberOfAgents++;
        } else if (activities.includes(label)) {
          if (!dataToSend.params.maxActivityCountPerCase) {
            dataToSend.params.maxActivityCountPerCase = {};
          }

          dataToSend.params.maxActivityCountPerCase = formStates[label].max_activity_count_per_case;

        } else {
          console.error(label + " was not found as a role, agent or activity")
        }
      }


      return dataToSend;
    }



    function getAllRoles() {
      const roleNodesStr = jsonDataAgentSim.role_nodes;
      const roleNodes = JSON.parse(roleNodesStr);
      const roles = roleNodes.map((node: any) => node.label);
      return roles;
    }

    // Sends the updated parameters
    async function sendParameters() {
      const roles = getAllRoles();
      const activities = getAllActivities();
      const agents = getAllAgents();
      const numberOfSimulations = numSimulations;
      const numberOfCases = numCases;
      /*NEEDS TO BE CORRECT FORMAT (yyyy-MM-dd HH:mm:ss+HH+mm)*/
      var startTime = agentSimStartTime.replace("T", " ").replace(",", "");
      if (!startTime.includes("+")) {
        startTime = startTime + "+00:00"
      }

      let dataToSend: any = {
        params: {
          numSimulations: numberOfSimulations,
          newNumCasesToSimulate: Number(numberOfCases),
          startTimestamp: startTime
        },
      };

      dataToSend = parseFormState(roles, activities, agents, dataToSend);
      dataToSend = toSnakeCase(dataToSend);

      const jsonFile = new File([JSON.stringify(dataToSend)], "params.json", {
        type: "application/json",
      });

      const userId = userSettings.username
      const scenarioId = userSettings.selectedScenarioId;
      if (scenarioId === null) { throw new Error("Missing scenarioId"); }


      try {
        const currentDate = new Date()
        var cleanScenario: string = scenario!.scenarioName
        if (cleanScenario.includes(" ( ")) {
          cleanScenario = cleanScenario.split(" (")[0].trim();
        }
        const response = await updateAgentParameters(
          userId,
          scenarioId,
          jsonFile,
          cleanScenario + " ( " + currentDate.toLocaleString("en-GB") + " ) "
        )

        if (!response) {
          throw new Error(`Server returned bad response`);
        } else {
          console.log("New scenarioID: " + response.scenarioId)
        }

      } catch (error) {
        console.error("Failed to send parameters:", error);
      }
    }

    useImperativeHandle(ref, () => ({
      sendParameters,
    }));

    // Expose reload function
    useEffect(() => {
      externalReload = () => {
        setReloadKey(k => k + 1);
        setBpmnFileContent('');
        setJsonDataSimod({});
        setJsonDataAgentSim(null);
        setSimParamAgentSim(null);
        setTopEdgeCount(1);
        setSelectedTab('bpmn');
      };
      return () => { externalReload = null; };
    }, []);

    // Load scenario Visualization and Parameters FOR SIMOD!
    useEffect(() => {
      if (!scenario || scenario.scenarioType !== 'Simod') {
        return;
      }
      (async () => {
        try {
          const { bpmnBlob, parametersBlob } = await getSimodScenario(scenario.scenarioId.toString());

          if (bpmnBlob && parametersBlob) {
            const bpmnText = await bpmnBlob.text();
            setBpmnFileContent(bpmnText);
            localStorage.setItem('bpmn_data', bpmnText);
            const jsonText = await parametersBlob.text();
            setJsonDataSimod(JSON.parse(jsonText));
            localStorage.setItem('bpmn_json_data', jsonText);
          }
        } catch (error) {
          console.error('Error loading selected scenario:', error);
        }
      })();
    }, [scenario, reloadKey]);

    // Load scenario Visualization and Paramters FOR AGENT!
    useEffect(() => {
      if (!scenario || scenario.scenarioType === 'Simod') {
        return;
      }
      (async () => {
        try {
          const { visualizationBlob, parametersBlob } = await getAgentScenario(scenario.scenarioId.toString());

          if (visualizationBlob && parametersBlob) {
            // Visualization
            const visualizationText = await visualizationBlob.text();
            const parsedVisualization = JSON.parse(visualizationText);
            setJsonDataAgentSim(parsedVisualization);
            // Parameters
            const simParamText = await parametersBlob.text();
            let parsedSimParam = JSON.parse(simParamText);
            setSimParamAgentSim(parsedSimParam);
            setNumSimulations(parsedSimParam.params.num_simulations)
            setStartTime(parsedSimParam.simulation_parameters.start_timestamp);
            setNumCases(parsedSimParam.num_cases_to_simulate);
          }
        } catch (error) {
          console.error('Error loading selected scenario:', error);
        }
      })();
    }, [scenario, reloadKey]);

    useEffect(() => {
      if (scenario && scenario.scenarioType === 'Agent') {
        setFormStates({});
        setLabel('');
      }
    }, [scenario]);

    // Check if we got a scenario
    if (!scenario) {
      return <p>No scenario selected.</p>;
    }

    return (
      <div className="flex flex-col w-full" key={reloadKey}>
        <TabContainer
          className="w-full"
          tabLayout="Inline"
          onTabSelect={(e) => setSelectedTab(e.detail.tab.getAttribute('data-key') || '')}
          collapsed
        >
          <Tab text="Diagram" data-key="bpmn" />
          <Tab text="Details" data-key="details" />
          <Tab text="Events" data-key="events" disabled={!jsonDataSimod.task_resource_distribution
            || jsonDataSimod.task_resource_distribution.length === 0} />
          <Tab text="Resources" data-key="resources" disabled={!jsonDataSimod.resource_profiles
            || jsonDataSimod.resource_profiles.length === 0} />
          {scenario.scenarioType === 'Simod' && (<Tab text="Probabilities" data-key="probabilities" />)}
        </TabContainer>

        <div className="p-4">
          { /**Simod Visualization Graph */}
          {selectedTab === 'bpmn' && scenario.scenarioType === 'Simod' && (
            <BpmnDiagram bpmnXml={bpmnFileContent} jsonData={jsonDataSimod} setJsonData={setJsonDataSimod}
              showSidePanel={true} />
          )}
          { /**Agent Visualization Graph */}
          {simParamAgentSim && selectedTab === 'bpmn' && scenario.scenarioType === 'Agent' && (
            <div style={{ marginTop: '40px' }}>
              <div style={{ display: 'flex' }}>
                <AgentSimulatorNetwork
                  jsonDataAgentSim={jsonDataAgentSim}
                  topEdgeCount={topEdgeCount}
                  setTopEdgeCount={setTopEdgeCount}
                  mode={mode}
                  setMode={setMode}
                  onLabelChange={setLabel}
                />
                <FormComponent
                  mode={mode}
                  label={label}
                  data={simParamAgentSim}
                  formState={formStates[label]}
                  setFormState={(label, newState) => {
                    setFormStates(prev => ({
                      ...prev,
                      [label]: newState
                    }));
                  }}
                  onChange={handleChange}
                />
              </div>
            </div>
          )}
          {
            selectedTab === 'events' &&
            <EventsTab
              bpmnXml={bpmnFileContent}
              onParaChange={isParaChange}
              jsonData={jsonDataSimod}
              setJsonData={setJsonDataSimod}
            />
          }
          {
            selectedTab === 'resources' &&
            <ResourcesTab bpmnXml={bpmnFileContent}
              onParaChange={isParaChange}
              jsonData={jsonDataSimod}
              setJsonData={setJsonDataSimod}
            />
          }
          {
            selectedTab === 'probabilities' && scenario.scenarioType === 'Simod' &&
            <ProbabilitiesTab
              bpmnXml={bpmnFileContent}
              onParaChange={isParaChange}
              jsonData={jsonDataSimod}
              setJsonData={setJsonDataSimod}
            />
          }
          {selectedTab === 'details' && scenario.scenarioType === 'Simod' && <GeneralSimulationParamtersEditor />}
          {selectedTab === 'details' && scenario.scenarioType === 'Agent' && (
            <div style={{
              marginTop: '20px', display: 'flex', flexDirection: 'column',
              padding: '20px', width: '20%', gap: '10px'
            }}>
              <Label>Number of simulations:</Label>
              <Input
                value={numSimulations !== null ? String(numSimulations) : '1'}
                style={{ width: '100%' }}
                onChange={(e) => setNumSimulations(Number(e.target.value))}>
              </Input>
              <Label>Number of cases to simulate:</Label>
              <Input
                value={numCases !== null ? String(numCases) : ''}
                style={{ width: '100%' }}
                onChange={(e) => setNumCases(e.target.value)}>
              </Input>
              <Label>Start time (yyyy-MM-dd HH:mm:ss+hh:mm):</Label>
              <DateTimePicker
                placeholder={agentSimStartTime ?? '2026-01-01 08:00:00+00:00'}
                onChange={(e) => setStartTime(e.target.value)}
                formatPattern="yyyy-MM-dd, HH:mm:ss"
                style={{ width: '100%' }}
              />
            </div>
          )}
        </div >
      </div >
    );
  });

export function forceSimulatorParameterEditorReload() {
  if (externalReload) {
    externalReload();
  }
}

export default SimulatorParameterEditor;
