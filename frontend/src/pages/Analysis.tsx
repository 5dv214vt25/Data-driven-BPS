import React, { useState, useEffect } from 'react';
import { Button } from '@ui5/webcomponents-react';
import { PopupMessage } from '../components/PopupMessage';
import AnalysisView from '../components/analysis-panel/AnalysisView';
import { useUser } from '../context/userContext';
import { usePopup } from '../hooks/usePopup';
import { fetchSimodOutputs } from '../api/controllerAPICalls/SimodOutputAPICalls';
import { fetchAgentOutputs } from '../api/controllerAPICalls/AgentOutputAPICalls';
import { analyzeSimodScenarioOutput, analyzeAgentScenarioOutput } from '../api/controllerAPICalls/AnalyzeAPICalls';
import '../assets/styles/Analysis.css';
import ModeSelector from '../components/analysis-panel/ModeSelector';
import ScenarioList from '../components/analysis-panel/ScenarioList';

/**
 * Interface representing a Simod output scenario
 * @interface SimodOutput
 */
interface SimodOutput {
  event_log_id: number;
  event_log_name: string;
  output_filename: string;
  scenario_name: string;
  simod_scenario_id: number;
}

/**
 * Interface representing an Agent output scenario
 * @interface AgentOutput
 */
interface AgentOutput {
  event_log_id: number;
  event_log_name: string;
  output_filename: string;
  scenario_name: string;
  agent_scenario_id: number;
}

/**
 * Interface representing an analysis entry with its state
 * @interface AnalysisEntry
 */
interface AnalysisEntry {
  scenarioId: number | null;
  analysisResult: any | null;
  isAnalyzing: boolean;
}

/**
 * Main Analysis component that handles scenario analysis for Simod and Agent simulations
 * @component
 * @returns {JSX.Element} The rendered Analysis component
 */
