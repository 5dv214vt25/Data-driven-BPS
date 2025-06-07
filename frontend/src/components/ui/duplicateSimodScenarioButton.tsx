// Import necessary components and hooks
import { Button } from '@ui5/webcomponents-react';
import { usePopup } from '../../hooks/usePopup.ts';
import { uploadSimodScenario } from '../../api/controllerAPICalls/SimodScenarioAPICalls.ts';
import { PopupMessage } from '../PopupMessage.tsx';

interface DuplicateSimodScenarioButtonProps {
  scenarioName: string;
  eventLogId: string | null;
  onSaveSuccess?: () => void;
}

// Component for duplicating a Simod scenario
export const DuplicateSimodScenarioButton = ({
  scenarioName,
  eventLogId,
  onSaveSuccess,
}: DuplicateSimodScenarioButtonProps) => {
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  const handleSaveAs = async () => {
    const paramJson = localStorage.getItem('bpmn_json_data');
    const bpmnBlob = paramJson ? new Blob([paramJson], { type: 'application/json' }) : null;

    if (eventLogId && scenarioName && bpmnBlob) {
      // Create a File object for the BPMN data
      const fileBpmn = new File([bpmnBlob], `${scenarioName}.bpmn`, { type: bpmnBlob.type });

      if (paramJson) {
        const paramFile = new File([paramJson], `${scenarioName}_params.json`, { type: 'application/json' });

        const result = await uploadSimodScenario(eventLogId, scenarioName, fileBpmn, paramFile);
      
        // Show a popup message based on the result of the upload
        showPopup(
          result?.success ? 'success' : 'error', 
          result?.success ? 'Scenario saved as version' : 'Failed to save scenario as version'
        );
        
        if (result && onSaveSuccess) {
          onSaveSuccess();
        }
      }
    } else {
      showPopup('error', 'Missing required data to save scenario as version');
    }
  };
  
  // Render the button and popup message
  return (
    <div className="flex flex-col space-y-3">
      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />
      <Button
        design="Emphasized"
        onClick={handleSaveAs}
      >
        Save Scenario Version
      </Button>
    </div>
  );
};