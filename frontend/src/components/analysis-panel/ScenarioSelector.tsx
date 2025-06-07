import React from 'react';
import { Button } from '@ui5/webcomponents-react';
import { SelectDropdown } from '../SelectDropdown';

/**
 * Props for the ScenarioSelector component
 * @interface ScenarioSelectorProps
 */
interface ScenarioSelectorProps {
  options: string[];
  value: string | undefined;
  onChange: (val: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
  showRemove?: boolean;
  onRemove?: () => void;
  label: string;
  analyzeLabel: string;
}

/**
 * Component that provides scenario selection and analysis controls
 * @component
 * @param {ScenarioSelectorProps} props - The component props
 * @returns {JSX.Element} The rendered ScenarioSelector component
 */
const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({
  options,
  value,
  onChange,
  onAnalyze,
  analyzing,
  showRemove = false,
  onRemove,
  label,
  analyzeLabel,
}: ScenarioSelectorProps) => (
  <div className="upload-body">
    <SelectDropdown
      options={options}
      label={label}
      value={value}
      onChange={onChange}
    />
    <Button onClick={onAnalyze} disabled={analyzing}>
      {analyzing ? 'Analyzing…' : analyzeLabel}
    </Button>
    {showRemove && onRemove && (
      <Button design="Transparent" onClick={onRemove} title="Remove scenario">
        ❌
      </Button>
    )}
  </div>
);

export default ScenarioSelector; 