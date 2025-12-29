# Deploy Backend to Google Cloud Run
# Usage: .\deploy-backend.ps1 -ProjectId "your-project-id"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [string]$ServiceName = "food-recommender-backend"
)

Write-Host "🚀 Deploying backend to Cloud Run..." -ForegroundColor Cyan

# Set project
gcloud config set project $ProjectId

# Build and submit to Container Registry
Write-Host "📦 Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$ProjectId/$ServiceName

# Deploy to Cloud Run
Write-Host "☁️  Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image gcr.io/$ProjectId/$ServiceName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 0

# Get the service URL
$serviceUrl = gcloud run services describe $ServiceName --region $Region --format 'value(status.url)'
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Backend URL: $serviceUrl" -ForegroundColor Cyan
Write-Host "`n📝 Update frontend/.env with: VITE_API_URL=$serviceUrl" -ForegroundColor Yellow

