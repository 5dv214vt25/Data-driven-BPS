import React, { useRef, useState } from 'react';
import { Button, Input } from '@ui5/webcomponents-react';
import { PopupMessage } from './PopupMessage';

interface CsvUploadProps {
  onFileSelected: (file: File) => void;
  onFileSave: (file: File, userId: string) => void;
}

/**
 * This file is currently not used 4/5 2025.
 * 
 * CsvUpload component allows users to upload and save a CSV file along with a user ID.
 * It provides validation for file format, displays the selected file, and shows error messages using a popup.
 *
 * @component
 * @param {function} onFileSelected - Callback function triggered when a valid CSV file is selected.
 * @param {function} onFileSave - Callback function triggered when the user clicks save with a valid file and user ID.
 */
const CsvUpload: React.FC<CsvUploadProps> = ({ onFileSelected, onFileSave }) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [userId, setUserId] = useState<string>('');
  const [showPopup, setShowPopup] = useState(false);
  const [popupMessage, setPopupMessage] = useState('');
  const [popupType, setPopupType] = useState<'success' | 'error'>('error');

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const activateError = (errorMessage: string)=>{
    setPopupType('error');
    setPopupMessage(errorMessage);
    setShowPopup(true);
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file);
      onFileSelected(file);
    } else {
      activateError("Please upload a valid CSV file");
    }
  };

  const handleSaveClick = () => {
    if (!userId) {
      activateError("Please upload a valid CSV file.");
      return;
    }
    if (selectedFile) {
      onFileSave(selectedFile, userId);
    } else {
      activateError("Please upload a valid CSV file.")
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <input
        type="file"
        accept=".csv"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
        data-testid="file-input"
      />

      <Button onClick={handleUploadClick}>Upload CSV</Button>

      <Input
        placeholder="Enter User ID"
        value={userId}
        onInput={(e: any) => setUserId(e.target.value)}
      />

      <Button onClick={handleSaveClick} disabled={!selectedFile}>
        Save
      </Button>

      <PopupMessage
        show={showPopup}
        type={popupType}
        message={popupMessage}
        duration={4000}
        onClose={() => setShowPopup(false)}
      />
      
      {selectedFile && (
        <div style={{ marginTop: '10px', fontSize: '14px' }}>
          Selected file: <strong>{selectedFile.name}</strong>
        </div>
      )}
    </div>
  );
};

export default CsvUpload;

