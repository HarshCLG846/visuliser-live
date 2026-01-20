import React from 'react'
import './DetectionResultsPanel.css'

function DetectionResultsPanel({ analysisResults, isValidImage }) {
  if (!analysisResults || !isValidImage) {
    return null
  }

  const regions = analysisResults.image_analysis || {}

  return (
    <div className="detection-results-panel">
      <div className="results-header">
        <h3>Detection Summary</h3>
      </div>
      <div className="results-content">
        {Object.entries(regions).map(([region, data]) => (
          <div key={region} className="result-item">
            <span className={`result-status ${data.detected ? 'detected' : 'not-detected'}`}>
              {data.detected ? '✓' : '✗'} {region.replace('_', ' ')}
            </span>
            {data.detected && (
              <span className="result-confidence" style={{ marginLeft: '8px' }}>
                {Math.round(data.confidence * 100)}%
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default DetectionResultsPanel

