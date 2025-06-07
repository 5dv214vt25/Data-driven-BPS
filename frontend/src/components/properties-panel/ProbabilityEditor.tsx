/**
 * ProbabilityEditor Component
 *
 * Displays the probability value for a selected path in a BPMN diagram. This
 * component is read-only and serves purely as a display element.
 *
 * Props:
 * - value: A numeric value representing the probability (between 0 and 1) or
 *          null if no probability is assigned to the path.
 *
 * Functionality:
 * - Shows a label and a disabled input field with the formatted probability value.
 * - Displays a fallback message if no probability is defined.
 */
import { Input, Label } from '@ui5/webcomponents-react';

interface ProbabilityEditorProps {
  value: number | null;
}

export default function ProbabilityEditor({ value }: ProbabilityEditorProps) {
  if (value === null) {
    return <span>No probability defined for this path.</span>;
  }

  return (
    <>
      <Label>Probability:</Label>
      <Input
        type="Number"
        value={value.toString()}
        disabled
        placeholder="No probability"
      />
    </>
  );
}
