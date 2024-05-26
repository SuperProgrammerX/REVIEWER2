import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import './styles.css';
import logo from './logo.svg';
import TypingText from './components/TypingText';
import FileUploadWithSpinner from './components/FileUploadWithSpinner';
import SlidingSwitch from './components/SlidingSwitch';
import { API_BASE_URL } from './config';

/**
 * Main application component.
 */
function App() {
  // State variables to manage the application state
  const [messages, setMessages] = useState([]); // List of messages
  const [fileObject, setFileObject] = useState(null); // Selected file
  const [paperContent, setPaperContent] = useState(null); // Content of the paper from the file
  const [promptData, setPromptData] = useState(null); // Generated prompt data
  const [editPromptData, setEditPromptData] = useState(''); // Editable prompt data
  const [isEditingPrompt, setIsEditingPrompt] = useState(false); // Editing state for prompt
  const [reviewData, setReviewData] = useState(null); // Generated review data
  const [isReviewButtonEnabled, setIsReviewButtonEnabled] = useState(false); // State to enable/disable review button
  const [isGeneratingPrompt, setIsGeneratingPrompt] = useState(false); // Loading state for generating prompt
  const [isGeneratingReview, setIsGeneratingReview] = useState(false); // Loading state for generating review
  const [version, setVersion] = useState('default'); // Version state ('default' or other)

  /**
   * Handles version change event.
   * @param {string} newVersion - The new version selected.
   */
  const handleVersionChange = (newVersion) => {
    setVersion(newVersion);
  };

  /**
   * Handles file selection event.
   * @param {string} name - The name of the file.
   * @param {File} file - The selected file object.
   * @param {Object} response_data - Additional response data.
   */
  const handleFileSelected = (name, file, response_data) => {
    setFileObject(file);
    setIsReviewButtonEnabled(false);
  };

  /**
   * Clears the selected file and related data.
   */
  const onFileClear = () => {
    setFileObject(null);
    setPromptData(null);
    setEditPromptData('');
    setIsEditingPrompt(false);
    setReviewData(null);
    setIsReviewButtonEnabled(false);
  };

  /**
   * Generates a prompt from the selected file.
   */
  const generatePrompt = async () => {
    if (!fileObject) return;
    setIsGeneratingPrompt(true);
    const formData = new FormData();
    formData.append('pdfFile', fileObject);
    formData.append('version', version);

    try {
      const response = await axios.post(`${API_BASE_URL}/submit-pdf-text`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPromptData(response.data.gen_prompt);
      setPaperContent(response.data.paper_content);
      setFileObject(null);
      setIsEditingPrompt(false);
      setIsReviewButtonEnabled(true);
    } catch (error) {
      console.error('Error fetching analysis result:', error);
    } finally {
      setIsGeneratingPrompt(false);
    }
  };

  /**
   * Enables editing of the prompt.
   */
  const handleEditPrompt = () => {
    setEditPromptData(promptData);
    setIsEditingPrompt(true);
  };

  /**
   * Cancels the editing of the prompt.
   */
  const handleCancelEdit = () => {
    setIsEditingPrompt(false);
  };

  /**
   * Saves the edited prompt.
   */
  const handleSaveEdit = () => {
    setPromptData(editPromptData);
    setIsEditingPrompt(false);
  };

  /**
   * Handles changes in the editable prompt textarea.
   * @param {Event} e - The change event.
   */
  const handleChangeEditPrompt = (e) => {
    setEditPromptData(e.target.value);
  };

  /**
   * Generates a review from the prompt and paper content.
   */
  const generateReview = async () => {
    if (!promptData || !paperContent) return;
    setIsGeneratingReview(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-review`, {
        paper_content: paperContent,
        prompt: promptData,
        version: version
      }, {
        headers: { 'Content-Type': 'application/json' },
      });
      setReviewData(response.data.gen_review);
      setMessages([...messages, { id: messages.length + 1, sender: 'llm', content: response.data.gen_review }]);
      setIsReviewButtonEnabled(false);
    } catch (error) {
      console.error('Error generating review:', error);
    } finally {
      setIsGeneratingReview(false);
    }
  };

  return (
    <div className="app-container">
      <div className="chat-history">
        <label className="history-label">Question Prompts:</label>
        <ul className="chat-history-list">
          <li id="gen_prompt" className="prompt-item">
            {isEditingPrompt ? (
              <textarea
                className="prompt-textarea"
                value={editPromptData}
                onChange={handleChangeEditPrompt}
              />
            ) : (
              promptData ? (
                <textarea
                  className="prompt-textarea"
                  value={promptData}
                  readOnly
                />
              ) : (
                <div
                  className="prompt-textarea"
                  dangerouslySetInnerHTML={{
                    __html: '<b>✦ No prompts available ✦</b><br><br><b>Default Version:</b><br>Concise and elegant prompts and reviews.<br><b>Detailed Version:</b><br>Detailed and elaborated prompts and reviews.<br><br><b>User Guide:</b><br>1. Select your PDF file;<br>2. Press \'Generate Prompt\';<br>3. Edit your prompts (optional);<br>4. Press \'Generate Review\'.'
                  }}
                />
              )
            )}
            {promptData && (
              <div className="edit-buttons">
                {isEditingPrompt ? (
                  <>
                    <button onClick={handleSaveEdit} style={{ color: 'green' }}>✔️</button>
                    <button onClick={handleCancelEdit}>❌</button>
                  </>
                ) : (
                  <button onClick={handleEditPrompt} className="edit-prompt">🖊️</button>
                )}
              </div>
            )}
          </li>
          <li className="chat-item">
            <FileUploadWithSpinner selectedfile={fileObject} onGetData={handleFileSelected} onFileClear={onFileClear} />
            <button
              className={isGeneratingPrompt ? 'button-loading' : (!fileObject ? 'button-disabled' : '')}
              onClick={generatePrompt}
              disabled={!fileObject || isGeneratingPrompt}
            >
              {isGeneratingPrompt ? (
                <>
                  <span className="loading-text-prompt">This process should take<br />around 1 minute</span>
                  <div className="spinner"></div>
                </>
              ) : 'Generate Prompt'}
            </button>
          </li>
        </ul>
      </div>
      <div className="chat-window">
        <div className="chat-window-header">
          <div className="header-content">
            <div className="logo">
              <img src={logo} className="App-logo" alt="logo" />
            </div>
            <h2>Reviewer2</h2>
            <SlidingSwitch onVersionChange={handleVersionChange} />
          </div>
          <p className="app-description">A Two-Stage LLM Framework for Academic Peer Review Generation</p>
        </div>
        <div className="message-list">
          <ul className="message-list">
            {messages.map((message) => (
              <li key={message.id} className="message-item">
                <div className={`message-item-content message-received`}>
                  <TypingText text={message.content} />
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div className="message-input">
          <button
            onClick={generateReview}
            className={isGeneratingReview ? 'button-loading' : (!isReviewButtonEnabled ? 'button-disabled' : '')}
            disabled={!isReviewButtonEnabled || isGeneratingReview}
          >
            {isGeneratingReview ? (
              <span>Generating...</span>
            ) : 'Generate Review'}
          </button>
          {isGeneratingReview && (
            <div className="loading-text-review">This process should take around 20 seconds</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
