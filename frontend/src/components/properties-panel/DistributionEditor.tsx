/**
 * DistributionEditor Component
 *
 * Renders an editable form for a given probability distribution's parameters.
 * It displays input fields corresponding to the distribution type (e.g., 'gamma', 'lognorm'),
 * and uses a label mapping to show human-readable parameter names.
 *
 * Props:
 * - distributionName: Name of the distribution type (e.g., 'gamma', 'norm')
 * - distributionParams: Array of parameter objects, each with a numeric value
 * - onChange: Callback to notify parent component of parameter changes
 */

import { Input, Label } from '@ui5/webcomponents-react';
import './DistributionEditor.css';

interface DistributionEditorProps {
  distributionName: string;
  distributionParams: { value: number }[];
  onChange: (paramIndex: number, newValue: number) => void;
}

export default function DistributionEditor({
  distributionName,
  distributionParams,
  onChange
}: DistributionEditorProps) {
  const labelsByType: Record<string, string[]> = {
    gamma: ['Mean', 'Variance', 'Min', 'Max'],
    lognorm: ['Mean', 'Variance', 'Min', 'Max'],
    norm: ['Mean', 'SD', 'Min', 'Max'],
    uniform: ['Min', 'Max'],
    expon: ['Mean', 'Min', 'Max'],
    fix: ['Mean'],
  };

  const labels = labelsByType[distributionName] || [];

  return (
    <div className="distribution-editor">
      {distributionParams.map((param, index) => (
        <div key={index} className="distribution-row">
          <Label className="distribution-label">
            {labels[index] || `Param ${index + 1}`}:
          </Label>
          <Input
            value={param.value.toString()}
            onInput={(e: any) => onChange(index, Number(e.target.value))}
          />
        </div>
      ))}
    </div>
  );
}
