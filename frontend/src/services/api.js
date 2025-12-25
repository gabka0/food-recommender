/**
 * API client for backend communication
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

/**
 * Predict food class and nutrition from image
 * @param {File} imageFile - Image file to upload
 * @returns {Promise} Prediction result with class, confidence, and nutrition
 */
export const predictFood = async (imageFile) => {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  const response = await api.post('/predict', formData)
  return response.data
}

/**
 * Get lower-calorie alternative suggestions
 * @param {File} imageFile - Image file to upload
 * @param {Object} options - Recommendation options
 * @param {number} options.topk_sim - Number of similar classes to consider
 * @param {number} options.topk_out - Number of suggestions to return
 * @param {number} options.min_calorie_drop - Minimum calorie reduction
 * @returns {Promise} Recommendation result with alternatives
 */
export const getRecommendations = async (imageFile, options = {}) => {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  const params = new URLSearchParams()
  if (options.topk_sim) params.append('topk_sim', options.topk_sim)
  if (options.topk_out) params.append('topk_out', options.topk_out)
  if (options.min_calorie_drop) params.append('min_calorie_drop', options.min_calorie_drop)
  
  const url = `/recommend${params.toString() ? '?' + params.toString() : ''}`
  const response = await api.post(url, formData)
  return response.data
}

export default api

