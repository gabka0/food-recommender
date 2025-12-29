# Quick Deployment Guide

## Prerequisites

### 1. Install Google Cloud SDK

**Windows:**
- Download installer: https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe
- Run the installer and follow the prompts
- Restart your terminal/PowerShell after installation

**Or use PowerShell:**
```powershell
# Download and install
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\gcloud-installer.exe")
Start-Process "$env:Temp\gcloud-installer.exe"
```

### 2. Authenticate with Google Cloud

```powershell
gcloud auth login
```

This will open a browser window for you to sign in.

### 3. Get Your Project ID

If you don't have a project yet:
```powershell
# List existing projects
gcloud projects list

# Or create a new one
gcloud projects create food-recommender-YOURNAME --name="Food Recommender"
```

## Deployment Steps

### Step 1: Deploy Backend to Cloud Run

```powershell
# Navigate to project root
cd C:\Users\Admin\Desktop\Food_recommender

# Run deployment script
.\deploy-backend-enhanced.ps1 -ProjectId "YOUR_PROJECT_ID"
```

**Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.**

The script will:
- ✅ Check prerequisites (gcloud, Docker)
- ✅ Enable required APIs
- ✅ Verify model files exist
- ✅ Build Docker image
- ✅ Deploy to Cloud Run
- ✅ Display your backend URL

**Expected time:** 10-20 minutes (mostly for uploading model files)

### Step 2: Test Your Backend

After deployment, test the health endpoint:
```powershell
# Get your backend URL (saved in backend-url.txt)
$url = Get-Content backend-url.txt
curl "$url/health"
```

You should see:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### Step 3: Deploy Frontend

#### Option A: Vercel (Recommended - Free)

1. **Install Vercel CLI:**
   ```powershell
   npm install -g vercel
   ```

2. **Deploy:**
   ```powershell
   cd frontend
   vercel
   ```

3. **When prompted:**
   - Set up and deploy? **Yes**
   - Link to existing project? **No**
   - Project name? **food-recommender-frontend**
   - Directory? **./**
   - Override settings? **No**

4. **Add environment variable:**
   ```powershell
   vercel env add VITE_API_URL
   # Enter your Cloud Run URL (from Step 1)
   ```

5. **Redeploy with environment variable:**
   ```powershell
   vercel --prod
   ```

#### Option B: Cloud Run (Alternative)

If you prefer to deploy frontend to Cloud Run too:

```powershell
# Build and deploy frontend
cd frontend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/food-recommender-frontend
gcloud run deploy food-recommender-frontend `
    --image gcr.io/YOUR_PROJECT_ID/food-recommender-frontend `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars VITE_API_URL=https://YOUR_BACKEND_URL.run.app
```

## Troubleshooting

### "gcloud: command not found"
- Install Google Cloud SDK (see Prerequisites)
- Restart your terminal after installation
- Verify installation: `gcloud --version`

### "Permission denied" or "Access denied"
- Make sure you're authenticated: `gcloud auth login`
- Check project permissions: `gcloud projects get-iam-policy YOUR_PROJECT_ID`

### Build fails with "file not found"
- Ensure you're in the project root directory
- Check that `models/` folder exists with all required files:
  - `food101_multitask_resnet18.pt`
  - `food101_class_prototypes.pt`
  - `calories_per100.pt`
  - `nutrition.csv`

### Deployment timeout
- Large model files take time to upload
- The script sets timeout to 3600s (1 hour)
- Check Cloud Build logs: https://console.cloud.google.com/cloud-build

### Backend returns 503 "Model not loaded"
- Check Cloud Run logs: `gcloud run services logs read food-recommender-backend --region us-central1`
- Verify models are in the container (check startup logs)
- May need to increase memory: `--memory 4Gi`

## Cost Estimation

- **Cloud Run Backend:** 
  - Free tier: 2 million requests/month
  - After free tier: ~$0.40 per million requests
  - Memory/CPU costs: ~$0.10-0.50/month for light usage

- **Vercel Frontend:**
  - Free tier: 100GB bandwidth/month
  - Usually $0/month for portfolio projects

**Total estimated cost: $0-5/month for portfolio use**

## Useful Commands

```powershell
# View backend logs
gcloud run services logs read food-recommender-backend --region us-central1

# Update backend (after code changes)
.\deploy-backend-enhanced.ps1 -ProjectId "YOUR_PROJECT_ID"

# Get backend URL
gcloud run services describe food-recommender-backend --region us-central1 --format 'value(status.url)'

# Delete service (if needed)
gcloud run services delete food-recommender-backend --region us-central1
```

## Next Steps After Deployment

1. ✅ Test backend health endpoint
2. ✅ Test prediction endpoint with a food image
3. ✅ Deploy frontend
4. ✅ Update CORS in backend (optional, for security)
5. ✅ Test full application end-to-end

