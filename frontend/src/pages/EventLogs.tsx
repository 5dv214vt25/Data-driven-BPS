import { useState, useRef } from 'react';
import CsvDisplayData from '../components/CsvDisplayData';
import { PopupMessage } from '../components/PopupMessage';
import FileUpload from '../components/FileUpload';
import EventTable from '../components/EventTable';
import { useUser } from "../context/userContext";
import type { CsvDisplayDataRef } from '../components/CsvDisplayData';
import { useCsvReader } from '../hooks/useCsvReader';
import { uploadEventLog } from '../api/simulationAPI';
import { SegmentedButton, SegmentedButtonItem, Button } from '@ui5/webcomponents-react';
import { useNavigate } from "react-router-dom";

import "../assets/styles/eventLogs.css";

/**
 * EventLogs component for managing and displaying event logs.
 * 
 * Allows users to upload an event log CSV file, which is then processed and displayed.
 * 
 * @component
 */
function EventLogs() {
  const { csvData, columns, rowNumber, handleCSVUpload, resetCsvData } = useCsvReader();
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [popupType, setPopupType] = useState<'success' | 'error'>('error');
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);
  const { userSettings } = useUser();
  const csvRef = useRef<CsvDisplayDataRef>(null);
  const [reloadFlag, setReloadFlag] = useState(0);
  const [selectedSegment, setSelectedSegment] = useState<'upload' | 'list'>('upload');
  const [uploaded, setUploaded] = useState(false);

  const navigate = useNavigate();

  /**
   * Handles the file selection process and sets the filename variable.
   * 
   * @function
   * @param file - The file to be uploaded.
   */
  const handleFileSelected = (file: File) => {
    setShowPopup(false);
    setSelectedFilename(file.name.replace(/\.[^/.]+$/, ' '));
    handleCSVUpload(file);
  };

  /**
   * Handles the file upload process.
   * 
   * @async
   * @function
   * @param file - The file to be uploaded.
   * @param userId - The user ID associated with the upload.
   * @param safe - Whether to perform the safe upload flow.
   */
  const handleFileUpload = async (file: File, userId: string, safe: boolean) => {
    if (safe) {
      const result = await uploadEventLog(file, userId);
      if (result.success) {
        setPopupType('success');
        setPopupMessage(`File uploaded successfully! Event Log ID: ${result.eventLogId}`);
        userSettings.selectedEventlogId = result.eventLogId || null;

        /* Save the returned ID into localStorage */
        localStorage.setItem("lastID", String(result.eventLogId));

        /* Force event list to refresh */
        setReloadFlag(prev => prev + 1);

        // Set the selected segment to list
        setSelectedSegment('list');

        setShowPopup(true);
        return true;
      } else {
        setPopupType('error');
        setPopupMessage(`Upload failed: ${result.message}`);
        setShowPopup(true);
        return false;
      }
    }
  };

  const handleSwitch = () => {
    csvRef.current?.reset();
    resetCsvData();
    setSelectedFilename(null);
    localStorage.removeItem('lastID');
  }

  /**
   * Generates 3 different components
   * - upload component and corresponding button
   * - view list of existing event logs
   * - overview over existing event log
   * 
   * @returns {JSX.Element}
   */
  return (
    <div className="container-wrapper">
      <div className='container-panel left-container'>

        {/* Toggle to display component that allows the user to upload files to the server */}
        <SegmentedButton className='eventlog-button-row' selectionMode='Single'>
          <SegmentedButtonItem
            className='upload-btn'
            selected={selectedSegment === 'upload'}
            onClick={() => {
              setUploaded(false);
              handleSwitch();
              setSelectedSegment('upload')
            }}
          >
            Upload New
          </SegmentedButtonItem>

          {/* Toggle to display component that allows the user to select an existing eventlog */}
          <SegmentedButtonItem
            className='list-btn'
            selected={selectedSegment === 'list'}
            onClick={() => {
              handleSwitch();
              setSelectedSegment('list')
            }}
          >
            Select Existing
          </SegmentedButtonItem>
        </SegmentedButton>

        {/* Toggle to display component that allows the user to upload files to the server */}
        {selectedSegment == 'upload' && (
          <div>
            <h2>Upload Event Log</h2>
            <FileUpload
              onFileSelected={handleFileSelected}
              onFileSave={handleFileUpload}
              csvRef={csvRef}
              onUpload={setUploaded}
              onCancel={() => {
                resetCsvData();
                setSelectedFilename(null);
                setUploaded(false);
              }}
            />
          </div>
        )}

        {/* Display the list of all existing event logs*/}
        {selectedSegment == 'list' && (
          <div>
            <h2>Event Logs List</h2>
            <EventTable
              onRowClick={(file) => {
                handleFileSelected(file);
                setUploaded(true);
              }}
              reloadFlag={reloadFlag}
              csvRef={csvRef}
              onRemoval={() => {
                resetCsvData();
                setSelectedFilename(null);
                setUploaded(false);
              }}
            />
          </div>
        )}
      </div>

      {/* Displays the content of an existing and selected eventlog */}
      <div className='container-panel right-container'>
        <h2>Event Log</h2>
        {selectedFilename && (
          <h3>
            Selected file:{' '}
            <span style={{ color: '#4682B4' }}>{selectedFilename}</span>
          </h3>
        )}

        <CsvDisplayData
          key={Date.now()}
          ref={csvRef}
          previewData={csvData}
          columns={columns}
          rowNumber={rowNumber}
        />

        {/* When the user has uploaded a file it is presented with a button to go discovery*/}
        {uploaded && (
          <div className='position_discovery_button'>
            <Button onClick={() => navigate("/discovery")}>Go to Discovery</Button>
          </div>
        )}
      </div>

      {/* Presents the success/error messages to the user */}
      <PopupMessage
        show={showPopup}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={() => setShowPopup(false)}
      />
    </div>
  );
}

export default EventLogs;

