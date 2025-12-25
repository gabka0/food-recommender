import React from 'react'

const PredictionResults = ({ prediction, loading, error }) => {
  const formatClassName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <div className="prediction-results loading">
        <div className="spinner"></div>
        <p>Analyzing food image...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="prediction-results error">
        <p className="error-message">❌ {error}</p>
      </div>
    )
  }

  if (!prediction) {
    return null
  }

  const confidencePercent = (prediction.confidence * 100).toFixed(1)
  const top5 = prediction.top5_predictions || []

  return (
    <div className="prediction-results">
      <div className="prediction-header">
        <h2>Prediction Results</h2>
      </div>
      <div className="prediction-content">
        <div className="predicted-class">
          <span className="class-label">Top Prediction:</span>
          <span className="class-name">{formatClassName(prediction.predicted_class)}</span>
        </div>
        <div className="confidence">
          <span className="confidence-label">Confidence:</span>
          <span className="confidence-value">{confidencePercent}%</span>
        </div>
        
        {top5.length > 1 && (
          <div className="top5-predictions">
            <h4>Top 5 Predictions:</h4>
            <div className="top5-list">
              {top5.map((pred, index) => (
                <div key={index} className="top5-item">
                  <span className="rank">#{index + 1}</span>
                  <span className="top5-class-name">{formatClassName(pred.class)}</span>
                  <span className="top5-confidence">{(pred.confidence * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PredictionResults

