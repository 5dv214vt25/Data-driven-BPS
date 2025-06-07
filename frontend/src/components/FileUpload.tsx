import React, { useRef, useState, DragEvent } from 'react';
import { Button, Icon } from '@ui5/webcomponents-react';
import { PopupMessage } from './PopupMessage';
import { usePopup } from '../hooks/usePopup';
import { useUser } from '../context/userContext'; // Import the UserContext <-- IMPORTANT
import '@ui5/webcomponents-icons/dist/upload.js';
import { CsvDisplayDataRef } from './CsvDisplayData';
import { useCreateReorderedData } from '../hooks/useCreateReorderedData';
import { xesToCsv } from '../api/controllerAPICalls/EventLogAPICalls';
import { Loader } from '@ui5/webcomponents-react-compat/dist/components/Loader/index.js';
import '../assets/styles/FileUpload.css';


/**
 * FileUpload handles the logic for uploading CSV/XES 
 * and controls the drag and drop for changing file structures.
 * 
 * 
 * Props:
 *  -onFileSelected: Called after a file is selected or converted.
 *  -onFileSave: Handles saving the file.
 *  -onUpload: Called after a succesful upload.
 *  -csvRef: Ref to CSV display component for resetting or validations. 
 *  -onCancel: Resets any unsaved state on cancel. 
 */

interface FileUploadProps {
  onFileSelected: (file: File) => void;
  onFileSave: (file: File, userId: string, safe: boolean) => Promise<boolean | undefined>;
  onUpload: (val: boolean) => void;
  csvRef: React.RefObject<CsvDisplayDataRef | null>;
  onCancel: () => void;
}

/**
 * Represents the mapping between original and new CSV column name and order.
 */
type ColumnMapping = {
  originalIndex: number;
  newIndex: number;
  newName: string;
  oldName: string;
};

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelected, onFileSave, csvRef, onCancel, onUpload }) => {
  const [isDisabled, setIsDisabled] = useState(false);
  const [onLoading, setOnLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();
  const { userSettings } = useUser();
  const [xesconvertion, setXesConvertion] = useState(false);

  const { createNewOrderedCsvFile } = useCreateReorderedData();

  const requiredHeaders = ['case_id', 'resource', 'activity', 'start_time', 'end_time'];
  const containsCorrectHeaders = (cols: string[]): boolean => {
    return requiredHeaders.every(header => cols.includes(header));
  };

  const validateFile = async (file: File) => {
    setOnLoading(true);

    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file);
      onFileSelected(file);
    } else if (file && file.name.endsWith('.xes')) {
      // Set this to make it clear for the user that xes to csv convertion is happening
      setXesConvertion(true);

      const prop = await xesToCsv(file);
      if (prop.success && prop.file) {
        setSelectedFile(prop.file);
        onFileSelected(prop.file);
      } else {
        showPopup('error', 'Please upload a valid CSV or XES file');
      }

      setXesConvertion(false);
    } else {
      showPopup('error', 'Please upload a valid CSV/XES file.');
    }

    setOnLoading(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);

    if (csvRef.current) {
      csvRef.current.reset();
    }
    onCancel();

    localStorage.removeItem("columnMapping");
    localStorage.removeItem("originalCsvColumns");
    localStorage.removeItem("csvData");

    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateFile(file);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (csvRef.current) {
      csvRef.current.reset();
    }
    onCancel();

    localStorage.removeItem("columnMapping");
    localStorage.removeItem("originalCsvColumns");
    localStorage.removeItem("csvData");

    const file = e.target.files?.[0];
    if (file) {
      validateFile(file);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSave = async () => {
    setIsDisabled(true);
    setOnLoading(true);


    if (!userSettings.username || !selectedFile) {
      showPopup('error', 'Please provide a user ID and upload a CSV file.');
      return;
    }

    // From the localStorage get the columnMapping and the originalCsvColumnOrder and check that it changed
    const columnMapping = JSON.parse(localStorage.getItem('columnMapping') || '[]');
    const headers = columnMapping.map((c: ColumnMapping) => c.newName);
    const oldCsv = JSON.parse(localStorage.getItem('originalCsvColumns') || '[]');

    if (JSON.stringify(headers) === JSON.stringify(oldCsv)) {
      const csvFile = await createNewOrderedCsvFile(selectedFile);
      const success = await onFileSave(csvFile, userSettings.username, true);
      if (success) {
        onUpload(true);
        setSelectedFile(null);
      }
    } else {
      if (containsCorrectHeaders(headers)) {
        if (csvRef.current) {
          try {
            const csvFile = await createNewOrderedCsvFile(selectedFile);
            const success = await onFileSave(csvFile, userSettings.username, true);
            if (success) {
              onUpload(true);
              setSelectedFile(null);
            }
          } catch (err) {
            showPopup("error", JSON.stringify(err));
          }
        } else {
          showPopup("error", "Unexpected error happened. Please try again later.");
        }
      } else {
        showPopup("error", "Missing column name. Please manually check the header names.");
        await onFileSave(selectedFile, userSettings.username, false);
      }
    }
    setIsDisabled(false);
    setOnLoading(false);
  };

  const handleCancel = () => {
    setSelectedFile(null);
    onCancel(); // Clear csvData when the cancel button is clicked

    if (csvRef.current) {
      csvRef.current.reset();
    }

    //Remove the data from the localStorage
    localStorage.removeItem("columnMapping");
    localStorage.removeItem("originalCsvColumns");
    localStorage.removeItem("csvData");
  };

  return (
    <div className="file-upload-container">
      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        {selectedFile ? (
          <p>
            <Icon name="document" />
            <br />
            <span className="upload-text">
              <strong style={{ color: '#4682B4' }}>{selectedFile.name.replace(/\.[^/.]+$/, ' ')}</strong>
              <br />
              Click to change file
            </span>
          </p>
        ) : (
          <p>
            <Icon name="upload" />
            <br />
            <span className="upload-text">
              <strong>Drag & Drop</strong> your CSV/XES file here
              <br />
              or <strong>Click to Upload</strong>
            </span>
            <br />
            <span className="upload-subtext">(Only .csv and .xes files are supported)</span>
          </p>
        )}

        {onLoading && (
          <Loader
            progress="60%"
            type="Indeterminate"
            style={{
              width: '90%',
              height: '10px',
              borderRadius: '1rem'
            }}
          />
        )}

        {xesconvertion && (
          <span className="upload-subtext" style={{ color: '#4682B4' }}>Converting XES-file to CSV</span>
        )}
      </div>

      <input
        type="file"
        accept=".csv, .xes"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      <PopupMessage
        show={!!popupMessage}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={closePopup}
      />

      <div className="button-row">
        <Button onClick={handleSave} disabled={!selectedFile || isDisabled}>
          Upload
        </Button>
        <Button onClick={handleCancel} disabled={!selectedFile}>
          Cancel
        </Button>
      </div>
    </div>
  );
};

export default FileUpload;