const Analysis: React.FC = () => {
  const { userSettings } = useUser();
  const { showPopup, closePopup, message: popupMessage, type: popupType } = usePopup();

  const [mode, setMode] = useState<'Simod' | 'Agent' | 'Cross'>('Simod');
  const [outputs, setOutputs] = useState<(SimodOutput | AgentOutput)[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [analyses, setAnalyses] = useState<AnalysisEntry[]>([
    { scenarioId: null, analysisResult: null, isAnalyzing: false }
  ]);
  const [showUndefined, setShowUndefined] = useState<boolean>(false);

  // New state for cross mode
  const [simodAnalyses, setSimodAnalyses] = useState<AnalysisEntry[]>([
    { scenarioId: null, analysisResult: null, isAnalyzing: false }
  ]);
  const [agentAnalyses, setAgentAnalyses] = useState<AnalysisEntry[]>([
    { scenarioId: null, analysisResult: null, isAnalyzing: false }
  ]);
  const [simodOutputs, setSimodOutputs] = useState<SimodOutput[]>([]);
  const [agentOutputs, setAgentOutputs] = useState<AgentOutput[]>([]);

  const modeOptions = ['Simod', 'Agent', 'Cross'];

  useEffect(() => {
    if (!userSettings.username) { return; }
    if (mode === 'Cross') {
      handleFetchOutputs('Simod');
      handleFetchOutputs('Agent');
    } else if (mode === 'Simod' || mode === 'Agent') {
      handleFetchOutputs(mode);
    }
  }, [userSettings.username, mode]);

  /**
   * Fetches outputs for either Simod or Agent scenarios
   * @param {('Simod'|'Agent')} fetchMode - The mode to fetch outputs for
   */
  const handleFetchOutputs = async (fetchMode: 'Simod' | 'Agent') => {
    try {
      setLoading(true);
      if (fetchMode === 'Simod') {
        const fetchedSimod = await fetchSimodOutputs(userSettings.username);
        setSimodOutputs(fetchedSimod);
        setSimodAnalyses([{ scenarioId: null, analysisResult: null, isAnalyzing: false }]);
        if (mode === 'Simod') {
          setOutputs(fetchedSimod);
          setAnalyses([{ scenarioId: null, analysisResult: null, isAnalyzing: false }]);
        }
      } else {
        const fetchedAgent = await fetchAgentOutputs(userSettings.username);
        setAgentOutputs(fetchedAgent);
        setAgentAnalyses([{ scenarioId: null, analysisResult: null, isAnalyzing: false }]);
        if (mode === 'Agent') {
          setOutputs(fetchedAgent);
          setAnalyses([{ scenarioId: null, analysisResult: null, isAnalyzing: false }]);
        }
      }
    } catch (error: any) {
      const status = error?.status;
      console.error(`Error status:`, status);
      // this is server errors it shouldn't be presented to the user
      if (status === 400) {
        console.error('error', `${fetchMode} data not found.`);
      } else if (status === 500) {
        console.error('error', `Server error while loading ${fetchMode} data.`);
      } else {
        console.error('error', `Failed to load ${fetchMode} outputs. Please try again later.`);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Analyzes a selected scenario
   * @param {number} index - The index of the analysis entry
   * @param {('Simod'|'Agent'|'Cross')} which - The mode to analyze in
   */
  const handleAnalyze = async (index: number, which: 'Simod' | 'Agent' | 'Cross' = mode) => {
    let entry: AnalysisEntry;
    let updated: AnalysisEntry[];
    let scenarioId: number | null;
    if (mode === 'Cross') {
      if (which === 'Simod') {
        entry = simodAnalyses[index];
        scenarioId = entry.scenarioId;
        updated = [...simodAnalyses];
      } else {
        entry = agentAnalyses[index];
        scenarioId = entry.scenarioId;
        updated = [...agentAnalyses];
      }
    } else {
      entry = analyses[index];
      scenarioId = entry.scenarioId;
      updated = [...analyses];
    }

    if (scenarioId === null) {
      showPopup('error', 'Please select a scenario first.');
      return;
    }

    const duplicate = updated.some((a, i) => i !== index && a.scenarioId === scenarioId);
    if (duplicate) {
      showPopup('error', 'This scenario is already selected in another analysis.');
      return;
    }

    updated[index].isAnalyzing = true;
    if (mode === 'Cross') {
      which === 'Simod' ? setSimodAnalyses(updated) : setAgentAnalyses(updated);
    } else {
      setAnalyses(updated);
    }

    try {
      const result = which === 'Simod'
        ? await analyzeSimodScenarioOutput(userSettings.username, scenarioId)
        : await analyzeAgentScenarioOutput(userSettings.username, scenarioId);
      updated[index].analysisResult = result.analysis_result;
    } catch (error) {
      showPopup('error', `Failed to analyze scenario ${scenarioId}`);
      console.error(error);
    } finally {
      updated[index].isAnalyzing = false;
      if (mode === 'Cross') {
        which === 'Simod' ? setSimodAnalyses([...updated]) : setAgentAnalyses([...updated]);
      } else {
        setAnalyses([...updated]);
      }
    }
  };

  /**
   * Handles changes to the selected log/scenario
   * @param {number} index - The index of the analysis entry
   * @param {string} value - The new value selected
   * @param {('Simod'|'Agent'|'Cross')} which - The mode being used
   */
  const handleLogChange = (index: number, value: string, which: 'Simod' | 'Agent' | 'Cross' = mode) => {
    let updated: AnalysisEntry[];
    if (mode === 'Cross') {
      updated = which === 'Simod' ? [...simodAnalyses] : [...agentAnalyses];
    } else {
      updated = [...analyses];
    }
    if (value === 'None') {
      updated[index].scenarioId = null;
      updated[index].analysisResult = null;
    } else {
      const scenarioId = parseInt(value.split('|')[0].trim(), 10);
      updated[index].scenarioId = scenarioId;
      updated[index].analysisResult = null;
    }
    if (mode === 'Cross') {
      which === 'Simod' ? setSimodAnalyses(updated) : setAgentAnalyses(updated);
    } else {
      setAnalyses(updated);
    }
    closePopup();
  };

  /**
   * Adds a new log entry for analysis
   * @param {('Simod'|'Agent'|'Cross')} which - The mode to add the log for
   */
  const addLog = (which: 'Simod' | 'Agent' | 'Cross' = mode) => {
    if (mode === 'Cross') {
      if (which === 'Simod') {
        if (simodAnalyses.length >= simodOutputs.length) {
          showPopup('error', 'No more Simod scenarios available.');
          return;
        }
        setSimodAnalyses([...simodAnalyses, { scenarioId: null, analysisResult: null, isAnalyzing: false }]);
      } else {
        if (agentAnalyses.length >= agentOutputs.length) {
          showPopup('error', 'No more Agent scenarios available.');
          return;
        }
        setAgentAnalyses([...agentAnalyses, { scenarioId: null, analysisResult: null, isAnalyzing: false }]);
      }
    } else {
      if (analyses.length >= outputs.length) {
        showPopup('error', 'No more simulated scenarios available.');
        return;
      }
      setAnalyses([...analyses, { scenarioId: null, analysisResult: null, isAnalyzing: false }]);
    }
  };

  /**
   * Removes a log entry from analysis
   * @param {number} index - The index of the entry to remove
   * @param {('Simod'|'Agent'|'Cross')} which - The mode to remove the log from
   */
  const removeLog = (index: number, which: 'Simod' | 'Agent' | 'Cross' = mode) => {
    if (mode === 'Cross') {
      if (which === 'Simod') {
        if (simodAnalyses.length <= 1) { return; }
        const updated = [...simodAnalyses];
        updated.splice(index, 1);
        setSimodAnalyses(updated);
      } else {
        if (agentAnalyses.length <= 1) { return; }
        const updated = [...agentAnalyses];
        updated.splice(index, 1);
        setAgentAnalyses(updated);
      }
    } else {
      if (analyses.length <= 1) { return; }
      const updated = [...analyses];
      updated.splice(index, 1);
      setAnalyses(updated);
    }
  };

  if (loading) {
    return <div className="analysis-container">Loading {mode} scenarios…</div>;
  }

  const simodDropdownOptions = [
    'None',
    ...simodOutputs.map((output: SimodOutput) => `${output.simod_scenario_id} | ${output.scenario_name}`)
  ];
  const agentDropdownOptions = [
    'None',
    ...agentOutputs.map((output: AgentOutput) => `${output.agent_scenario_id} | ${output.scenario_name}`)
  ];
  const dropdownOptions = [
    'None',
    ...outputs.map((output: SimodOutput | AgentOutput) => {
      if (mode === 'Simod' && 'simod_scenario_id' in output) {
        return `${output.simod_scenario_id} | ${output.scenario_name}`;
      } else if (mode === 'Agent' && 'agent_scenario_id' in output) {
        return `${output.agent_scenario_id} | ${output.scenario_name}`;
      }
      return null;
    }).filter(Boolean) as string[]
  ];

  return (
    <div className="analysis-container">
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1rem'
      }}>
        <h1 className="h1style">Analyze {mode} Scenarios</h1>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
            alignItems: 'flex-end',
            minWidth: '200px'
          }}
        >
          <ModeSelector
            options={modeOptions}
            value={mode}
            onChange={val => setMode(val as 'Simod' | 'Agent' | 'Cross')}
          />
          <Button onClick={() => setShowUndefined(prev => !prev)}>
            {showUndefined ? 'Hide undefined values' : 'Show undefined values'}
          </Button>
        </div>
      </div>

      {mode === 'Cross' ? (
        <div className="scenario-list-wrapper">
          <div className="upload-section">
            <div className="upload-header"
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>Select Simod Scenario</h3>
            </div>
            <ScenarioList
              analyses={simodAnalyses}
              dropdownOptions={simodDropdownOptions}
              handleLogChange={handleLogChange}
              handleAnalyze={handleAnalyze}
              removeLog={removeLog}
              addLog={addLog}
              modeLabel="Simod Scenario"
              analyzeLabel="Analyze Simod Scenario"
              showAdd={simodAnalyses.length < simodOutputs.length}
              which="Simod"
            />
          </div>
          <div className="upload-section">
            <div className="upload-header"
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>Select Agent Scenario</h3>
            </div>
            <ScenarioList
              analyses={agentAnalyses}
              dropdownOptions={agentDropdownOptions}
              handleLogChange={handleLogChange}
              handleAnalyze={handleAnalyze}
              removeLog={removeLog}
              addLog={addLog}
              modeLabel="Agent Scenario"
              analyzeLabel="Analyze Agent Scenario"
              showAdd={agentAnalyses.length < agentOutputs.length}
              which="Agent"
            />
          </div>
        </div>
      ) : (
        <ScenarioList
          analyses={analyses}
          dropdownOptions={dropdownOptions}
          handleLogChange={handleLogChange}
          handleAnalyze={handleAnalyze}
          removeLog={removeLog}
          addLog={addLog}
          modeLabel="Scenario"
          analyzeLabel="Analyze Scenario"
          showAdd={analyses.length < outputs.length}
          which={mode}
        />
      )}

      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />

      <div className="analysis-view-container" style={{ marginTop: '2rem' }}>
        {mode === 'Cross' ? (
          <>
            {simodAnalyses.map((entry, idx) =>
              entry.analysisResult ? (
                <AnalysisView
                  key={`simod-view-${idx}`}
                  analysis={entry.analysisResult}
                  title={`Simod Scenario ${idx + 1}`}
                  showUndefined={showUndefined}
                />
              ) : null
            )}
            {agentAnalyses.map((entry, idx) =>
              entry.analysisResult ? (
                <AnalysisView
                  key={`agent-view-${idx}`}
                  analysis={entry.analysisResult}
                  title={`Agent Scenario ${idx + 1}`}
                  showUndefined={showUndefined}
                />
              ) : null
            )}
          </>
        ) : (
          analyses.map((entry, idx) =>
            entry.analysisResult ? (
              <AnalysisView
                key={`view-${idx}`}
                analysis={entry.analysisResult}
                title={`Scenario ${idx + 1}`}
                showUndefined={showUndefined}
              />
            ) : null
          )
        )}
      </div>
    </div>
  );
};

export default Analysis;