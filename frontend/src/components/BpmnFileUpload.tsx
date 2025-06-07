import React, { useRef, useState, DragEvent } from 'react';
import { Icon } from '@ui5/webcomponents-react';
import { PopupMessage } from './PopupMessage';
import { usePopup } from '../hooks/usePopup';
import '@ui5/webcomponents-icons/dist/upload.js';
import '../assets/styles/FileUpload.css';

interface BpmnFileUploadProps {
  onFileSelected: (file: File) => void;
}

/**
 * BpmnFileUpload component allows users to upload BPMN files via drag-and-drop or file selection.
 * It validates the file type, displays the selected file name, and shows an error popup for invalid uploads.
 * 
 * Component is used in AgentSimConfig.tsx
 *
 * @component
 * @param {function} onFileSelected - Callback function triggered with the selected BPMN file.
 */
const BpmnFileUpload: React.FC<BpmnFileUploadProps> = ({ onFileSelected }) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { message: popupMessage, type: popupType, showPopup, closePopup } = usePopup();

  const validateFile = (file: File) => {
    if (file && file.name.endsWith('.bpmn')) {
      setSelectedFile(file);
      onFileSelected(file);
    } else {
      showPopup('error', 'Please upload a valid BPMN file.');
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
            <strong>Drag & Drop</strong> your BPMN file here
            <br />
            or <strong>Click to Upload</strong>
          </span>
          <br />
          <span className="upload-subtext">(Only .bpmn files are supported)</span>
        </p>
      </div>

      <input
        type="file"
        accept=".bpmn"
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

export default BpmnFileUpload;
