import { useState, useEffect } from 'react';
import { Label, Switch, FlexBox } from '@ui5/webcomponents-react';
import { Loader } from '@ui5/webcomponents-react-compat/dist/components/Loader/index.js';
import JSZip from 'jszip';
import { PopupMessage } from '../components/PopupMessage';
import BpmnDiagram from '../components/BpmnDiagram';
import { useScenario } from '../hooks/useScenario';
import { useDiscovery } from '../hooks/useDiscovery';
import { usePopup } from '../hooks/usePopup';
import { useUser } from '../context/userContext';
import { useEventLogs } from '../hooks/useEventLogs';
import { AgentSimulatorSettings } from '../types/AgentSimulatorTypes';
import { SimodSimulatorSettings } from '../types/SimodSimulatorTypes';

import ContentContainer from '../components/contentContainer';
import DiscoveryController from '../components/discoveryController';
import AgentSimulatorNetwork from '../components/agentSimulatorNetwork.tsx';

import '../assets/styles/Discovery.css';
import '../assets/styles/Topdivbutton.css';

/**
 * @function Discovery
 * @description This page is used for the discovery process of the simulation. 
 * It allows the user to select an uploaded event log, select a discovery approach 
 * (Simod or AgentSimulator), and start the discovery process.
 * After the discovery process is completed, the user can save the scenario and 
 * see a preview of the generated diagram.
 * @returns Discovery component
 */
