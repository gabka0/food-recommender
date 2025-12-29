#!/bin/bash
# Deploy Backend to Google Cloud Run
# Usage: ./deploy-backend.sh your-project-id

set -e

PROJECT_ID=${1:-""}
REGION=${2:-"us-central1"}
SERVICE_NAME="food-recommender-backend"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID required"
    echo "Usage: ./deploy-backend.sh YOUR_PROJECT_ID"
    exit 1
fi

echo "🚀 Deploying backend to Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Build and submit to Container Registry
echo "📦 Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "✅ Deployment complete!"
echo "🌐 Backend URL: $SERVICE_URL"
echo ""
echo "📝 Update frontend environment variable: VITE_API_URL=$SERVICE_URL"

