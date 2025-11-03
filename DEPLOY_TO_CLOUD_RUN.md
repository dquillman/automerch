# Deploy AutoMerch to Google Cloud Run

This guide walks you through deploying AutoMerch to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **Docker** installed (optional, for local testing)
4. **Git** for version control

## Initial Setup

### 1. Install and Configure gcloud CLI

```bash
# Install gcloud CLI (if not already installed)
# Windows: Download from https://cloud.google.com/sdk/docs/install
# Mac: brew install google-cloud-sdk
# Linux: curl https://sdk.cloud.google.com | bash

# Login to Google Cloud
gcloud auth login

# Set your project (replace YOUR_PROJECT_ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Create Google Cloud Project (if needed)

```bash
# Create new project
gcloud projects create YOUR_PROJECT_ID --name="AutoMerch"

# Set as active project
gcloud config set project YOUR_PROJECT_ID

# Link billing account (required for Cloud Run)
gcloud billing accounts list
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

## Deployment Methods

### Method 1: Quick Deploy (Recommended for First Time)

```bash
# Navigate to project directory
cd automerch_remote

# Deploy directly to Cloud Run
gcloud run deploy automerch \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars AUTOMERCH_DRY_RUN=true
```

This will:
- Build the Docker container
- Push to Google Container Registry
- Deploy to Cloud Run
- Give you a public URL (e.g., https://automerch-xxxxx-uc.a.run.app)

### Method 2: Using Cloud Build (Automated CI/CD)

```bash
# Submit build using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml

# Or connect to GitHub for automatic deployments
gcloud run deploy automerch \
  --source . \
  --region us-central1
```

### Method 3: Manual Docker Build and Push

```bash
# Set project ID
export PROJECT_ID=$(gcloud config get-value project)

# Build Docker image
docker build -t gcr.io/$PROJECT_ID/automerch:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/automerch:latest

# Deploy to Cloud Run
gcloud run deploy automerch \
  --image gcr.io/$PROJECT_ID/automerch:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

## Environment Variables Configuration

### Set Environment Variables via gcloud

```bash
# Set individual variables
gcloud run services update automerch \
  --region us-central1 \
  --set-env-vars "AUTOMERCH_DRY_RUN=false"

# Set multiple variables
gcloud run services update automerch \
  --region us-central1 \
  --set-env-vars "ETSY_CLIENT_ID=your_client_id,ETSY_CLIENT_SECRET=your_secret,AUTOMERCH_DRY_RUN=false"

# Or use a .env.yaml file
gcloud run services update automerch \
  --region us-central1 \
  --env-vars-file .env.yaml
```

### Create .env.yaml for Cloud Run

Create a file named `.env.yaml`:

```yaml
AUTOMERCH_DRY_RUN: "false"
ETSY_CLIENT_ID: "your_etsy_client_id"
ETSY_CLIENT_SECRET: "your_etsy_client_secret"
ETSY_SHOP_ID: "your_shop_id"
ETSY_REDIRECT_URI: "https://your-cloud-run-url.run.app/auth/etsy/callback"
PRINTFUL_API_KEY: "your_printful_key"
ALLOWED_ORIGINS: "https://your-cloud-run-url.run.app"
API_KEY: "your_secure_api_key"
AUTOMERCH_DB: "sqlite:///automerch.db"
```

**Important:** Never commit `.env.yaml` to git! Add it to `.gitignore`.

## Database Configuration

### Option 1: SQLite (Simple, for testing)

```bash
# Use default SQLite (data will be lost on container restart)
gcloud run services update automerch \
  --region us-central1 \
  --set-env-vars "AUTOMERCH_DB=sqlite:///automerch.db"
```

**Note:** SQLite data is ephemeral on Cloud Run. Use Cloud SQL for production.

### Option 2: Cloud SQL (Recommended for Production)

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create automerch-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create automerch --instance=automerch-db

# Create user
gcloud sql users create automerch-user \
  --instance=automerch-db \
  --password=SECURE_PASSWORD

# Get connection name
gcloud sql instances describe automerch-db --format='value(connectionName)'

# Deploy with Cloud SQL connection
gcloud run deploy automerch \
  --image gcr.io/$PROJECT_ID/automerch:latest \
  --region us-central1 \
  --add-cloudsql-instances PROJECT_ID:us-central1:automerch-db \
  --set-env-vars "AUTOMERCH_DB=postgresql://automerch-user:SECURE_PASSWORD@/automerch?host=/cloudsql/PROJECT_ID:us-central1:automerch-db"
```

## Security Configuration

### 1. Require Authentication (Recommended)

```bash
# Deploy with authentication required
gcloud run deploy automerch \
  --image gcr.io/$PROJECT_ID/automerch:latest \
  --region us-central1 \
  --no-allow-unauthenticated

# Grant access to specific users
gcloud run services add-iam-policy-binding automerch \
  --region us-central1 \
  --member="user:your-email@example.com" \
  --role="roles/run.invoker"
```

### 2. Set API Key Protection

```bash
# Generate secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set as environment variable
gcloud run services update automerch \
  --region us-central1 \
  --set-env-vars "API_KEY=your_generated_key"
```

### 3. Configure CORS

```bash
# Set allowed origins
gcloud run services update automerch \
  --region us-central1 \
  --set-env-vars "ALLOWED_ORIGINS=https://your-frontend.com,https://app.your-frontend.com"
```

## Monitoring and Logs

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail automerch --region us-central1

# View recent logs
gcloud run services logs read automerch --region us-central1 --limit 50
```

### View Service Details

```bash
# Get service URL
gcloud run services describe automerch --region us-central1 --format='value(status.url)'

# View all service details
gcloud run services describe automerch --region us-central1
```

### Monitor Metrics

```bash
# Open Cloud Console monitoring
gcloud run services describe automerch --region us-central1 --format='value(status.url)'

# Or visit: https://console.cloud.google.com/run
```

## Testing the Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe automerch --region us-central1 --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Test API docs
curl $SERVICE_URL/docs

# Or open in browser
echo "Visit: $SERVICE_URL/docs"
```

## Updating the Deployment

```bash
# After making code changes, rebuild and deploy
gcloud builds submit --config cloudbuild.yaml

# Or quick redeploy from source
gcloud run deploy automerch \
  --source . \
  --region us-central1
```

## Cost Optimization

### Set Instance Limits

```bash
# Set minimum instances to 0 (no cost when idle)
# Set maximum instances based on expected traffic
gcloud run services update automerch \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 5
```

### Set Resource Limits

```bash
# Optimize memory and CPU
gcloud run services update automerch \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1
```

### Set Request Timeout

```bash
# Set timeout (max 3600s)
gcloud run services update automerch \
  --region us-central1 \
  --timeout 300
```

## Troubleshooting

### Issue: Container fails to start

```bash
# Check logs
gcloud run services logs read automerch --region us-central1 --limit 100

# Common causes:
# - Missing environment variables
# - Port mismatch (Cloud Run expects PORT=8080)
# - Database connection issues
```

### Issue: 502 Bad Gateway

```bash
# Ensure app listens on 0.0.0.0:$PORT
# Check Dockerfile CMD:
# CMD uvicorn automerch.api.app:app --host 0.0.0.0 --port ${PORT:-8080}
```

### Issue: Out of memory

```bash
# Increase memory allocation
gcloud run services update automerch \
  --region us-central1 \
  --memory 1Gi
```

### Issue: Slow cold starts

```bash
# Set minimum instances to keep one warm
gcloud run services update automerch \
  --region us-central1 \
  --min-instances 1
```

## Rollback

```bash
# List revisions
gcloud run revisions list --service automerch --region us-central1

# Rollback to previous revision
gcloud run services update-traffic automerch \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## Delete Service

```bash
# Delete Cloud Run service
gcloud run services delete automerch --region us-central1

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/automerch:latest

# Delete Cloud SQL instance (if created)
gcloud sql instances delete automerch-db
```

## CI/CD with GitHub

### Connect GitHub Repository

1. Go to Cloud Console: https://console.cloud.google.com/cloud-build/triggers
2. Click "Connect Repository"
3. Select GitHub and authorize
4. Choose your automerch repository
5. Create trigger:
   - Event: Push to branch
   - Branch: `^main$`
   - Configuration: Cloud Build configuration file
   - Location: `/cloudbuild.yaml`

Now every push to main will automatically deploy to Cloud Run!

## Cost Estimates

**Cloud Run Pricing (as of 2024):**
- First 2 million requests/month: FREE
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests

**Typical costs for low-traffic app:**
- ~100 requests/day: **~$0-5/month**
- ~1000 requests/day: **~$5-15/month**

**Cloud SQL (if used):**
- db-f1-micro: **~$7.67/month** (shared core, 614MB RAM)
- db-g1-small: **~$24.84/month** (1 core, 1.7GB RAM)

## Best Practices

1. ✅ Use Cloud SQL for production (not SQLite)
2. ✅ Set `--min-instances 0` to save costs when idle
3. ✅ Enable authentication for production deployments
4. ✅ Use Secret Manager for sensitive credentials
5. ✅ Set up Cloud Monitoring alerts
6. ✅ Configure automated backups for Cloud SQL
7. ✅ Use Cloud Build for CI/CD
8. ✅ Tag images with git commit SHA for traceability

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

## Support

If you encounter issues:
1. Check the logs: `gcloud run services logs tail automerch --region us-central1`
2. Review the troubleshooting section above
3. Consult Cloud Run documentation

---

**Deployment Date:** $(date +%Y-%m-%d)
**Last Updated:** 2025-11-03
