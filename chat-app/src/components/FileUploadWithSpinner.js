import React, { useRef, useState } from 'react';
import { FaFilePdf, FaTimesCircle } from 'react-icons/fa';
import LoadingSpinner from './LoadingSpinner'; // Ensure this matches your actual LoadingSpinner component's path
import '../styles.css';
import axios from 'axios';

function FileUploadWithSpinner({ onGetData, onFileClear }) {
    const fileInputRef = useRef(null);
    const [isUploading, setIsUploading] = useState(false);
    const [selectedFileName, setSelectedFileName] = useState(''); // State to keep track of the selected file name
    const [tooltipText, setTooltipText] = useState('Please select a PDF paper to upload');

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFileName(file.name); // Update state with the selected file name
            setTooltipText(file.name); // Update tooltip text to the file name
            onGetData(file.name, file, null); // Notify parent about the file selection without uploading
        }
    };

    const clearFileSelection = () => {
        if (fileInputRef.current) {
            fileInputRef.current.value = ""; // Clear the input
            onFileClear(); // Notify the parent component that the file has been cleared
            setSelectedFileName(''); // Reset the selected file name state
            setTooltipText('Please select a PDF paper to upload'); // Reset the tooltip text
        }
    };

    return (
        <div className="custom-file-upload">
            <span className="tooltip-text">{tooltipText}</span>
            <label htmlFor="file-input" className="file-input-label">
                <FaFilePdf size="34" color='red' />
                {selectedFileName || 'Select File'} {/* Display the selected file name or 'Select File' */}
            </label>
            {selectedFileName && ( // Only show the 'cross' icon when a file is selected
                <FaTimesCircle className="file-clear-icon" onClick={clearFileSelection} title="Remove file" />
            )}
            <input
                ref={fileInputRef}
                id="file-input"
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={handleFileChange}
            />
            {isUploading && <LoadingSpinner />}
        </div>
    );
}

export default FileUploadWithSpinner;
