import React, { useEffect, useRef, useState } from "react";
import {
  Table,
  TableRow,
  TableCell,
  TableHeaderRow,
  TableHeaderCell,
  Button,
  Input,
  InputDomRef,
  TableRowAction,
} from "@ui5/webcomponents-react";
import { PopupMessage } from '../components/PopupMessage';
import { usePopup } from '../hooks/usePopup';
import { useUser } from "../context/userContext";
import {
  fetchEventLog,
  fetchEventLogs,
  updateEventLogName,
  deleteEventLog
} from "../api/controllerAPICalls/EventLogAPICalls";
import { CsvDisplayDataRef } from './CsvDisplayData';
import "@ui5/webcomponents-icons/dist/delete.js";

/** Represents a single event log */
interface EventLog {
  /** Unique ID for the event log */
  event_log_id: number;
  /** The filename  */
  filename: string;
}

/** Props for the EventTable component */
interface EventTableProps {
  /** Callback to trigger when a row (event log) is clicked. */
  onRowClick: (file: File) => void;
  /** A number flag that triggers a reload when changed */
  csvRef: React.RefObject<CsvDisplayDataRef | null>;
  reloadFlag: number;
  onRemoval: () => void;
}

/**
 * EventTable Component
 *
 * Displays a list of event logs in a searchable and scrollable table.
 * Allows selecting a log to load it, and supports deletion with confirmation.
 *
 * @component
 * @param {EventListProps}  props - Component props
 * @returns {JSX.Element}   Rendered event log list
 */
