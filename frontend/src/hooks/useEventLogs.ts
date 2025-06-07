import { useState } from 'react';
import { fetchEventLogs } from '../api/simulationAPI';

/**
 * Interface/type the component uses.
 */
interface EventLogsList {
  /** A string representing the eventID. */
  eventID: string,
  /** A string representing the event name.  */
  eventName: string
}

/**
 * Custom hook to loads event logs from a user id.
 */

export const useEventLogs = () => {

  /** Use state that handles the list of event logs. */
  const [eventLogsList, setEventLogsList] = useState<EventLogsList[]>([]);
  /** Use state that sets the  */
  const [eventLogs, setEventLogs] = useState<{ filename: string; event_log_id: string }[]>([]);
  /** Use state that handles if loading bar should be displayed or not. */
  const [loading, setLoading] = useState(false);

  const loadEventLogs = async (userId: string) => {

    /** Sets the loading bar to be visible on call. */
    setLoading(true);
    try {
      /** Retrieves the event logs that are stored on userId. */
      const response = await fetchEventLogs(userId);

      /** If the response is false or the length is zero display error message,
       * and set the list of event logs and the selected eventlog to be empty.
       */
      if (!response || response.length === 0) {
        console.warn('No event logs returned from API.');
        setEventLogs([]);
        setEventLogsList([]);
        return;
      }

      /** Transforms the response (array of objects) to an array of event logs. */
      const eventList = response.map((item: any ) => ({
        eventID: item.event_log_id,
        eventName: item.filename,
      }));


      /** Sets the event log list to eventList. */
      setEventLogsList(eventList);
      /** Sets the event log to response. */
      setEventLogs(response);

    } catch (error: unknown) {

      /** On error thrown
       * 
       *  display error message and set eventlogs to empty.
       */
      console.error('Failed to fetch event logs:', error);
      setEventLogs([]);

    } finally {

      /** Always sets the loading bar to be invisible. */
      setLoading(false);

    }
  };
 
  return { eventLogs, loadEventLogs, eventLogsList, loading };

};
