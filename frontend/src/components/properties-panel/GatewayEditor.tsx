/**
 * GatewayEditor Component
 *
 * Renders a panel allowing users to edit the branching probabilities for a
 * Gateway in a BPMN diagram. Users can adjust probabilities manually and
 * balance them to ensure the total equals 1.0.
 *
 * Functionality:
 * - Validates that the sum of probabilities equals 1.0, showing an error if not.
 * - Provides a "Balance" button that adjusts a single probability to correct
 *   any imbalance in the total.
 */

import { useState, useEffect } from 'react';
import { Input, Label, Button } from '@ui5/webcomponents-react';
import './GatewayEditor.css';
import { PathProbability } from '../../types/JsonDataSimod';

/**
 * Props:
 * - probabilities: An array of path probability objects (path_id and value).
 * - onChange: Optional callback function that receives the updated probabilities.
 * - getTargetElementName: A function that returns a display name for a given pathId.
 */
interface GatewayEditorProps {
  probabilities: PathProbability[];
  onChange?: (updated: PathProbability[]) => void;
  getTargetElementName: (pathId: string) => string;
}

export default function GatewayEditor({
  probabilities,
  onChange,
  getTargetElementName,
}: GatewayEditorProps) {
  const [localProbs, setLocalProbs] = useState<PathProbability[]>([]);
  const [isValidTotal, setIsValidTotal] = useState(true);

  useEffect(() => {
    setLocalProbs([...probabilities]);
  }, [probabilities]);

  // Check that sum of probabilities is 1 after each change.
  useEffect(() => {
    const total = localProbs.reduce((sum, p) => sum + p.value, 0);
    const valid = Math.abs(total - 1.0) < 0.0001;
    setIsValidTotal(valid);
  }, [localProbs]);

  const handleInputChange = (index: number, rawValue: string) => {
    const parsed = parseFloat(rawValue);
    if (!isNaN(parsed)) {
      const updated = [...localProbs];
      updated[index] = {
        ...updated[index],
        value: parsed,
      };
      setLocalProbs(updated);
      if (onChange) {
        onChange(updated);
      }
    }
  };

  const handleBalanceClick = (index: number) => {
    const total = localProbs.reduce((sum, p) => sum + p.value, 0);
    const diff = 1.0 - total;
    const updated = [...localProbs];
    const currentValue = updated[index].value;
    const newValue = Math.max(0, Math.min(1, currentValue + diff));
    updated[index] = {
      ...updated[index],
      value: parseFloat(newValue.toFixed(4)),
    };
    setLocalProbs(updated);
    if (onChange) {
      onChange(updated);
    }
  };

  return (
    <div className="gateway-editor">
      <Label>Gateway Branch Probabilities</Label>
      <div className="gateway-branches">
        {localProbs.map((branch, idx) => (
          <div key={branch.path_id} className="branch-row">
            <Label>To: {getTargetElementName(branch.path_id)}</Label>
            <Input
              value={branch.value.toString()}
              type="Number"
              onInput={(e: any) => handleInputChange(idx, e.target.value)}
            />
            <Button onClick={() => handleBalanceClick(idx)}>Balance</Button>
          </div>
        ))}
      </div>
      {!isValidTotal && (
        <div style={{ color: 'red', marginTop: '0.5rem' }}>
          Total probability must equal 1.0. Current: {localProbs
            .reduce((sum, p) => sum + p.value, 0)
            .toFixed(4)}
        </div>
      )}
    </div>
  );
}