const EventTable: React.FC<EventTableProps> = ({ onRowClick, csvRef, reloadFlag, onRemoval }) => {
  /** User information */
  const { userSettings } = useUser();
  /** List of event logs */
  const [eventLogs, setEventLogs] = useState<EventLog[]>([]);
  /** Selected event log */
  const [selectedEventLogId, setSelectedEventLogId] = useState<number | null>(null);
  /** Number of event logs to show in the event logs list */
  const [visibleCount, setVisibleCount] = useState(5);
  /** Search keyword for filtering logs */
  const [searchTerm, setSearchTerm] = useState("");
  /** Ref to the search input field */
  const inputRef = useRef<InputDomRef>(null);
  /** Event log's ID to be edited */
  const [editingEventLogId, setEditingEventLogId] = useState<number | null>(null);
  /** Event log to be edited */
  const [editedEventLog, setEditedEventLog] = useState<string>("");

  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  const [loading, setLoading] = useState(true);

  /**
   * Fetches the event logs for the current user when the component mounts
   * or when `reloadFlag` or username changes.
   */
  useEffect(() => {
    const fetchLogs = async () => {
      if (!userSettings.username) {
        return;
      }
      setLoading(true);
      try {
        const logs = await fetchEventLogs(userSettings.username);

        // Remove `.csv` for display purposes
        const processedLogs = logs.map((log: EventLog) => ({
          ...log,
          filename: log.filename.replace(/\.csv$/i, ""),
        }));

        setEventLogs(processedLogs);
      } catch (error: any) {
        console.error("Failed to fetch event logs:", error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [userSettings.username, reloadFlag]);

  /**
   * Visually display more rows when the more button the the table is visible 
  */
  const handleLoadMore = () => {
    setVisibleCount((prev) => prev + 5);
  };

  /** 
   * Filters event logs based on the search term entered by the user 
  */
  const handleSearch = () => {
    const value = inputRef.current?.value || "";
    setSearchTerm(value.toLowerCase());
    setVisibleCount(5); // Reset number of event logs to show when seaching
  };

  /** 
   * Filters the logs bases on filename or event log ID 
  */
  const filteredLogs = eventLogs.filter((log) => {
    const search = searchTerm.toLowerCase();
    return (
      log.filename.toLowerCase().includes(search) ||
      log.event_log_id.toString().includes(search)
    );
  });

  /**
   * Fetches the eventlog from the datastore when clicked 
   * 
   * @param eventLogId ID of the event log to delete 
   */
  const handleRowClick = async (eventLogId: number) => {
    const lastIDString = localStorage.getItem("lastID");
    const lastID = lastIDString !== null ? Number(lastIDString) : undefined;

    if (!userSettings.username || !eventLogs) {
      return;
    }

    if (lastID != eventLogId) {
      try {
        localStorage.removeItem("columnMapping");
        localStorage.removeItem("csvData");
        localStorage.removeItem("originalCsvColumnOrder");

        const eventLogBlob = await fetchEventLog(userSettings.username, eventLogId);

        // Get the filename
        const log = eventLogs.find(log => log.event_log_id === eventLogId);
        const eventLogName = log ? log.filename : `event_log_${eventLogId}`;

        const eventLogFile = new File([eventLogBlob], eventLogName);
        onRowClick(eventLogFile);
        userSettings.selectedEventlogId = eventLogId.toString();
        setSelectedEventLogId(eventLogId);

        localStorage.setItem('lastID', JSON.stringify(eventLogId));
      } catch (error) {
        console.error("Failed to fetch event log:", error);
      }
    }
  };

  /**
   * Deletes an event log after user confirmation and updates the table.
   * 
   * @param eventLogId ID of the event log to delete
   */
  const handleDelete = async (eventLogId: number) => {
    if (!userSettings.username) {
      return;
    }

    const confirmed = window.confirm("Are you sure you want to delete this event log?");
    if (!confirmed) {
      return;
    }

    try {
      await deleteEventLog(userSettings.username, String(eventLogId));
      setEventLogs((prevLogs) => prevLogs.filter(log => log.event_log_id !== eventLogId));

      // First check that we lastID and event_log_id is the same to reset it
      const lastIDString = localStorage.getItem("lastID");
      const lastID = lastIDString !== null ? Number(lastIDString) : undefined;

      if (lastID == eventLogId) {
        onRemoval(); // Clear csvData remove is confirmed
        if (csvRef.current) {
          csvRef.current.reset();
        }
      }

    } catch (error) {
      console.error("Delete failed:", error);
      showPopup("error", "Failed to delete event log. Please try again.");
    }
  };

  /**
   * Sets the state of the eventlog to edited.
   * 
   * @param eventLogId ID of the event log to delete
   */
  const handleEdit = async (eventLogId: number) => {
    if (!userSettings.username) {
      return;
    }

    const eventLogToEdit = eventLogs.find(log => log.event_log_id === eventLogId);
    if (eventLogToEdit) {
      setEditingEventLogId(eventLogId);
      setEditedEventLog(eventLogToEdit.filename);
    }
  };

  /**
   * Updates the eventlogs name when the changes are saved.
   * 
   */
  const handleSaveEdit = async () => {
    if (!userSettings.username || editingEventLogId === null) {
      return;
    }

    // Trim and remove .csv or .xes if user included them
    let cleanedName = editedEventLog.trim().replace(/\.(csv|xes)$/i, "");

    // Re-append .csv before saving
    const finalFilename = `${cleanedName}.csv`;

    try {
      await updateEventLogName(userSettings.username, editingEventLogId, finalFilename);
      setEventLogs(prevLogs =>
        prevLogs.map(log =>
          log.event_log_id === editingEventLogId
            ? { ...log, filename: cleanedName }
            : log
        )
      );
      showPopup("success", "Successfully update event log.");
      setEditingEventLogId(null);
      setEditedEventLog("");
    } catch (error) {
      showPopup("error", "Failed to update event log. Please try again.");
      console.error(error);
    }
  };

  /**
   * Updates the states to handle cancle
   */
  const handleCancelEdit = () => {
    setEditingEventLogId(null);
    setEditedEventLog("");
  };

  /**
   * Visually display a message to tell the user that its loading
   */
  if (loading) {
    return <div>Loading event logs...</div>;
  }

  return (
    <div>
      {/* Search Input */}
      <div>
        <Input
          placeholder="Search by ID or filename..."
          value={searchTerm}
          onInput={handleSearch} // Use onInput for real-time search but there is an error.
          ref={inputRef}
          style={{ width: "100%" }}
        />
      </div>

      {/* Scrollable Table */}
      <div style={{ maxHeight: "50vh", overflowY: "auto" }}>
        <Table
          headerRow={
            <TableHeaderRow sticky>
              <TableHeaderCell width="2rem">
                <span>ID</span>
              </TableHeaderCell>
              <TableHeaderCell minWidth="15rem">
                <span>Name</span>
              </TableHeaderCell>
            </TableHeaderRow>
          }
          rowActionCount={2}
        >
          { /* Table Rows which event are ordering by ID*/}
          {filteredLogs.slice(0, visibleCount).map((log) => (
            <TableRow
              key={log.event_log_id}
              data-event-log-id={log.event_log_id}
              onClick={() => handleRowClick(log.event_log_id)}
              actions={
                editingEventLogId === log.event_log_id ? (
                  <>
                    {/* Edit mode */}
                    <TableRowAction icon="accept" onClick={handleSaveEdit} />
                    <TableRowAction icon="decline" onClick={handleCancelEdit} />
                  </>
                ) : (
                  <>
                    {/* Normal mode */}
                    <TableRowAction icon="edit" onClick={() => handleEdit(log.event_log_id)} />
                    <TableRowAction icon="delete" onClick={() => handleDelete(log.event_log_id)} />
                  </>
                )
              }
              className="listRow"
              style={{
                backgroundColor: log.event_log_id === selectedEventLogId ? "#bde0fe" : undefined
              }}
            >
              <TableCell>
                <span>{log.event_log_id}</span>
              </TableCell>
              <TableCell>
                {editingEventLogId === log.event_log_id ? (
                  <Input
                    value={editedEventLog}
                    onInput={(e: any) => setEditedEventLog(e.target.value)}
                    style={{ width: "100%" }}
                  />
                ) : (
                  <span>{log.filename}</span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </Table>
      </div>

      {/* Load More Button */}
      {visibleCount < filteredLogs.length && (
        <div style={{ textAlign: "center", padding: "5px" }}>
          <Button onClick={handleLoadMore}>Load More</Button>
        </div>
      )}

      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />
    </div>
  );
};

export default EventTable;