function Discovery() {
  // Local state for agent simulation network data
  const [jsonDataAgentSim, setJsonDataAgentSim] = useState<any>(null);
  const [mode, setMode] = useState<'agent' | 'role' | 'activity'>('agent');
  const [topEdgeCount, setTopEdgeCount] = useState<number | 'all'>(1);

  // User and event log context
  const { userSettings } = useUser();
  const { eventLogs, loadEventLogs } = useEventLogs();

  // Discovery approach state
  const [selectedApproach, setSelectedApproach] = useState<string>('AgentSimulator');
  const [enableSaveScenario, setEnableSaveScenario] = useState<boolean>(false);
  const [bpmnBlob, setBpmnBlob] = useState<Blob | null>(null);
  const [bpmnFileContent, setBpmnFileContent] = useState<string>('');

  // Hooks for API calls and popup messages
  const { runGetScenarios } = useScenario();
  const { runDiscovery, loading: discoveryLoading } = useDiscovery({ bpmnBlob, setBpmnBlob });
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  // ----------------------------------------
  // AgentSimulator start-discovery parameters:
  // ----------------------------------------
  const [agentDiscoverySettings, setAgentDiscoverySettings] = useState<AgentSimulatorSettings>({
    extraneousDelays: false,
    centralOrchestration: false,
    determineAutomatically: false,
  });
  const toggleAgentDiscoverySetting = (key: keyof AgentSimulatorSettings) => {
    setAgentDiscoverySettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  useEffect(() => {
    if (!bpmnBlob) { return; }
    if (!bpmnBlob) { return; }

    const readBlob = async () => {
      const bpmnText = await bpmnBlob.text();
      setBpmnFileContent(bpmnText);
    };

    readBlob();
  }, [bpmnBlob]);

  // ----------------------------------------
  // Simod start-discovery parameters:
  // ----------------------------------------
  const [simodDiscoverySettings, setSimodDiscoverySettings] = useState<SimodSimulatorSettings>({
    disableExtraneousDelays: false,
    setSplitMinerV1: false,
  });
  const toggleSimodDiscoverySetting = (key: keyof SimodSimulatorSettings) => {
    setSimodDiscoverySettings(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // Load event logs on mount
  useEffect(() => {
    if (userSettings.username) {
      loadEventLogs(userSettings.username);
    }
  }, [userSettings.username]);

  /**
   * @function updateUserSettings
   * @description Updates context with the selected scenario and approach
   */
  const updateUserSettings = (scenarioId: string | null | undefined, approach: string) => {
    if (!scenarioId) {
      console.error('No scenarioId to update');
      return;
    }
    userSettings.selectedScenarioId = scenarioId;
    userSettings.selectedApproach = approach === 'AgentSimulator' ? 'Agent' : 'Simod';
  };

  /**
   * @function simulateAgent
   * @description Extracts and sets the AgentSimulator visualization data from ZIP
   */
  const simulateAgent = async (zipBlob: Blob) => {
    const arrayBuffer = await zipBlob.arrayBuffer();
    const zip = await JSZip.loadAsync(arrayBuffer);
    const vizFile = zip.file('visualization.json');
    const paramFile = zip.file('params.json');

    if (!vizFile || !paramFile) {
      showPopup('error', 'Missing visualization or parameters in ZIP');
      return;
    }

    const parsedVis = JSON.parse(await vizFile.async('string'));
    setJsonDataAgentSim(parsedVis);
  };

  /**
   * @function setScenarioName
   * @description Builds a unique scenario name based on the uploaded event log
   */
  const setScenarioName = async (logId: string, approach: string) => {
    const { names } = await runGetScenarios(userSettings.username, approach);
    // Find the event log by ID and extract the base filename (without extension)
    const eventLog = eventLogs.find(log => String(log.event_log_id) === String(logId));
    const baseName = eventLog?.filename.replace(/\.[^/.]+$/, '') || 'Scenario';
    let scenarioName = `${baseName} Scenario`;
    const existing = names ?? [];
    let counter = 1;
    while (existing.includes(scenarioName)) {
      scenarioName = `${baseName} (Scenario ${counter++})`;
    }
    return scenarioName;
  };

  /**
   * @function handleDiscovery
   * @description Coordinates both Simod and AgentSimulator discovery flows
   */
  const handleDiscovery = async (logId: string | null, approach: string) => {
    // Reset state
    setJsonDataAgentSim(null);
    setTopEdgeCount(1);
    setBpmnBlob(null);
    setSelectedApproach(approach);

    if (!logId) {
      showPopup('error', 'Please select an event log');
      return;
    }

    // Generate a unique scenario name
    const scenarioName = await setScenarioName(logId, approach);

    // Run the discovery hook (handles both approaches)
    const result = await runDiscovery(
      userSettings.username,
      logId,
      approach,
      scenarioName,
      agentDiscoverySettings,
      simodDiscoverySettings
    );

    if (result.success) {
      showPopup('success', `${approach} Discovery completed successfully!`);
      updateUserSettings(result.scenarioId, approach);
      setEnableSaveScenario(true);

      if (approach === 'AgentSimulator' && result.zipBlob) {
        simulateAgent(result.zipBlob);
      }
      // Simod case: `bpmnBlob` is already set by the hook via `setBpmnBlob`
    } else {
      showPopup('error', `${approach} Discovery failed`);
    }
  };

  return (
    <>
      <ContentContainer containerHeader='Discovery'>
        <DiscoveryController
          handleDiscovery={handleDiscovery}
          buttonEnableSaveScenario={enableSaveScenario}
          isLoading={discoveryLoading}
          selectedApproach={selectedApproach}
          setSelectedApproach={setSelectedApproach}
        />

        {/* Simod configuration switches */}
        {selectedApproach === 'Simod' && (
          <FlexBox className='flex-box' alignItems='Center' gap='1em'>
            <label htmlFor='extraneousDelays' style={discoveryLoading ? { color: 'gray' } : {}}
            >Extraneous Delays:</label>
            <Switch
              id='disableExtraneousDelays'
              design='Textual'
              disabled={discoveryLoading}
              checked={!simodDiscoverySettings.disableExtraneousDelays}
              onChange={() => toggleSimodDiscoverySetting('disableExtraneousDelays')}
            />
            <label htmlFor='setSplitMinerV1' style={discoveryLoading ? { color: 'gray' } : {}}
            >Use Split Miner V1 (Default is V2):</label>
            <Switch
              id='setSplitMinerV1'
              design='Textual'
              disabled={discoveryLoading}
              checked={simodDiscoverySettings.setSplitMinerV1}
              onChange={() => toggleSimodDiscoverySetting('setSplitMinerV1')}
            />
          </FlexBox>
        )}

        {/* AgentSimulator configuration switches */}
        {selectedApproach === 'AgentSimulator' && (
          <FlexBox className='flex-box' alignItems='Center' gap='1em'>
            <label htmlFor='extraneousDelays' style={discoveryLoading ? { color: 'gray' } : {}}
            >Extraneous Delays:</label>

            <Switch
              id='extraneousDelays'
              design='Textual'
              disabled={discoveryLoading}
              onChange={() => toggleAgentDiscoverySetting('extraneousDelays')}
            />
            
          </FlexBox>
        )}
        {/* Render network or BPMN diagram */}
        <div style={{ width: '100%' }}>
          {selectedApproach === 'AgentSimulator' && jsonDataAgentSim && (
            <div>
              <AgentSimulatorNetwork
                jsonDataAgentSim={jsonDataAgentSim}
                topEdgeCount={topEdgeCount}
                mode={mode}
                setMode={setMode}
                setTopEdgeCount={setTopEdgeCount}
              />
            </div>
          )}

          {selectedApproach !== 'AgentSimulator' && bpmnBlob && (
            <div className="bpmn-container">
              <h2>Scenario preview</h2>
              <BpmnDiagram bpmnXml={bpmnFileContent} showSidePanel={false} />
            </div>
          )}

          {(discoveryLoading) && (
            <div className="loading-container">
              <Label>{selectedApproach} Running...</Label>
              <Loader
                progress="60%"
                type="Indeterminate"
                style={{ width: '400px', height: '10px' }} />
            </div>
          )}

        </div>

        {/* Popup for messages */}
        <PopupMessage
          show={!!popupMessage}
          type={popupType}
          message={popupMessage}
          duration={4000}
          onClose={closePopup}
        />
      </ContentContainer>
    </>
  );
}

export default Discovery;
