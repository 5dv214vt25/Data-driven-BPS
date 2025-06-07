import { useState, useEffect } from 'react';
import { TabContainer, Tab, Button, Title, Label, Select, Option, Icon, Input } from '@ui5/webcomponents-react';
import { useNavigate } from 'react-router-dom';
import BpmnDiagram from '../components/BpmnDiagram.tsx';
import EventsTab from '../components/top-panel/EventsTab';
import ResourcesTab from '../components/top-panel/ResourcesTab';
import ProbabilitiesTab from '../components/top-panel/ProbabilitiesTab';
import GeneralSimulationParamtersEditor from '../components/properties-panel/GeneralSimulationParametersEditor';
import { useUser } from '../context/userContext';
import {
  getSimodScenario,
  listSimodScenarios,
} from '../api/controllerAPICalls/SimodScenarioAPICalls';
import { SaveSimodScenarioButton } from '../components/ui/saveSimodScenarioButton.tsx';
import ContentContainer from '../components/contentContainer';

import '../assets/styles/SimConfig.css';
import { ResetScenarioButton } from '../components/ui/resetScenarioButton.tsx';
import { JsonDataSimod } from '../types/JsonDataSimod.tsx';

let externalReload: (() => void) | null = null; // For external access

export default function SimConfig() {
  const [selectedTab, setSelectedTab] = useState<string>('bpmn');
  const [bpmnFileContent, setBpmnFileContent] = useState<string>('');
  const [isEditingName, setIsEditingName] = useState(false);


  const navigate = useNavigate();

  const [scenarios, setScenarios] = useState<{
    scenario_id: number;
    scenario_name: string;
    event_log_id: number;
  }[]>([]);

  const [selectedScenario, setSelectedScenario] = useState<{
    scenario_id: number;
    scenario_name: string;
    event_log_id: number;
  } | null>(null);

  const [scenarioName, setScenarioName] = useState<string>('');
  const [tempScenarioName, setTempScenarioName] = useState('');
  const { userSettings } = useUser();
  const [reloadKey, setReloadKey] = useState(0);

  const [jsonDataSimod, setJsonDataSimod] = useState<JsonDataSimod>(() => {
    const savedData = localStorage.getItem('bpmn_json_data');
    return savedData ? JSON.parse(savedData) : ({} as JsonDataSimod);
  });
  useEffect(() => {
    localStorage.setItem('bpmn_json_data', JSON.stringify(jsonDataSimod));
  }, [jsonDataSimod]);


  // Expose reload function
  useEffect(() => {
    externalReload = () => {
      setReloadKey(k => k + 1);
      setSelectedTab('bpmn');
    };
    return () => { externalReload = null; };
  }, []);


  useEffect(() => {
    // If userSettings.selectedScenarioId is set and no scenario is selected yet
    if (
      userSettings.selectedScenarioId &&
      !selectedScenario &&
      scenarios.length > 0
    ) {
      const sel = scenarios.find(
        s => s.scenario_id.toString() === (userSettings.selectedScenarioId?.toString() ?? '')
      );
      if (sel) {
        setSelectedScenario(sel);
      }
    }
  }, [userSettings.selectedScenarioId, scenarios]);

  useEffect(() => {
    if (selectedScenario) {
      setScenarioName(selectedScenario.scenario_name);
      setTempScenarioName(selectedScenario.scenario_name);
    }
  }, [selectedScenario]);

  useEffect(() => {
    const fetchScenarios = async () => {
      if (!userSettings.username) {
        return;
      }
      try {
        const response = await listSimodScenarios(userSettings.username);
        setScenarios(response);
      } catch (error) {
        console.error('Error fetching scenarios:', error);
      }
    };
    fetchScenarios();
  }, [userSettings.username]);

  const downloadJsonData = () => {
    const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.parse(JSON.stringify(
        localStorage.getItem('bpmn_json_data'),
        null,
        2
      ))
    )}`;
    const anchor = document.createElement('a');
    anchor.href = dataStr;
    anchor.download = 'updated_event_data.json';
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
  };

  // Load scenario BPMN and params
  useEffect(() => {
    if (!selectedScenario) {
      localStorage.clear();
      return;
    }
    (async () => {
      try {
        const { bpmnBlob, parametersBlob } = await getSimodScenario(selectedScenario.scenario_id.toString());

        if (bpmnBlob && parametersBlob) {
          const bpmnText = await bpmnBlob.text();
          setBpmnFileContent(bpmnText);
          const jsonText = await parametersBlob.text();
          localStorage.setItem('bpmn_json_data', jsonText);
          setScenarioName(selectedScenario.scenario_name);
        }
      } catch (error) {
        console.error('Error loading selected scenario:', error);
      }
    })();
  }, [selectedScenario, reloadKey]);

  if (!selectedScenario) {
    return (
      <ContentContainer>
        <div className="w-full h-screen flex flex-col items-center justify-center p-6 gap-8 bg-gray-50">
          <Title level="H2">Select a Scenario</Title>
          <div className="w-full max-w-md flex flex-col gap-4">
            <Label for="scenario-select">Choose a simulation scenario:</Label>
            <Select
              id="scenario-select"
              onChange={(e) => {
                const value = e.detail.selectedOption.value;
                const sel = scenarios.find(s => s.scenario_id.toString() === value);
                if (sel) { setSelectedScenario(sel); }
              }}
            >
              <Option value="">-- Select a scenario --</Option>
              {scenarios.map(s => (
                <Option key={s.scenario_id} value={s.scenario_id.toString()}>
                  {s.scenario_name}
                </Option>
              ))}
            </Select>
          </div>
        </div>
      </ContentContainer>
    );
  }

  return (
    <div className="flex flex-col w-full" key={reloadKey}>
      <ContentContainer containerHeader={<div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {isEditingName ? (
          <>
            <Input
              value={tempScenarioName}
              onChange={(e) => setTempScenarioName(e.target.value)}
            />
            <SaveSimodScenarioButton
              scenarioId={selectedScenario.scenario_id.toString()}
              scenarioName={tempScenarioName}
              onSaveSuccess={() => {
                setScenarioName(tempScenarioName);
                setIsEditingName(false);
              }}
            />
            <Button
              design='Emphasized'
              onClick={() => {
                setTempScenarioName(scenarioName); // discard edits
                setIsEditingName(false);           // exit edit mode
              }}
            >
              Cancel
            </Button>
          </>
        ) : (
          <>
            {scenarioName}
            <Icon name="edit" onClick={() => setIsEditingName(true)} style={{ cursor: 'pointer' }} />
          </>
        )}
      </div>}>
        <div>
          <div style={{ display: "flex", gap: "0.5rem", marginLeft: "auto", marginTop: "0.5rem" }}>
            <Button
              onClick={() => setSelectedScenario(null)}>
              Select other bpn model
            </Button>

            <Button onClick={downloadJsonData}>Download Updated JSON</Button>

            <Button onClick={() => navigate('/simulation')}>
              Run Simulation
            </Button>


            {/*=================================== Custom Components ==================================*/}
            {/* <SaveSimodScenarioButton
            scenarioId={selectedScenario.scenario_id.toString()}
            scenarioName={scenarioName}
          /> */}
            <ResetScenarioButton onReset={forceSimConfigReload} />
            {/*=================================== Custom Components ==================================*/}
          </div>
        </div>
      </ContentContainer>

      <TabContainer
        className="w-full"
        tabLayout="Inline"
        onTabSelect={(e) => setSelectedTab(e.detail.tab.getAttribute('data-key') || '')}
        collapsed
      >
        <Tab text="BPMN Diagram" data-key="bpmn" />
        <Tab text="Details" data-key="details" />
        <Tab text="Events" data-key="events" />
        <Tab text="Resources" data-key="resources" />
        <Tab text="Probabilities" data-key="probabilities" />
      </TabContainer>

      <div className="p-4">
        {selectedTab === 'bpmn' && (
          <BpmnDiagram
            bpmnXml={bpmnFileContent}
            jsonData={jsonDataSimod} setJsonData={setJsonDataSimod}
            showSidePanel={true}
          />
        )}
        {selectedTab === 'events' &&
          <EventsTab
            bpmnXml={bpmnFileContent}
            jsonData={jsonDataSimod}
            setJsonData={setJsonDataSimod}
          />
        }
        {selectedTab === 'resources' &&
          <ResourcesTab
            bpmnXml={bpmnFileContent}
            jsonData={jsonDataSimod}
            setJsonData={setJsonDataSimod}
          />
        }
        {selectedTab === 'probabilities' &&
          <ProbabilitiesTab
            bpmnXml={bpmnFileContent}
            jsonData={jsonDataSimod}
            setJsonData={setJsonDataSimod}
          />
        }
        {selectedTab === 'details' &&
          <GeneralSimulationParamtersEditor
          />
        }
      </div>
    </div>
  );
}

export function forceSimConfigReload() {
  if (externalReload) {
    externalReload();
  }
}
