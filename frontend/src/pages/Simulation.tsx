import { useRef, useState, useEffect } from 'react';
import { Button, Label } from '@ui5/webcomponents-react';
import { Loader } from '@ui5/webcomponents-react-compat/dist/components/Loader/index.js';
import { usePopup } from '../hooks/usePopup';
import { useUser } from '../context/userContext';
import { fetchSimodOutput } from '../api/controllerAPICalls/SimodOutputAPICalls';
import { startSimodSimulation } from '../api/controllerAPICalls/SimodGeneralAPICalls';
import { startAgentSimulation } from '../api/controllerAPICalls/AgentGeneralAPICalls';
import { fetchAgentOutput } from '../api/controllerAPICalls/AgentOutputAPICalls';
import { PopupMessage } from '../components/PopupMessage';
import ContentContainer from '../components/contentContainer';
import ScenarioList from '../components/simulation/ScenarioList';
import SimulatorParameterEditor, {
  SimulatorParameterEditorHandle,
  forceSimulatorParameterEditorReload
} from '../components/simulatorParameterEditor';
import { SaveSimodScenarioButton } from '../components/ui/saveSimodScenarioButton';
import { DuplicateSimodScenarioButton } from '../components/ui/duplicateSimodScenarioButton';
import { ResetScenarioButton } from '../components/ui/resetScenarioButton';

import '../assets/styles/simulation.css';

/**
 * @function Simulation
 * @description This page is used for running simulation.
 * This page contain senarios table where the users can select to edit name, duplicate, delete or run simulation.
 * Moreover, it include parameter editing and output download.
 * It supports both Simod and Agent simulations.
 *
 * @component
 */
