// FileUpload.js
import React, { useState } from 'react';
import { FaFilePdf } from 'react-icons/fa';
import '../styles.css';
import axios from 'axios';

function FileUpload({ onGetData }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [responsedata, setResponsedata] = useState('');

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setFileName(file.name);

      console.log('File Chosen:', file.name);

      const formData = new FormData();
      formData.append('pdfFile', file);

      try {
        axios.defaults.withCredentials = true;
        const response = await axios.post('http://localhost:3001/submit-pdf-text', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        setResponsedata(response.data)

        console.log('The file was uploaded successfully:', response.data);

        onGetData(file.name, file, response.data);

      } catch (error) {
        console.error('The file upload failed:', error);
      }
    }
  };



  return (
    <div className="custom-file-upload">
      <span className="tooltip-text">Please upload a pdf paper...</span>
      <label htmlFor="file-input"  >
        <FaFilePdf size="34" color='red' /> {fileName || ''}
      </label>
      <input
        id="file-input"
        type="file"
        accept=".pdf"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
    </div>

  );
}

export default FileUpload;