# Deployment Guide

## Prerequisites

1. **Google Cloud Account**
   - Create account at https://cloud.google.com
   - Enable Cloud Run API and Container Registry API
   - Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install

2. **Vercel Account**
   - Sign up at https://vercel.com (free tier available)

## Step 1: Deploy Backend to Cloud Run

### Setup Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create food-recommender-project --name="Food Recommender"

# Set as active project
gcloud config set project food-recommender-project

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Deploy Backend

**Windows:**
```powershell
.\deploy-backend.ps1 -ProjectId "your-project-id"
```

**Linux/Mac:**
```bash
chmod +x deploy-backend.sh
./deploy-backend.sh your-project-id
```

**Manual deployment:**
```bash
# Build image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/food-recommender-backend

# Deploy
gcloud run deploy food-recommender-backend \
    --image gcr.io/YOUR_PROJECT_ID/food-recommender-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10
```

**Note the Cloud Run URL** (e.g., `https://food-recommender-backend-xxx.run.app`)

## Step 2: Deploy Frontend to Vercel

### Option A: Using Vercel CLI

```bash
cd frontend
npm install -g vercel
vercel
```

When prompted:
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No**
- Project name? **food-recommender-frontend**
- Directory? **./**
- Override settings? **No**

Then add environment variable:
```bash
vercel env add VITE_API_URL
# Enter your Cloud Run URL: https://food-recommender-backend-xxx.run.app
```

### Option B: Using GitHub Integration

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: Your Cloud Run URL (e.g., `https://food-recommender-backend-xxx.run.app`)
6. Click "Deploy"

## Step 3: Update CORS (Optional but Recommended)

After deploying frontend, update backend CORS to allow only your Vercel domain:

```bash
gcloud run services update food-recommender-backend \
    --set-env-vars FRONTEND_URL=https://your-vercel-app.vercel.app \
    --region us-central1
```

## Cost Monitoring

- **Cloud Run**: Monitor in [Cloud Console](https://console.cloud.google.com/run)
- **Vercel**: Monitor in [Vercel Dashboard](https://vercel.com/dashboard)

### Estimated Costs (Portfolio/Demo Use)

- **Cloud Run**: $0-5/month (free tier: 2M requests/month)
- **Vercel**: $0/month (free tier: 100GB bandwidth/month)
- **Total**: $0-5/month for internship portfolio

## Troubleshooting

### Backend Issues

- **Cold starts**: First request may take 10-30 seconds. Consider setting `--min-instances 1` (costs more)
- **Memory errors**: Increase memory with `--memory 4Gi`
- **Timeout errors**: Increase timeout with `--timeout 600`

### Frontend Issues

- **API not connecting**: Check `VITE_API_URL` environment variable in Vercel
- **CORS errors**: Update backend CORS settings

## Useful Commands

```bash
# View backend logs
gcloud run services logs read food-recommender-backend --region us-central1

# Update backend
gcloud run services update food-recommender-backend --region us-central1

# Delete service (if needed)
gcloud run services delete food-recommender-backend --region us-central1
```

## Quick Reference

### Backend URL Format
```
https://food-recommender-backend-XXXXX.run.app
```

### Environment Variables

**Backend (Cloud Run):**
- `PORT` - Automatically set by Cloud Run
- `FRONTEND_URL` - Optional, for CORS restriction

**Frontend (Vercel):**
- `VITE_API_URL` - Your Cloud Run backend URL