function Simulation() {
  // These will be set by ScenarioList
  const [selectedScenario, setSelectedScenario] = useState<{
    scenarioId: string;
    scenarioName: string;
    scenarioType: 'Simod' | 'Agent';
  } | null>(null);

  const [simulationLoading, setSimulationLoading] = useState<boolean>(false);
  const [outputAvailable, setOutputAvailable] = useState(true);
  const { userSettings } = useUser();
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();
  const [isEditing, setIsEditing] = useState(false);

  const parameterEditorRef = useRef<SimulatorParameterEditorHandle>(null);
  const [scenarioReloadKey, setScenarioReloadKey] = useState(0);


  // Check if output exists for the selected scenario
  useEffect(() => {
    const checkOutput = async () => {
      if (!selectedScenario) {
        setOutputAvailable(false);
        return;
      }
      const exists = await checkIfOutputExists(selectedScenario.scenarioId, selectedScenario.scenarioType);
      setOutputAvailable(exists);
    };
    checkOutput();
  }, [selectedScenario]);

  /**
   * Checks if output exists for the selected scenario.
   * 
   * @param {string} scenarioId  The ID of the scenario.
   * @param {'Simod' | 'Agent'} scenarioType  The type of the simulation to be checked.
   * @returns {Promise<boolean>} True if output exists, false otherwise.
   */
  const checkIfOutputExists = async (scenarioId: string, scenarioType: 'Simod' | 'Agent'): Promise<boolean> => {
    try {
      let response;
      if (scenarioType === 'Simod') {
        response = await fetchSimodOutput(Number(scenarioId));
      } else {
        response = await fetchAgentOutput(Number(scenarioId));
      }

      /* If the response size is empty so there are no output */
      if (response.size === 0) {
        return false;
      }

      return !!response;
    } catch (error) {
      console.error('Error checking output:', error);
      return false;
    }
  };

  /**
   * Starts the simulation for the selected scenario.
   * Handles both Simod and Agent simulation.
   */
  const handleSimulation = async () => {
    setSimulationLoading(true);

    if (!selectedScenario) {
      return;
    }
    try {
      let blob = null;
      if (selectedScenario.scenarioType === 'Simod') {
        blob = await startSimodSimulation(userSettings.username, selectedScenario.scenarioId, true);
      } else {
        blob = await startAgentSimulation(userSettings.username, selectedScenario.scenarioId, true);
      }
      if (!blob) {
        console.log("No blob")
      }
      // Optionally use blob
      const exists = await checkIfOutputExists(selectedScenario.scenarioId, selectedScenario.scenarioType);
      setOutputAvailable(exists);
      showPopup('success', `Simulation completed`);
      setSimulationLoading(false);
    } catch (error: unknown) {
      showPopup('error', `Simulation failed.`);
    }
  };

  /**
   * Downnloads the output file for the siumation,
   * Handles both Simod and Agent simulation.
   * @returns 
   */
  const handleDownload = async () => {
    if (!selectedScenario) {
      showPopup('error', 'No scenario selected');
      return;
    }
    try {
      let blob;
      if (selectedScenario.scenarioType === 'Simod') {
        blob = await fetchSimodOutput(Number(selectedScenario.scenarioId));
      } else {
        blob = await fetchAgentOutput(Number(selectedScenario.scenarioId));
      }
      if (!blob) {
        showPopup('error', 'No data available for download');
        return;
      }
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      if (selectedScenario.scenarioType === 'Simod') {
        link.download = `simod_output_${timestamp}.csv`;
      } else {
        link.download = `agent_output_${timestamp}.zip`;
      }
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      showPopup('success', 'File downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      showPopup('error', 'Failed to download file');
    }
  };

  /**
   * Handles scenario selection from the ScenarioList.
   * Warns user if there are unsaved changes.
   * Resets parameter editor if needed.
   * 
   * @param {Object|null} scenario  The selected scenario object or null.
   * @param {string} scenario.scenarioId  The scenario ID.
   * @param {string} scenario.name  The scenario name.
   * @param {'Simod' | 'Agent'} scenario.scenarioType  The simulation to be run.
   */
  const handleScenarioSelect = (scenario: {
    scenarioId: string;
    name: string;
    scenarioType: 'Simod' | 'Agent';
  } | null) => {

    /* Give a warning if the user edited parameter and did not save */
    if (isEditing) {
      let str = 'You have unsaved changes. Do you want to discard them and switch scenarios?';
      const confirmLeave = window.confirm(str);
      if (!confirmLeave) {
        return;
      }
    }

    if (scenario && scenario.scenarioType === 'Agent') {
      localStorage.removeItem('bpmn_json_data');
    }

    if (!scenario) {
      setSelectedScenario(null);
    } else {
      setSelectedScenario({
        scenarioId: scenario.scenarioId,
        scenarioName: scenario.name,
        scenarioType: scenario.scenarioType,
      });
    }

    setIsEditing(false);
    forceSimulatorParameterEditorReload();
  };

  /**
   * Renders the correct Save/Duplicate button based on the selected scenario simulation and state.
   * For Simod:
   * - Show Save button if no output exists
   * - Show Duplicate button if output exists
   * For Agent:
   * - Always show Save button that sends parameters
   * @returns {JSX.Element|null} A button element or null if no scenario is selected.
   */
  function renderSaveButton() {
    if (!selectedScenario) {
      return (
        <Button
          design="Emphasized"
        >
          Save Scenario
        </Button>
      );
    }

    const { scenarioType, scenarioName, scenarioId } = selectedScenario;

    if (scenarioType === "Simod") {
      const currentDate = new Date()
      var cleanScenario: string = scenarioName
      if (cleanScenario.includes(" ( ")) {
        cleanScenario = cleanScenario.split(" (")[0].trim();
      }

      if (!outputAvailable) {
        return (
          <SaveSimodScenarioButton
            scenarioName={scenarioName || ""}
            scenarioId={scenarioId || null}
            onSaveSuccess={() => {
              forceSimulatorParameterEditorReload();
              setIsEditing(false);
            }}
          />
        );
      } else {
        return (
          <DuplicateSimodScenarioButton
            scenarioName={cleanScenario + " ( " + currentDate.toLocaleString("en-GB") + " ) "}
            eventLogId={userSettings.selectedEventlogId}
            onSaveSuccess={() => {
              forceSimulatorParameterEditorReload();
              setIsEditing(false);
              setScenarioReloadKey(k => k + 1);
            }}
          />
        );
      }
    }

    if (scenarioType === "Agent") {
      return (
        <Button
          design="Emphasized"
          onClick={async () => {
            await parameterEditorRef.current?.sendParameters()
            forceSimulatorParameterEditorReload();
            console.log('reloading ScenarioList parent')
            setScenarioReloadKey(k => k + 1);
          }}
        >
          Save Scenario
        </Button>
      );
    }

    return null;
  }

  return (
    <>
      <ContentContainer containerHeader='Simulation'>
        <div className="scenario-table-wrapper">
          <ScenarioList
            onScenarioSelect={handleScenarioSelect}
            selectedScenarioId={selectedScenario?.scenarioId || null}
            selectedScenarioType={selectedScenario?.scenarioType || null}
            onStartSimulation={handleSimulation}
            onDownload={handleDownload}
            outputAvailable={outputAvailable}
            scenarioSelected={!!selectedScenario}
            scenarioReloadKey={scenarioReloadKey}
          />

          {(simulationLoading) && (
            <div className="loading-container">
              <Label> Simulation is running...</Label>
              <Loader progress="60%" type="Indeterminate" style={{ width: '400px', height: '10px' }} />
            </div>
          )}
        </div>

        <PopupMessage
          show={!!popupMessage}
          type={popupType}
          message={popupMessage}
          duration={4000}
          onClose={closePopup}
        />
      </ContentContainer>

      <ContentContainer containerHeader='Parameter Editor' height={"auto"}>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          {renderSaveButton()}
          < ResetScenarioButton onReset={forceSimulatorParameterEditorReload} />
        </div >
        <SimulatorParameterEditor scenario={selectedScenario} isParaChange={setIsEditing} ref={parameterEditorRef} />
      </ContentContainer>
    </>
  );
}

export default Simulation;
