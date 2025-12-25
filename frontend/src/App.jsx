import React, { useState } from 'react'
import ImageUpload from './components/ImageUpload'
import PredictionResults from './components/PredictionResults'
import NutritionDisplay from './components/NutritionDisplay'
import AlternativesList from './components/AlternativesList'
import { predictFood, getRecommendations } from './services/api'

function App() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(false)
  const [recommendationsLoading, setRecommendationsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [recommendationsError, setRecommendationsError] = useState(null)

  const handleImageSelect = (file) => {
    setSelectedImage(file)
    setPrediction(null)
    setRecommendations(null)
    setError(null)
    setRecommendationsError(null)
  }

  const handlePredict = async () => {
    if (!selectedImage) {
      alert('Please select an image first')
      return
    }

    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      const result = await predictFood(selectedImage)
      setPrediction(result)
      
      // Automatically get recommendations after prediction
      handleGetRecommendations()
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed')
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleGetRecommendations = async () => {
    if (!selectedImage) {
      console.log('No image selected for recommendations')
      return
    }

    console.log('Getting recommendations...')
    setRecommendationsLoading(true)
    setRecommendationsError(null)
    setRecommendations(null)

    try {
      const result = await getRecommendations(selectedImage, {
        topk_sim: 30,  // Increased to find more candidates
        topk_out: 6,
        min_calorie_drop: 10.0  // Lowered threshold to find more alternatives
      })
      console.log('Recommendations received:', result)
      console.log('Number of suggestions:', result?.suggestions?.length || 0)
      setRecommendations(result)
    } catch (err) {
      console.error('Recommendation error:', err)
      console.error('Error details:', err.response?.data)
      setRecommendationsError(err.response?.data?.detail || err.message || 'Recommendation failed')
    } finally {
      setRecommendationsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🍽️ Food Recommender</h1>
        <p>Upload a food image to get nutrition info and healthier alternatives</p>
      </header>

      <main className="app-main">
        <div className="upload-section">
          <ImageUpload
            onImageSelect={handleImageSelect}
            selectedImage={selectedImage}
          />
          {selectedImage && (
            <button
              className="predict-btn"
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? 'Analyzing...' : 'Analyze Food'}
            </button>
          )}
        </div>

        {prediction && (
          <div className="results-section">
            <PredictionResults
              prediction={prediction}
              loading={loading}
              error={error}
            />
            <NutritionDisplay
              nutrition={prediction.nutrition}
              loading={loading}
            />
          </div>
        )}

        {recommendations && (
          <div className="recommendations-section">
            <AlternativesList
              recommendations={recommendations}
              loading={recommendationsLoading}
              error={recommendationsError}
            />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by AI/ML Food Classification Model</p>
      </footer>
    </div>
  )
}

export default App

