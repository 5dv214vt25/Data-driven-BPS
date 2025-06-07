import { Button } from '@ui5/webcomponents-react';

interface ResetScenarioButtonProps {
  onReset: () => void;
}

// Component for resetting scenario parameters
export const ResetScenarioButton = ({ onReset }: ResetScenarioButtonProps) => {
  // Function to reset parameters and clear local storage
  const resetParameters = async () => {
    localStorage.removeItem('bpmn_json_data');
    localStorage.removeItem('NumberOfSimulations');
    localStorage.removeItem('SimulationDateAndTime');
    onReset();
  };

  // Render the button
  return (
    <div>
      <Button
        design="Negative"
        onClick={resetParameters}
      > 
        Revert Unsaved Changes
      </Button>
    </div>
  );
};
