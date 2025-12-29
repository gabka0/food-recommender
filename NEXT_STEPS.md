# ✅ Backend Deployment Complete!

## Your Backend URL
```
https://food-recommender-backend-738722045336.us-central1.run.app
```

**Status:** ✅ Healthy and running
- Model loaded: ✅ Yes
- Device: CPU
- Public access: ✅ Enabled

---

## Next Steps: Deploy Frontend

You have two options for deploying the frontend:

### Option 1: Deploy to Vercel (Recommended - Free & Easy)

**Step 1: Install Vercel CLI**
```powershell
npm install -g vercel
```

**Step 2: Navigate to frontend directory**
```powershell
cd frontend
```

**Step 3: Deploy**
```powershell
vercel
```

**When prompted:**
- Set up and deploy? → **Yes**
- Which scope? → **Your account**
- Link to existing project? → **No**
- Project name? → **food-recommender-frontend**
- Directory? → **./**
- Override settings? → **No**

**Step 4: Add environment variable**
```powershell
vercel env add VITE_API_URL
# When prompted, enter: https://food-recommender-backend-738722045336.us-central1.run.app
# Select: Production, Preview, and Development
```

**Step 5: Redeploy with environment variable**
```powershell
vercel --prod
```

**Done!** Vercel will give you a URL like: `https://food-recommender-frontend.vercel.app`

---

### Option 2: Deploy Frontend to Cloud Run

**Step 1: Build and deploy**
```powershell
cd frontend
gcloud builds submit --tag gcr.io/foodrecognizerapp-482717/food-recommender-frontend

gcloud run deploy food-recommender-frontend `
    --image gcr.io/foodrecognizerapp-482717/food-recommender-frontend `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars VITE_API_URL=https://food-recommender-backend-738722045336.us-central1.run.app
```

---

## Testing Your Deployment

### Test Backend
```powershell
# Health check
curl https://food-recommender-backend-738722045336.us-central1.run.app/health

# Should return: {"status":"healthy","model_loaded":true,"device":"cpu"}
```

### Test Frontend
1. Open your frontend URL in a browser
2. Upload a food image
3. Check if predictions work

---

## Useful Commands

### View Backend Logs
```powershell
gcloud run services logs read food-recommender-backend --region us-central1
```

### Update Backend (after code changes)
```powershell
gcloud builds submit --config cloudbuild.yaml --timeout=3600
```

### Get Backend URL
```powershell
gcloud run services describe food-recommender-backend --region us-central1 --format 'value(status.url)'
```

---

## Troubleshooting

### Frontend can't connect to backend
- Check that `VITE_API_URL` is set correctly in your deployment platform
- Verify backend is accessible: `curl https://food-recommender-backend-738722045336.us-central1.run.app/health`
- Check browser console for CORS errors

### Backend returns 503
- Check Cloud Run logs: `gcloud run services logs read food-recommender-backend --region us-central1`
- Verify models are loaded (check startup logs)

### CORS errors
- Backend is configured to allow all origins (`*`)
- If you want to restrict, update backend CORS in `backend/main.py`

---

## Summary

✅ **Backend:** Deployed and running
- URL: `https://food-recommender-backend-738722045336.us-central1.run.app`
- Status: Healthy

⏳ **Frontend:** Ready to deploy
- Choose Vercel (easiest) or Cloud Run
- Set `VITE_API_URL` environment variable

🎉 **Next:** Deploy frontend and test the full application!

