# Food Recommender System

A full-stack web application for food classification, nutrition prediction, and lower-calorie alternative recommendations using a multi-task deep learning model.

## Features

- 🍽️ **Food Classification**: Identify food items from images (101 food categories)
- 📊 **Nutrition Prediction**: Get nutrition values (calories, protein, fat, carbs, sugars, sodium) per 100g
- 💡 **Smart Recommendations**: Find visually similar foods with lower calories
- 🎨 **Modern UI**: Beautiful, responsive React frontend
- 🐳 **Docker Ready**: Containerized for easy deployment

## Architecture

- **Backend**: FastAPI with PyTorch model inference
- **Frontend**: React with Vite
- **Model**: Multi-task ResNet18 (classification + nutrition regression)
- **Deployment**: Docker containers, ready for Cloud Run

## Project Structure

```
Food_recommender/
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI application
│   ├── model_architecture.py
│   ├── model_loader.py
│   ├── nutrition_loader.py
│   ├── image_utils.py
│   ├── recommendation.py
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
├── models/              # Model artifacts (from Colab training)
│   ├── food101_multitask_resnet18.pt
│   ├── food101_class_prototypes.pt
│   ├── calories_per100.pt
│   ├── nutrition.csv
│   └── meta.json
└── docker-compose.yml
```

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Node.js 18+ (for local frontend development)

## Quick Start with Docker

1. **Clone and navigate to the project**:
   ```bash
   cd Food_recommender
   ```

2. **Start services with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### `POST /predict`
Upload an image to get food classification and nutrition prediction.

**Request**: Multipart form data with `file` field (image)

**Response**:
```json
{
  "predicted_class": "apple_pie",
  "confidence": 0.95,
  "nutrition": {
    "calories": 300.0,
    "protein": 3.0,
    "fat": 12.0,
    "carbs": 45.0,
    "sugars": 20.0,
    "sodium": 150.0
  }
}
```

### `POST /recommend`
Get lower-calorie alternative suggestions.

**Request**: Multipart form data with `file` field (image)

**Query Parameters**:
- `topk_sim`: Number of similar classes to consider (default: 20)
- `topk_out`: Number of suggestions to return (default: 6)
- `min_calorie_drop`: Minimum calorie reduction (default: 15.0)

**Response**:
```json
{
  "pred_class": "apple_pie",
  "pred_calories_per_100g": 300.0,
  "suggestions": [
    {
      "class": "bread_pudding",
      "similarity": 0.738,
      "calories_per_100g": 250.0,
      "calorie_drop": 50.0
    }
  ]
}
```

### `GET /health`
Health check endpoint.

## Deployment to Google Cloud Run

1. **Build and push backend image**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/food-recommender-backend
   ```

2. **Deploy backend**:
   ```bash
   gcloud run deploy food-recommender-backend \
     --image gcr.io/PROJECT_ID/food-recommender-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --timeout 300
   ```

3. **Build and push frontend image**:
   ```bash
   cd frontend
   gcloud builds submit --tag gcr.io/PROJECT_ID/food-recommender-frontend
   ```

4. **Deploy frontend**:
   ```bash
   gcloud run deploy food-recommender-frontend \
     --image gcr.io/PROJECT_ID/food-recommender-frontend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Model Information

- **Architecture**: ResNet18 backbone with multi-task heads
- **Tasks**: 
  - Classification: 101 food categories
  - Regression: 6 nutrition values (calories, protein, fat, carbs, sugars, sodium)
- **Training**: Done in Google Colab with GPU
- **Inference**: CPU-compatible for Cloud Run deployment

## Notes

- Model artifacts must be present in `models/` directory
- First prediction may take 2-5 seconds (model loading + inference)
- Backend requires ~2GB RAM for model loading
- For production, consider using Cloud Storage for model files

## License

This project is for educational purposes.

