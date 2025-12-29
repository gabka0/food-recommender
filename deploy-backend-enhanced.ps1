# Enhanced Backend Deployment Script for Google Cloud Run
# Usage: .\deploy-backend-enhanced.ps1 -ProjectId "your-project-id"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    [string]$ServiceName = "food-recommender-backend"
)

# Colors for output
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "🚀 Starting deployment process..."

# Add gcloud to PATH if not already there (common Windows installation location)
$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
if (Test-Path $gcloudPath) {
    if ($env:PATH -notlike "*$gcloudPath*") {
        $env:PATH += ";$gcloudPath"
        Write-Info "📝 Added gcloud to PATH for this session"
    }
}

# Check if gcloud is installed
Write-Info "📋 Checking prerequisites..."
try {
    $gcloudVersion = gcloud --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud not found"
    }
    Write-Success "✅ Google Cloud SDK is installed"
} catch {
    Write-Error "❌ Google Cloud SDK not found!"
    Write-Warning "Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install"
    Write-Warning "Or use the installer: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
    exit 1
}

# Check if Docker is installed
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "docker not found"
    }
    Write-Success "✅ Docker is installed"
} catch {
    Write-Warning "⚠️  Docker not found. Cloud Build will build the image, but local testing requires Docker."
}

# Set project
Write-Info "🔧 Setting Google Cloud project to: $ProjectId"
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Failed to set project. Please check your project ID and authentication."
    exit 1
}

# Enable required APIs
Write-Info "🔌 Enabling required Google Cloud APIs..."
$apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "  Enabling $api..."
    gcloud services enable $api --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "  ✅ $api enabled"
    } else {
        Write-Warning "  ⚠️  Failed to enable $api (may already be enabled)"
    }
}

# Check if models directory exists
if (-not (Test-Path "models")) {
    Write-Error "❌ Models directory not found! Please ensure the 'models' folder exists in the project root."
    exit 1
}

# Check for required model files
$requiredFiles = @(
    "models/food101_multitask_resnet18.pt",
    "models/food101_class_prototypes.pt",
    "models/calories_per100.pt",
    "models/nutrition.csv"
)

Write-Info "📦 Checking for required model files..."
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $sizeMB = [math]::Round((Get-Item $file).Length / 1MB, 2)
        Write-Success "  ✅ $file ($sizeMB MB)"
    } else {
        Write-Error "  ❌ Missing: $file"
        exit 1
    }
}

# Build and submit to Container Registry
Write-Info "📦 Building Docker image (this may take several minutes)..."
Write-Warning "  This will upload your models to Google Cloud. Large files may take time."

$imageTag = "gcr.io/$ProjectId/$ServiceName"
gcloud builds submit --tag $imageTag --timeout=3600

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Build failed! Check the error messages above."
    exit 1
}

Write-Success "✅ Image built successfully!"

# Deploy to Cloud Run
Write-Info "☁️  Deploying to Cloud Run..."
Write-Info "  Service: $ServiceName"
Write-Info "  Region: $Region"
Write-Info "  Memory: 2Gi"
Write-Info "  CPU: 2"
Write-Info "  Timeout: 300s"

gcloud run deploy $ServiceName `
    --image $imageTag `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 0 `
    --port 8080

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Deployment failed! Check the error messages above."
    exit 1
}

# Get the service URL
Write-Info "🔍 Retrieving service URL..."
$serviceUrl = gcloud run services describe $ServiceName --region $Region --format 'value(status.url)' 2>&1

if ($LASTEXITCODE -eq 0 -and $serviceUrl) {
    Write-Success "`n✅ Deployment complete!"
    Write-Success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Info "🌐 Backend URL: $serviceUrl"
    Write-Success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Warning "`n📝 Next steps:"
    Write-Info "1. Test the backend: $serviceUrl/health"
    Write-Info "2. Update frontend environment variable:"
    Write-Info "   VITE_API_URL=$serviceUrl"
    Write-Info "3. Deploy frontend to Vercel or your preferred platform"
    
    # Save URL to file for easy reference
    $serviceUrl | Out-File -FilePath "backend-url.txt" -Encoding utf8
    Write-Success "`n💾 Backend URL saved to: backend-url.txt"
} else {
    Write-Warning "⚠️  Deployment completed but couldn't retrieve URL."
    Write-Info "You can get it manually with:"
    Write-Info "gcloud run services describe $ServiceName --region $Region --format 'value(status.url)'"
}

