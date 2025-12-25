import React from 'react'

const NutritionDisplay = ({ nutrition, loading }) => {
  if (loading || !nutrition) {
    return null
  }

  const nutritionItems = [
    { key: 'calories', label: 'Calories', unit: 'kcal', icon: '🔥' },
    { key: 'protein', label: 'Protein', unit: 'g', icon: '💪' },
    { key: 'fat', label: 'Fat', unit: 'g', icon: '🧈' },
    { key: 'carbs', label: 'Carbs', unit: 'g', icon: '🍞' },
    { key: 'sugars', label: 'Sugars', unit: 'g', icon: '🍬' },
    { key: 'sodium', label: 'Sodium', unit: 'mg', icon: '🧂' },
  ]

  return (
    <div className="nutrition-display">
      <h3>Nutrition (per 100g)</h3>
      <div className="nutrition-grid">
        {nutritionItems.map((item) => (
          <div key={item.key} className="nutrition-item">
            <div className="nutrition-icon">{item.icon}</div>
            <div className="nutrition-info">
              <span className="nutrition-label">{item.label}</span>
              <span className="nutrition-value">
                {nutrition[item.key]?.toFixed(1) || '0.0'} {item.unit}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default NutritionDisplay

