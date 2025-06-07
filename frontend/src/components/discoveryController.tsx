import { useEffect, useState } from "react";
import { Button, Label } from '@ui5/webcomponents-react';
import { SelectDropdown } from '../components/SelectDropdown';
import { useNavigate } from "react-router-dom";
import { useEventLogs } from "../hooks/useEventLogs";
import { useUser } from "../context/userContext";
import { usePopup } from "../hooks/usePopup";
import { PopupMessage } from "./PopupMessage";

import '../assets/styles/Discovery.css';
import '../assets/styles/Topdivbutton.css';
import SimodAgentSelector from "./simodAgentSelector";

/**
 * Handles the page configurations
 * 
 * @component
 */
interface Props {
  handleDiscovery: (selectedEventLog2: string | null, selectedApproach2: string) => void;
  buttonEnableSaveScenario?: Boolean;
  isLoading?: boolean;
  selectedApproach: string;
  setSelectedApproach: React.Dispatch<React.SetStateAction<string>>;
}

/**
 * DiscoveryController component manages the UI and logic for selecting an event log,
 * choosing a discovery approach (Simod or AgentSimulator), and triggering the discovery process.
 * It also provides navigation to the simulation page and handles popup notifications.
 */
function DiscoveryController(props: Props) {
  const { selectedApproach, setSelectedApproach } = props;
  const [selectedEventlog, setSelectedEventlog] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const { userSettings } = useUser();
  const { eventLogs, loadEventLogs, loading: logsLoading } = useEventLogs();
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  /**
   * @function useEffect
   * @description Calls getEventLogs when the component mounts
   * @returns nothing
   */
  useEffect(() => {
    getEventLogs();
  }, [userSettings.username]);

  useEffect(() => {
    setEventLogs();
  }, [eventLogs]);

  useEffect(() => {
    if (props.isLoading != undefined) {
      setIsLoading(props.isLoading);
    }

  }, [props.isLoading]);

  // Update dropdown value when eventLogs or selectedEventlogId changes
  useEffect(() => {
    if (eventLogs.length > 0) {
      if (userSettings.selectedEventlogId === null) {
        setSelectedEventlog(eventLogs[0].event_log_id);
      } else {
        const selectedLog = eventLogs.find((log) => log.event_log_id.toString() === userSettings.selectedEventlogId);
        if (selectedLog) {
          setSelectedEventlog(selectedLog.event_log_id);
        } else {
          setSelectedEventlog(eventLogs[0].event_log_id);
        }
      }
    }
  }, [eventLogs, userSettings.selectedEventlogId]);

  useEffect(() => {
    if (eventLogs.length > 0) {
      const selectedLog = eventLogs.find((log) => log.event_log_id.toString() === userSettings.selectedEventlogId);
      console.log('Selected log:', selectedLog?.event_log_id);
      if (userSettings.selectedEventlogId && !selectedLog) {
        console.warn('Invalid selectedEventlogId:', userSettings.selectedEventlogId);
      }
    }
  }, [eventLogs, userSettings.selectedEventlogId]);

  /**
   * @function getEventLogs
   * @description Function to load event logs for a specific user.
   * @returns nothing
   */
  const getEventLogs = () => {
    if (!userSettings.username.trim()) {
      console.error("When loading eventlogs, userID can't be empty");
      return;
    }
    loadEventLogs(userSettings.username);
    setEventLogs();
  };

  /**
   * @function setEventLogs
   * @description Function to set the selected event log.
   * @returns nothing
   */
  const setEventLogs = () => {
    if (eventLogs.length > 0) {
      if (!selectedEventlog || !eventLogs.some(log => log.event_log_id === selectedEventlog)) {
        setSelectedEventlog(eventLogs[0].event_log_id);
      }
    } else {
      setSelectedEventlog('None');
    }
  };

  const generateEventDropdown = () => {
    const formatEventLogOption = (log: { event_log_id: string, filename: string; }) =>
      `${log.event_log_id} | ${log.filename}`;

    const getSelectedLog = () => {
      if (selectedEventlog === 'null') { return 'None'; }
      const log = eventLogs.find(log => log.event_log_id === selectedEventlog);
      return log ? formatEventLogOption(log) : 'None';
    };

    const handleEventLogChange = (displayName: string) => {
      if (displayName === 'None') {
        setSelectedEventlog('null');
      } else if (displayName === 'Test Log') {
        setSelectedEventlog('test');
      } else {
        const log = eventLogs.find(log => formatEventLogOption(log) === displayName);
        if (log) {
          setSelectedEventlog(log.event_log_id);
        }
      }
    };

    return (
      <>
        {logsLoading ? (
          <Label>Loading event logs...</Label>
        ) : (
          <SelectDropdown
            options={eventLogs.length === 0 ? ['None'] : eventLogs.map(formatEventLogOption)}
            label="Select Event Log"
            disabled={isLoading}
            value={getSelectedLog()}
            onChange={handleEventLogChange}
          />
        )}
      </>);
  };

  return (
    <div className="controls-container">

      {generateEventDropdown()}

      <SimodAgentSelector
        selected={selectedApproach}
        disabled={selectedEventlog == "None" || isLoading ? true : false}
        newSelected={(selectorUpdate: string) => {
          setSelectedApproach(selectorUpdate);
        }}
      />

      <Button design="Default"
        className="topdivbuttonstyle"

        onClick={() => {
          if (!selectedEventlog) {
            showPopup("error", "Please select an event log");
            return;
          }
          props.handleDiscovery(selectedEventlog, selectedApproach);
        }}

        disabled={isLoading || selectedEventlog == 'None'}>
        Start Discovery
      </Button>

      <Button
        design="Default"
        className="topdivbuttonstyle"
        disabled={isLoading || selectedEventlog == 'None' || !props.buttonEnableSaveScenario}

        onClick={() => {
          let str = "simulation";
          navigate("/" + str);
        }}>
        Go to Simulation
      </Button>

      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />
    </div>
  );
}

export default DiscoveryController;
