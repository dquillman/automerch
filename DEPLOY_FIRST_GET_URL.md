# 🚀 Quick Deploy to Get URL First

Since Printful needs your app URL to register, here's how to deploy with minimal config first:

## Step 1: Deploy with Minimal Config

1. **Go to:** https://console.cloud.google.com/cloud-build/builds?project=automerch-app
2. **Build the image** (follow Step 1-2 from CONSOLE_DEPLOY_STEP_BY_STEP.md)
3. **Go to:** https://console.cloud.google.com/run?project=automerch-app
4. **Click** "Create Service"
5. **Container image:** `gcr.io/automerch-app/automerch:latest`
6. **Service name:** `automerch`
7. **Region:** `us-central1`
8. **Authentication:** Allow unauthenticated
9. **Variables & Secrets tab:** Add ONLY:
   - `AUTOMERCH_DRY_RUN` = `true`
   - `ETSY_REDIRECT_URI` = `https://placeholder.run.app/auth/etsy/callback`
10. **Click** "Create"

## Step 2: Get Your URL

After deployment, copy the service URL:
```
https://automerch-abc123-uc.a.run.app
```

## Step 3: Register with Printful

1. **Go to:** https://www.printful.com/dashboard/api
2. **Register your app** using the URL from Step 2
3. **Copy your Printful API key**

## Step 4: Register with Etsy (if not done)

1. **Go to:** https://www.etsy.com/developers/register
2. **Use your service URL** as redirect URI: `https://YOUR_URL.run.app/auth/etsy/callback`
3. **Get your Etsy credentials**

## Step 5: Add All Credentials to Cloud Run

1. **Go to:** https://console.cloud.google.com/run?project=automerch-app
2. **Click** your `automerch` service
3. **Click** "Edit & Deploy New Revision"
4. **Variables & Secrets tab:** Add all variables:
   - `ETSY_CLIENT_ID` = your Etsy client ID
   - `ETSY_CLIENT_SECRET` = your Etsy secret
   - `ETSY_SHOP_ID` = your Etsy shop ID
   - `ETSY_REDIRECT_URI` = `https://YOUR_URL.run.app/auth/etsy/callback`
   - `PRINTFUL_API_KEY` = your Printful API key
   - `AUTOMERCH_DRY_RUN` = `false`
5. **Click** "Deploy"

## ✅ Done!

You now have:
- ✅ App deployed with URL
- ✅ Printful registered
- ✅ Etsy registered
- ✅ All credentials configured


