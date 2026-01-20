import React, { useRef } from 'react'
import './RightActionSidebar.css'

function RightActionSidebar({ onImageUpload, onReset, onViewToggle, onDownload, isAnalyzing, hasAnalysis, viewMode, isEditing, hasImage, hasSelectedItems, isValidImage }) {
  const fileInputRef = useRef(null)

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      onImageUpload(file)
    }
  }

  const handleReset = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    if (onReset) {
      onReset()
    }
  }

  return (
    <div className="right-action-sidebar">
      <div className="action-header">
        <h3>Actions</h3>
      </div>
      <div className="action-content">
        <div className="action-list">
          <button
            className="action-button secondary-button upload-button"
            onClick={handleUploadClick}
            title="Upload Image"
          >
            <span className="action-icon">📤</span>
            <span className="action-label">Upload</span>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />

          <button
            className="action-button primary-button"
            onClick={onViewToggle}
            title={viewMode === 'original' ? "View Edited" : "View Original"}
            disabled={!hasImage || !hasSelectedItems || isAnalyzing || isEditing}
          >
            <span className="action-icon">{viewMode === 'original' ? '👁️' : '🔄'}</span>
            <span className="action-label">{viewMode === 'original' ? 'View' : 'Original'}</span>
          </button>

          <button
            className="action-button secondary-button"
            onClick={handleReset}
            title="Reset"
          >
            <span className="action-icon">↺</span>
            <span className="action-label">Reset</span>
          </button>

          {viewMode === 'edited' && (
            <button
              className="action-button secondary-button download-button"
              onClick={onDownload}
              title="Download Edited Image"
              disabled={isAnalyzing || isEditing}
            >
              <span className="action-icon">💾</span>
              <span className="action-label">Download</span>
            </button>
          )}

          {(isAnalyzing || isEditing) && (
            <div className="analyzing-indicator">
              <span className="analyzing-text">
                {isAnalyzing ? 'Analyzing...' : 'Editing image...'}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RightActionSidebar

