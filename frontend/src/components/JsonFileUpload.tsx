import React, { useRef, useState, DragEvent } from 'react';
import { Icon } from '@ui5/webcomponents-react';
import { PopupMessage } from './PopupMessage';
import { usePopup } from '../hooks/usePopup';
import '@ui5/webcomponents-icons/dist/upload.js';
import '../assets/styles/FileUpload.css';

interface JsonFileUploadProps {
  onFileSelected: (file: File) => void;
}

/**
 * This file is used in AgentSimConfig.tsx
 * 
 * JsonFileUpload component allows users to upload a `.json` file 
 * via drag-and-drop or by clicking to open the file dialog.
 * It validates the file type, displays the selected file name, 
 * and shows error messages using a popup if an invalid file is uploaded.
 * 
 * @component
 * @param {function} onFileSelected - Callback function triggered when a valid JSON file is selected.
 */
const JsonFileUpload: React.FC<JsonFileUploadProps> = ({ onFileSelected }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  const validateFile = (file: File) => {
    if (file && file.name.endsWith('.json')) {
      setSelectedFile(file);
      onFileSelected(file);
    } else {
      showPopup('error', 'Please upload a valid JSON file.');
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
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
    const file = e.target.files?.[0];
    if (file) {
      validateFile(file);
    }
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
        <p>
          <Icon name="upload" />
          <br />
          <span className="upload-text">
            <strong>Drag & Drop</strong> your JSON file here
            <br />
            or <strong>Click to Upload</strong>
          </span>
          <br />
          <span className="upload-subtext">(Only .json files are supported)</span>
        </p>
      </div>

      <input
        type="file"
        accept=".json"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      {selectedFile && (
        <div className="selected-file">
          Selected file: <strong>{selectedFile.name}</strong>
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

export default JsonFileUpload;
