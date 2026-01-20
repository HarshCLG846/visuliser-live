import React from 'react'
import './ImageCanvas.css'

function ImageCanvas({ houseImage, hasSubPanel, analysisResults, isAnalyzing, apiError, apiConnected, viewMode, isEditing, hasSelectedItems }) {
  // Determine image state
  const isInvalidImage = analysisResults && analysisResults.valid_exterior_image === false
  const isValidAnalyzed = analysisResults && analysisResults.valid_exterior_image === true
  const isImageUploaded = !!houseImage
  const showAnalysisResults = isValidAnalyzed && !isAnalyzing

  return (
    <div className={`image-canvas ${hasSubPanel ? 'has-sub-panel' : ''}`}>
      <div className="canvas-container">
        {!isImageUploaded ? (
          // Case 1: No image
          <div className="placeholder-content">
            <div className="placeholder-icon">🏠</div>
            <p className="placeholder-text">
              Upload your exterior photo
            </p>
            <p className="placeholder-subtext">
              Supports JPG & PNG · Best results with daylight photos
            </p>
          </div>
        ) : isInvalidImage ? (
          // Case 3: Invalid image
          <div className="image-wrapper invalid-image">
            <img
              src={houseImage}
              alt="Invalid"
              className="house-image dimmed"
            />
            <div className="invalid-overlay">
              <div className="invalid-icon">⚠️</div>
              <p className="invalid-text">Not a house exterior</p>
              <p className="invalid-subtext">Upload a valid house or garage image</p>
            </div>
          </div>
        ) : (
          // Case 2 & 4: Valid image (analyzed or not)
          <div className="canvas-content">
            {viewMode === 'edited' && !isEditing && (
              <div className="view-mode-header">
                <span>✏️ Edited View</span>
              </div>
            )}

            <div className="image-wrapper">
              <img
                src={houseImage}
                alt="House/Garage"
                className="house-image"
              />
              {!showAnalysisResults && !isAnalyzing && !isEditing && hasSelectedItems && (
                <div className="instruction-overlay">
                  <p>Select products and click View to analyze</p>
                </div>
              )}
              {(isAnalyzing || isEditing) && (
                <div className="analysis-overlay">
                  <div className="loading-spinner">⏳</div>
                  <p>{isAnalyzing ? 'Analyzing image...' : 'Editing image...'}</p>
                </div>
              )}
              {apiError && (
                <div className="error-overlay">
                  <p className="error-message">⚠️ {apiError}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ImageCanvas

