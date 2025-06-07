import React from 'react';
import { Button } from '@ui5/webcomponents-react';
import ScenarioSelector from './ScenarioSelector';

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
 * Props for the ScenarioList component
 * @interface ScenarioListProps
 */
interface ScenarioListProps {
  analyses: AnalysisEntry[];
  dropdownOptions: string[];
  handleLogChange: (idx: number, value: string, which?: "Simod" | "Agent" | "Cross") => void;
  handleAnalyze: (idx: number, which?: "Simod" | "Agent" | "Cross") => void;
  removeLog: (idx: number, which?: "Simod" | "Agent" | "Cross") => void;
  addLog: (which?: "Simod" | "Agent" | "Cross") => void;
  modeLabel: string;
  analyzeLabel: string;
  showAdd: boolean;
  which?: "Simod" | "Agent" | "Cross";
}

/**
 * Component that displays a list of scenario selectors with analysis controls
 * @component
 * @param {ScenarioListProps} props - The component props
 * @returns {JSX.Element} The rendered ScenarioList component
 */
const ScenarioList: React.FC<ScenarioListProps> = ({
  analyses,
  dropdownOptions,
  handleLogChange,
  handleAnalyze,
  removeLog,
  addLog,
  modeLabel,
  analyzeLabel,
  showAdd,
  which
}: ScenarioListProps) => (
  <div className="scenario-list-wrapper">
    {analyses.map((entry: AnalysisEntry, idx: number) => (
      <div key={idx} className="upload-section">
        <div className="upload-header"
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>{modeLabel} {idx + 1}</h3>
        </div>
        <ScenarioSelector
          options={dropdownOptions}
          value={
            entry.scenarioId !== null
              ? dropdownOptions.find((option: string) => option.trim().startsWith(`${entry.scenarioId} |`))
              : 'None'
          }
          onChange={(value: string) => handleLogChange(idx, value, which)}
          onAnalyze={() => handleAnalyze(idx, which)}
          analyzing={entry.isAnalyzing}
          showRemove={analyses.length > 1}
          onRemove={() => removeLog(idx, which)}
          label={`Select ${modeLabel}`}
          analyzeLabel={analyzeLabel + ` ${idx + 1}`}
        />
      </div>
    ))}
    {showAdd && (
      <div className="upload-section" style={{ marginTop: '4rem' }}>
        <Button onClick={() => addLog(which)}>
          Add another {modeLabel}
        </Button>
      </div>
    )}
  </div>
);

export default ScenarioList; 