import React, { useState, useRef } from 'react';
import './VideoUploader.css';

const VideoUploader = () => {
  const [file, setFile] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [originalFilename, setOriginalFilename] = useState('');
  const [currentStep, setCurrentStep] = useState('');
  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const uploadAndProcess = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setStatus('uploading');
      setError(null);
      setProgress(0);

      const response = await fetch('/upload-and-process/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setTaskId(result.task_id);
      setOriginalFilename(result.original_filename);
      setStatus('processing');
      
      // Start polling for progress
      pollProgress(result.task_id);
    } catch (err) {
      setError(err.message || 'Upload failed');
      setStatus('error');
    }
  };

  const pollProgress = async (taskId) => {
    const poll = async () => {
      try {
        const response = await fetch(`/status/${taskId}`);
        const data = await response.json();

        if (data.status === 'SUCCESS') {
          setStatus('completed');
          setProgress(100);
          setCurrentStep('Processing complete!');
        } else if (data.status === 'FAILURE') {
          setError(data.error || 'Processing failed');
          setStatus('error');
        } else if (data.status === 'PROGRESS') {
          setProgress(data.progress || 0);
          setCurrentStep(data.step || 'Processing...');
          setTimeout(poll, 1000); // Poll every second
        } else {
          setTimeout(poll, 1000);
        }
      } catch (err) {
        setError('Failed to check status');
        setStatus('error');
      }
    };

    poll();
  };

  const downloadVideo = () => {
    window.open(`/download/${taskId}`, '_blank');
  };

  const resetUploader = () => {
    setFile(null);
    setTaskId(null);
    setStatus('idle');
    setProgress(0);
    setError(null);
    setOriginalFilename('');
    setCurrentStep('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.type.startsWith('video/')) {
        setError('Please select a video file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  return (
    <div className="video-uploader">
      <div className="upload-card">
        <h2>Upload Video</h2>
        
        {status === 'idle' && (
          <div className="upload-section">
            <div className="file-input-wrapper">
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileChange}
                className="file-input"
                id="video-upload"
              />
              <label htmlFor="video-upload" className="file-input-label">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="m14 2 6 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <path d="M12 18v-6"/>
                  <path d="m9 15 3-3 3 3"/>
                </svg>
                {file ? 'Change Video' : 'Choose Video File'}
              </label>
            </div>
            
            {file && (
              <div className="file-info">
                <p><strong>Selected:</strong> {file.name}</p>
                <p><strong>Size:</strong> {formatFileSize(file.size)}</p>
                <p><strong>Type:</strong> {file.type}</p>
              </div>
            )}
            
            <button
              onClick={uploadAndProcess}
              disabled={!file}
              className="upload-button"
            >
              Upload & Process Video
            </button>
          </div>
        )}

        {status === 'uploading' && (
          <div className="status-section">
            <div className="spinner"></div>
            <p>Uploading video...</p>
          </div>
        )}

        {status === 'processing' && (
          <div className="status-section">
            <h3>Processing Video</h3>
            <p><strong>File:</strong> {originalFilename}</p>
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <span className="progress-text">{progress}%</span>
            </div>
            {currentStep && <p className="current-step">{currentStep}</p>}
          </div>
        )}

        {status === 'completed' && (
          <div className="status-section success">
            <div className="success-icon">✓</div>
            <h3>Processing Complete!</h3>
            <p>Your video has been processed successfully.</p>
            <div className="button-group">
              <button onClick={downloadVideo} className="download-button">
                Download Processed Video
              </button>
              <button onClick={resetUploader} className="reset-button">
                Process Another Video
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="status-section error">
            <div className="error-icon">⚠</div>
            <h3>Error</h3>
            <p>{error}</p>
            <button onClick={resetUploader} className="reset-button">
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoUploader;
