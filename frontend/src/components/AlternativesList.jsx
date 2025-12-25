import React from 'react'

const AlternativesList = ({ recommendations, loading, error }) => {
  const formatClassName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (loading) {
    return (
      <div className="alternatives-list loading">
        <div className="spinner"></div>
        <p>Finding alternatives...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="alternatives-list error">
        <p className="error-message">❌ {error}</p>
      </div>
    )
  }

  console.log('AlternativesList render:', { recommendations, loading, error })
  
  if (!recommendations) {
    console.log('No recommendations object')
    return null
  }

  if (!recommendations.suggestions || recommendations.suggestions.length === 0) {
    console.log('No suggestions in recommendations:', recommendations)
    return (
      <div className="alternatives-list">
        <h3>Lower-Calorie Alternatives</h3>
        <p className="alternatives-subtitle">
          No lower-calorie alternatives found for this food item. 
          <br />
          Predicted: {recommendations.pred_class} ({recommendations.pred_calories_per_100g?.toFixed(0)} kcal/100g)
          <br />
          Try a different image or the food might already be relatively low in calories.
        </p>
      </div>
    )
  }

  return (
    <div className="alternatives-list">
      <h3>Lower-Calorie Alternatives</h3>
      <p className="alternatives-subtitle">
        Similar foods with fewer calories (per 100g)
      </p>
      <div className="alternatives-grid">
        {recommendations.suggestions.map((suggestion, index) => (
          <div key={index} className="alternative-item">
            <div className="alternative-header">
              <span className="alternative-name">{formatClassName(suggestion.class)}</span>
              <span className="similarity-badge">
                {(suggestion.similarity * 100).toFixed(0)}% similar
              </span>
            </div>
            <div className="alternative-stats">
              <div className="calorie-info">
                <span className="calorie-value">{suggestion.calories_per_100g.toFixed(0)} kcal</span>
                <span className="calorie-drop">-{suggestion.calorie_drop.toFixed(0)} kcal</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AlternativesList

