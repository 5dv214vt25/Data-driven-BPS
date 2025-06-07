import { useEffect, useState } from 'react';

import { SelectDropdown } from '../components/SelectDropdown';
import { useEventLogs } from "../hooks/useEventLogs";
import { useUser } from "../context/userContext";

import '../assets/styles/Discovery.css';
import '../assets/styles/Topdivbutton.css';

/**
 * Handles the eventlogDropdownMenu
 * 
 * @component
 */

// interface Props { }


function EventlistDropdownMenu() {
  const [selectedEventlog, setSelectedEventlog] = useState<string | null>(null);
  const { userSettings } = useUser();
  const { eventLogs, loadEventLogs } = useEventLogs();

  /**
   * @function useEffect
   * @description Updates the eventlogs to correspond to the specific user
   */
  useEffect(() => {
    getEventLogs();
  }, [userSettings.username]);


  /**
   * @function useEffect
   * @description update the eventlog view when the model changes
   */
  useEffect(() => {
    setEventLogs();
  }, [eventLogs]);


  /**
   * @function getEventLogs
   * @description loads all event logs connected to a specific user.
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
   * @description Sets default / selected option in the dropdown list.
   * @returns nothing
   */
  const setEventLogs = () => {
    if (eventLogs.length > 0) {
      if (!selectedEventlog || !eventLogs.some(log => log.event_log_id === selectedEventlog)) {
        setSelectedEventlog(eventLogs[0].event_log_id);
      }
    } else {
      setSelectedEventlog(null);
    }
  };

  /**
   * @function setValue 
   * @description selects specific item/value in the dropdown menu
   * @returns string
   */
  const setValue = () => {
    if (selectedEventlog === 'test') {
      return 'Test Log';

    } else if (selectedEventlog) {
      const foundLog = eventLogs.find(log => log.event_log_id === selectedEventlog);
      return foundLog ? foundLog.filename : 'None';
    } else {
      return "None";
    }
  };

  /**
   * @function _onChange
   * @description handles the onChange logic in the drowdown menu
   * @returns nothing
   */
  const _onChange = (filename: string) => {
    if (filename === 'None') {
      setSelectedEventlog(null);

    } else if (filename === 'Test Log') {
      setSelectedEventlog('test');

    } else {
      const log = eventLogs.find((log) => log.filename === filename);
      setSelectedEventlog(log?.event_log_id || null);
    }
  };

  return (<>
    <SelectDropdown
      options={['None', ...eventLogs.map((log) => log.filename), 'Test Log']}
      label="Select Log"
      value={setValue()}
      onChange={(filename: string) => _onChange(filename)}
    />
  </>);
}

export default EventlistDropdownMenu;