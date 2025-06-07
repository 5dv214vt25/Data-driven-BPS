// Import necessary components and hooks
import { Button } from '@ui5/webcomponents-react';
import { usePopup } from '../../hooks/usePopup.ts';
import { updateSimodScenario } from '../../api/controllerAPICalls/SimodScenarioAPICalls.ts';
import { PopupMessage } from '../PopupMessage.tsx';

interface SaveSimodScenarioButtonProps {
  scenarioName: string;
  scenarioId: string | null;
  onSaveSuccess?: () => void;
}

// Component for saving a Simod scenario
export const SaveSimodScenarioButton = ({
  scenarioId,
  scenarioName,
  onSaveSuccess,
}: SaveSimodScenarioButtonProps) => {
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  const handleSave = async () => {
    if (scenarioId && scenarioName) {
      const paramJson = localStorage.getItem('bpmn_json_data');

      if (paramJson) {
        // Create a File object for the BPMN data
        const paramFile = new File([paramJson], `${scenarioName}_params.json`, { type: 'application/json' });

        const success = await updateSimodScenario(scenarioId, scenarioName, paramFile);

        if (success && onSaveSuccess) {
          onSaveSuccess();
        }
      }
    } else {
      showPopup('error', 'Missing required data to save scenario');
    }
  };
  
  // Render the button and popup message
  return (
    <div>
      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />
      <Button
        design="Emphasized"
        onClick={handleSave}
      >
        Save Scenario
      </Button>
    </div>
  );
};
