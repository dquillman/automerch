# 🚀 Deploy AutoMerch to Google Cloud Run

This guide will help you deploy AutoMerch to Google Cloud Run, giving you a permanent HTTPS URL that works perfectly with Etsy OAuth.

---

## 📋 Prerequisites

1. **Google Cloud Account** - Sign up at https://cloud.google.com
2. **Google Cloud CLI** - Install from https://cloud.google.com/sdk/docs/install
3. **Docker** (optional, for local testing) - Install from https://www.docker.com

---

## 🎯 Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project

1. **Go to:** https://console.cloud.google.com
2. **Click** "Select a project" → "New Project"
3. **Enter project name:** `automerch` (or your choice)
4. **Click** "Create"
5. **Note your Project ID** (e.g., `automerch-123456`)

### 1.2 Enable Billing

1. **Go to:** Billing in Google Cloud Console
2. **Link a billing account** to your project
3. **Note:** Cloud Run has a generous free tier, but billing must be enabled

### 1.3 Enable Required APIs

```powershell
# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

---

## 🎯 Step 2: Configure Environment Variables

### 2.1 Create Secret Manager Secrets (Recommended)

Store sensitive credentials in Google Secret Manager:

```powershell
# Create secrets for Etsy credentials
echo -n "your_etsy_client_id" | gcloud secrets create etsy-client-id --data-file=-
echo -n "your_etsy_client_secret" | gcloud secrets create etsy-client-secret --data-file=-
echo -n "your_etsy_shop_id" | gcloud secrets create etsy-shop-id --data-file=-
echo -n "your_printful_api_key" | gcloud secrets create printful-api-key --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding etsy-client-id --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding etsy-client-secret --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding etsy-shop-id --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding printful-api-key --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
```

**Note:** Replace `PROJECT_NUMBER` with your actual project number (found in Cloud Console).

### 2.2 Alternative: Use Environment Variables Directly

You can also set environment variables directly in Cloud Run (less secure, but simpler for testing).

---

## 🎯 Step 3: Build and Deploy

### 3.1 Build Container Image

```powershell
# Navigate to automerch_remote directory
cd automerch_remote

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/automerch

# Or use Artifact Registry (newer, recommended)
gcloud artifacts repositories create automerch-repo --repository-format=docker --location=us-central1
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/automerch-repo/automerch:latest
```

### 3.2 Deploy to Cloud Run

```powershell
# Deploy with environment variables
gcloud run deploy automerch \
  --image gcr.io/YOUR_PROJECT_ID/automerch \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ETSY_CLIENT_ID=your_client_id,ETSY_CLIENT_SECRET=your_secret,ETSY_SHOP_ID=your_shop_id,ETSY_REDIRECT_URI=https://YOUR_SERVICE_URL.run.app/auth/etsy/callback,PRINTFUL_API_KEY=your_key,AUTOMERCH_DRY_RUN=false" \
  --set-secrets="ETSY_CLIENT_ID=etsy-client-id:latest,ETSY_CLIENT_SECRET=etsy-client-secret:latest,ETSY_SHOP_ID=etsy-shop-id:latest,PRINTFUL_API_KEY=printful-api-key:latest" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

**Note:** After first deployment, you'll get a URL. Update `ETSY_REDIRECT_URI` with that URL and redeploy.

---

## 🎯 Step 4: Update Etsy App Configuration

### 4.1 Get Your Cloud Run URL

After deployment, you'll see output like:
```
Service URL: https://automerch-abc123-uc.a.run.app
```

### 4.2 Update Etsy Redirect URI

1. **Go to:** https://www.etsy.com/developers/your-apps
2. **Click** your app
3. **Update Redirect URI** to: `https://YOUR_SERVICE_URL.run.app/auth/etsy/callback`
4. **Save** changes

### 4.3 Update Cloud Run with Correct Redirect URI

```powershell
# Redeploy with correct redirect URI
gcloud run services update automerch \
  --update-env-vars="ETSY_REDIRECT_URI=https://YOUR_SERVICE_URL.run.app/auth/etsy/callback" \
  --region us-central1
```

---

## 🎯 Step 5: Set Up Database (Optional)

Cloud Run is stateless. For persistent storage, you have options:

### Option A: Cloud SQL (PostgreSQL/MySQL)

```powershell
# Create Cloud SQL instance
gcloud sql instances create automerch-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create automerch --instance=automerch-db

# Update connection string
# Update AUTOMERCH_DB in Cloud Run to use Cloud SQL connection
```

### Option B: Cloud Firestore (NoSQL)

Update your database connection to use Firestore.

### Option C: Keep SQLite (Ephemeral - Data Lost on Restart)

For testing, SQLite works but data is lost when containers restart.

---

## 🎯 Step 6: Complete OAuth Setup

1. **Visit:** `https://YOUR_SERVICE_URL.run.app/auth/etsy/login`
2. **Authorize** with Etsy
3. **You'll be redirected back** - tokens will be saved

---

## 📝 Quick Deploy Script

Create a file `deploy.sh` (or `deploy.ps1` for Windows):

```bash
#!/bin/bash
PROJECT_ID="your-project-id"
REGION="us-central1"

echo "Building and deploying to Cloud Run..."

gcloud builds submit --tag gcr.io/$PROJECT_ID/automerch

gcloud run deploy automerch \
  --image gcr.io/$PROJECT_ID/automerch \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300

echo "Deployment complete!"
echo "Update ETSY_REDIRECT_URI with the service URL above"
```

---

## 🔧 Troubleshooting

### "Permission denied" errors
- Make sure billing is enabled
- Check you're authenticated: `gcloud auth list`
- Verify project: `gcloud config get-value project`

### "Image not found"
- Make sure you built the image first
- Check project ID matches: `gcloud config get-value project`

### "Database connection errors"
- SQLite files are ephemeral in Cloud Run
- Consider Cloud SQL for persistent storage

### "OAuth redirect mismatch"
- Verify Etsy redirect URI matches Cloud Run URL exactly
- Check `ETSY_REDIRECT_URI` environment variable in Cloud Run

---

## 💰 Cost Estimation

**Cloud Run Free Tier:**
- 2 million requests/month free
- 400,000 GB-seconds of memory, 200,000 vCPU-seconds free per month
- After free tier: ~$0.40 per million requests

**For typical usage:**
- Small app: **$0-5/month**
- Medium app: **$5-20/month**

---

## ✅ Post-Deployment Checklist

- [ ] Service is running and accessible
- [ ] Etsy redirect URI updated in Etsy developer console
- [ ] `ETSY_REDIRECT_URI` updated in Cloud Run environment variables
- [ ] OAuth flow completes successfully
- [ ] Research functionality works with real Etsy data
- [ ] Database persistence configured (if needed)

---

## 🚀 Next Steps

1. **Set up CI/CD** - Automatically deploy on git push
2. **Add custom domain** - Use your own domain instead of `.run.app`
3. **Set up monitoring** - Use Cloud Monitoring for logs and metrics
4. **Configure backups** - Set up database backups if using Cloud SQL

---

**Your app is now live on Google Cloud with a permanent HTTPS URL!** 🎉



