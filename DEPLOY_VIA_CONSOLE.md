# 🚀 Deploy via Google Cloud Console (No CLI Issues)

Since we're having permission issues with `gcloud builds submit`, here's how to deploy via the web console:

## Step 1: Build via Cloud Build Console

1. **Go to:** https://console.cloud.google.com/cloud-build/builds?project=automerch-app
2. **Click** "Create Build" or "Triggers" → "Create Trigger"
3. **Select** "Cloud Build configuration file"
4. **Repository:** Connect to GitHub (if you want) OR use "Cloud Source Repositories"
5. **OR** use "Inline" configuration:
   - **Build configuration:** `cloudbuild.yaml` (we created this)
   - **Substitution variables:** Leave default

## Step 2: Manual Build via Console

**Alternative - Direct Build:**

1. **Go to:** https://console.cloud.google.com/cloud-build/builds?project=automerch-app
2. **Click** "Create Build" or the "+" button
3. **Choose:** "Cloud Source Repositories" or "Upload Archive"
4. **Upload** your `automerch_remote` folder as a zip
5. **Build configuration:** Use `cloudbuild.yaml` or inline:
   ```yaml
   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/automerch-app/automerch:latest', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'gcr.io/automerch-app/automerch:latest']
   images:
   - 'gcr.io/automerch-app/automerch:latest'
   ```
6. **Click** "Create"

## Step 3: Deploy to Cloud Run

1. **Go to:** https://console.cloud.google.com/run?project=automerch-app
2. **Click** "Create Service"
3. **Deploy one revision from an existing container image**
4. **Container image URL:** `gcr.io/automerch-app/automerch:latest`
5. **Service name:** `automerch`
6. **Region:** `us-central1`
7. **Authentication:** Allow unauthenticated invocations
8. **Container:** 
   - **Memory:** 512 MiB
   - **CPU:** 1
   - **Timeout:** 300 seconds
   - **Max instances:** 10
9. **Environment variables:** 
   - Scroll down to the **"Container, Variables, Secrets, Connections"** section
   - Click on **"Variables & Secrets"** tab
   - Click **"Add Variable"** button
   - Add each variable one by one:
     - **Name:** `ETSY_CLIENT_ID` → **Value:** `your_client_id`
     - **Name:** `ETSY_CLIENT_SECRET` → **Value:** `your_secret`
     - **Name:** `ETSY_SHOP_ID` → **Value:** `your_shop_id`
     - **Name:** `ETSY_REDIRECT_URI` → **Value:** `https://placeholder.run.app/auth/etsy/callback` (we'll update this after deployment)
     - **Name:** `PRINTFUL_API_KEY` → **Value:** `your_key`
     - **Name:** `AUTOMERCH_DRY_RUN` → **Value:** `false`
   - **Note:** For `ETSY_REDIRECT_URI`, you can use a placeholder now - we'll update it after we get the actual service URL
10. **Click** "Create" button at the bottom

## Step 4: Get Your URL

After deployment, you'll see:
```
Service URL: https://automerch-abc123-uc.a.run.app
```

## Step 5: Update Etsy Redirect URI

1. **Copy the service URL** from above
2. **Go to:** https://www.etsy.com/developers/your-apps
3. **Update Redirect URI** to: `https://YOUR_URL.run.app/auth/etsy/callback`
4. **Update Cloud Run** environment variable `ETSY_REDIRECT_URI` with the same URL

---

**This bypasses the CLI permission issues!** 🎉


