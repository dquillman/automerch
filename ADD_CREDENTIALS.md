# 🔑 Add Credentials to Cloud Run

Since the Settings button is hard to find in the console, here's how to add credentials via command line:

## Option 1: Add All Credentials at Once

**When you have all your credentials ready:**

```powershell
gcloud run services update automerch \
  --update-env-vars="ETSY_CLIENT_ID=your_client_id,ETSY_CLIENT_SECRET=your_secret,ETSY_SHOP_ID=your_shop_id,ETSY_REDIRECT_URI=https://automerch-715156784717.us-central1.run.app/auth/etsy/callback,PRINTFUL_API_KEY=your_printful_key,AUTOMERCH_DRY_RUN=false" \
  --region us-central1 \
  --project automerch-app
```

**Replace:**
- `your_client_id` with your actual Etsy Client ID
- `your_secret` with your actual Etsy Secret
- `your_shop_id` with your actual Etsy Shop ID
- `your_printful_key` with your actual Printful API key

## Option 2: Add One at a Time

**If you only have some credentials now:**

```powershell
# Add Etsy credentials
gcloud run services update automerch \
  --update-env-vars="ETSY_CLIENT_ID=your_client_id,ETSY_CLIENT_SECRET=your_secret,ETSY_SHOP_ID=your_shop_id,ETSY_REDIRECT_URI=https://automerch-715156784717.us-central1.run.app/auth/etsy/callback" \
  --region us-central1 \
  --project automerch-app

# Add Printful later
gcloud run services update automerch \
  --update-env-vars="PRINTFUL_API_KEY=your_printful_key" \
  --region us-central1 \
  --project automerch-app

# Turn off dry run when ready
gcloud run services update automerch \
  --update-env-vars="AUTOMERCH_DRY_RUN=false" \
  --region us-central1 \
  --project automerch-app
```

## Option 3: Find Settings in Console

If you want to try the console again:

1. **Go to:** https://console.cloud.google.com/run?project=automerch-app
2. **Click** on the service name `automerch` (not the URL, but the name itself)
3. **You should see tabs:** "Metrics", "Logs", "Revisions", "YAML"
4. **Click** on any revision (like `automerch-00002-v8b`)
5. **Look for** "Edit & Deploy New Revision" button
6. **Click** it
7. **Scroll down** to find "Variables & Secrets" tab

**Or try:**
- Look for "EDIT" or pencil icon near the top
- Check the right sidebar for settings
- Look for "Environment Variables" in the main content area

---

## Quick Test

After adding credentials, test your app:
- Visit: https://automerch-715156784717.us-central1.run.app
- Try: https://automerch-715156784717.us-central1.run.app/auth/etsy/login

---

**I can help you run the command when you have your credentials ready!** Just let me know. 🚀

