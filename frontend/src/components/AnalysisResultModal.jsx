import React from 'react'
import './AnalysisResultModal.css'

function AnalysisResultModal({ isOpen, onClose, analysisResults, isAnalyzing, apiError }) {
  if (!isOpen) return null

  const isValid = analysisResults?.valid_exterior_image === true
  const reason = analysisResults?.reason
  const regions = analysisResults?.image_analysis || {}

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Analysis Results</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {isAnalyzing ? (
            <div className="loading-state">
              <div className="spinner">⏳</div>
              <p>Analyzing image with Gemini AI...</p>
            </div>
          ) : apiError ? (
            <div className="error-state">
              <div className="status-icon error">❌</div>
              <h3>Error</h3>
              <p className="error-text">{apiError}</p>
            </div>
          ) : !analysisResults ? (
            <div className="no-results">
              <p>No analysis results available.</p>
            </div>
          ) : !isValid ? (
            <div className="invalid-result">
              <div className="status-icon invalid">⚠️</div>
              <h3>Invalid Image</h3>
              <p className="reason-text">{reason || "Uploaded image is not a house or garage exterior"}</p>
              <p className="help-text">Please upload a valid house or garage exterior image.</p>
            </div>
          ) : (
            <div className="valid-result">
              <div className="status-icon valid">✅</div>
              <h3>Valid House/Garage Image</h3>
              <p className="success-text">Image successfully analyzed!</p>
              
              <div className="detection-summary">
                <h4>Detection Summary</h4>
                <div className="regions-list">
                  {Object.entries(regions).map(([region, data]) => (
                    <div key={region} className="region-item">
                      <div className="region-header">
                        <span className={`region-status ${data.detected ? 'detected' : 'not-detected'}`}>
                          {data.detected ? '✓' : '✗'} {region.replace('_', ' ').toUpperCase()}
                        </span>
                        {data.detected && (
                          <span className="confidence-badge">
                            {Math.round(data.confidence * 100)}%
                          </span>
                        )}
                      </div>
                      {data.detected ? (
                        <div className="region-details">
                          <span className="detail-item">Visibility: {data.visibility || 'N/A'}</span>
                          {data.bounding_box && (
                            <span className="detail-item">
                              BBox: [{data.bounding_box[0].toFixed(2)}, {data.bounding_box[1].toFixed(2)}, {data.bounding_box[2].toFixed(2)}, {data.bounding_box[3].toFixed(2)}]
                            </span>
                          )}
                        </div>
                      ) : (
                        <div className="region-reason">
                          <span className="reason-text">{data.reason || 'Not detected'}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="close-button" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  )
}

export default AnalysisResultModal

