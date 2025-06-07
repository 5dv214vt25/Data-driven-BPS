
import { useEffect, useState } from "react";

import "../assets/styles/simodAgentSelector.css";

interface Props {
  selected: string;
  newSelected: (selected: string) => void;
  disabled: boolean;
}

/**
 * SimodAgentSelector component allows the user to select between two discovery approaches:
 * "Simod" and "Agent Simulator".
 * 
 * It displays two buttons representing each option, highlighting the selected one, and disables
 * the buttons if the `disabled` prop is true.
 * 
 * This component is used in discoveryController.tsx that is a part of page Discovery.tsx
 * 
 * Props:
 * @param {string} selected - The currently selected discovery approach ("Simod" or "AgentSimulator").
 * @param {(selected: string) => void} newSelected - Callback function called when selection changes,
 *        passing the new selected approach as a string.
 * @param {boolean} disabled - If true, disables both buttons and reduces their opacity.
 */
export default function SimodAgentSelector({ selected, newSelected, disabled }: Props) {
  const [isSimodSelected, setSimodSelected] = useState(true);

  const [isDisabled, setDisabled] = useState(disabled);

  useEffect(() => {
    setSimodSelected(selected == "Simod" ? true : false);
  }, []);

  useEffect(() => {
    setDisabled(disabled);
  }, [disabled]);

  /**
  * Updates the selection state and notifies the parent of the new choice.
  * Does nothing if the selected option is already active.
  */
  const selectorUpdate = (selected: boolean) => {
    if (selected == isSimodSelected) {
      return;
    }
    setSimodSelected(selected);
    newSelected(selected ? "Simod" : "AgentSimulator");
  };

  return (
    <>
      <div className="simodAgentContainer">
        <span className="headlineText">Select Discovery approach</span>
        <div className="selectorContainer">
          <button
            disabled={isDisabled}
            className={`segmentButton ${!isSimodSelected ? "active" : ""} agentButton`}
            style={isDisabled ? { opacity: 0.3 } : {}}
            onClick={() => {
              selectorUpdate(false);
            }}
          >Agent Simulator
          </button>
          <button
            disabled={isDisabled}
            className={`segmentButton ${isSimodSelected ? "active" : ""} sigmodButton`}
            style={isDisabled ? { opacity: 0.3 } : {}}
            onClick={() => {
              selectorUpdate(true);
            }}
          >Simod
          </button>
        </div>
      </div>
    </>
  );
}
