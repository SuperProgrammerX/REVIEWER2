import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ isLoading = true, text = "File parsing..." }) => {
  return (
    <div>
      {(
        <div className="loading-spinner">
          <div className="loading-content">
            <div className="spinner"></div>
            {isLoading && <p className="loading-text">{text}</p>}
          </div>
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;