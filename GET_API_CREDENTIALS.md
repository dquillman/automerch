# 🔑 How to Get Etsy Shop Info & Printful API Credentials

## 📋 Etsy API Shop Information

### Step 1: Get Etsy Client ID and Secret

1. **Go to:** https://www.etsy.com/developers/register
2. **Click** "Register a new application"
3. **Fill in:**
   - **Application Name:** AutoMerch
   - **Redirect URI:** `https://automerch-715156784717.us-central1.run.app/auth/etsy/callback`
     *(Use your Cloud Run URL - already set up!)*
   - **Description:** "Automated listing management"
4. **Click** "Register"
5. **Copy these values:**
   - **Keystring (Client ID)**
   - **Shared Secret (Client Secret)**

### Step 2: Get Your Etsy Shop ID

**Method 1: From Shop Settings (Easiest)**
1. **Go to:** https://www.etsy.com/your/shops/me/tools/settings
2. **Scroll down** to find your **Shop ID**
3. It's a number (like `12345678`)

**Method 2: From Shop URL**
1. **Go to your Etsy shop page** (e.g., `https://www.etsy.com/shop/YourShopName`)
2. **Look in the URL** - sometimes the shop ID is visible
3. Or **right-click** on your shop name → "View Source" → search for "shop_id"

**Method 3: Using Etsy API (After OAuth)**
1. Complete OAuth flow (see below)
2. Visit: `https://automerch-715156784717.us-central1.run.app/api/shops`
3. Your shop ID will be automatically detected and shown

### Step 3: Complete Etsy OAuth

1. **Make sure your credentials are set:**
   ```env
   ETSY_CLIENT_ID=your_client_id
   ETSY_CLIENT_SECRET=your_secret
   ETSY_SHOP_ID=your_shop_id
   ETSY_REDIRECT_URI=https://automerch-715156784717.us-central1.run.app/auth/etsy/callback
   ```

2. **Visit:** https://automerch-715156784717.us-central1.run.app/auth/etsy/login
   *(Or use your local URL if running locally: http://localhost:8000/auth/etsy/login)*

3. **You'll be redirected to Etsy** → Click "Allow"
4. **You'll be redirected back** → Tokens are saved automatically
5. **Shop ID is automatically detected** from your Etsy account!

---

## 📋 Printful API Credentials

### Step 1: Log into Printful

1. **Go to:** https://www.printful.com
2. **Log in** (or create account if needed)

### Step 2: Get API Key

1. **Click** your profile icon (top right)
2. **Go to:** Settings → **API**
3. **Click** "Create API token" or "Generate API key"
4. **Copy** your API key

**Alternative path:**
- Go directly to: https://www.printful.com/dashboard/api
- Click "Create new key" or "Generate API key"

### Step 3: Add to Environment Variables

Add to your `.env` file or Cloud Run environment variables:
```env
PRINTFUL_API_KEY=your_printful_api_key_here
```

---

## 🚀 Quick Setup for Cloud Run

### Add Credentials to Cloud Run

**Option 1: Via Command Line**
```powershell
gcloud run services update automerch \
  --update-env-vars="ETSY_CLIENT_ID=your_client_id,ETSY_CLIENT_SECRET=your_secret,ETSY_SHOP_ID=your_shop_id,ETSY_REDIRECT_URI=https://automerch-715156784717.us-central1.run.app/auth/etsy/callback,PRINTFUL_API_KEY=your_printful_key,AUTOMERCH_DRY_RUN=false" \
  --region us-central1 \
  --project automerch-app
```

**Option 2: Via Cloud Console**
1. Go to: https://console.cloud.google.com/run?project=automerch-app
2. Click on `automerch` service
3. Click "EDIT & DEPLOY NEW REVISION"
4. Scroll to "Variables & Secrets"
5. Add each variable:
   - `ETSY_CLIENT_ID` = `your_client_id`
   - `ETSY_CLIENT_SECRET` = `your_secret`
   - `ETSY_SHOP_ID` = `your_shop_id`
   - `ETSY_REDIRECT_URI` = `https://automerch-715156784717.us-central1.run.app/auth/etsy/callback`
   - `PRINTFUL_API_KEY` = `your_printful_key`
   - `AUTOMERCH_DRY_RUN` = `false`
6. Click "DEPLOY"

---

## 📝 Quick Reference

### Etsy URLs:
- **Developer Portal:** https://www.etsy.com/developers/register
- **Your Apps:** https://www.etsy.com/your/apps
- **Shop Settings:** https://www.etsy.com/your/shops/me/tools/settings
- **OAuth Login:** https://automerch-715156784717.us-central1.run.app/auth/etsy/login

### Printful URLs:
- **Dashboard:** https://www.printful.com/dashboard
- **API Settings:** https://www.printful.com/dashboard/api

### Required Environment Variables:

| Variable | Where to Get It |
|----------|----------------|
| `ETSY_CLIENT_ID` | Etsy Developer Portal → Your App → Keystring |
| `ETSY_CLIENT_SECRET` | Etsy Developer Portal → Your App → Shared Secret |
| `ETSY_SHOP_ID` | Etsy Shop Settings → Shop ID (or auto-detected via OAuth) |
| `ETSY_REDIRECT_URI` | `https://automerch-715156784717.us-central1.run.app/auth/etsy/callback` |
| `PRINTFUL_API_KEY` | Printful Dashboard → Settings → API → Create Token |

---

## ✅ After Setup Checklist

- [ ] Etsy app registered with correct redirect URI
- [ ] Etsy Client ID copied
- [ ] Etsy Client Secret copied
- [ ] Etsy Shop ID found (or will auto-detect via OAuth)
- [ ] Printful API key generated
- [ ] All credentials added to Cloud Run environment variables
- [ ] `AUTOMERCH_DRY_RUN=false` set
- [ ] OAuth flow completed at `/auth/etsy/login`
- [ ] Test research page - should show real images!

---

## 💡 Pro Tips

1. **Shop ID Auto-Detection:** After completing OAuth, your shop ID is automatically detected and saved. You can check it at `/api/shops` endpoint.

2. **Multiple Shops:** Your app supports multiple Etsy shops! After OAuth, each shop is automatically added. Set a default shop in the Settings page.

3. **Testing:** Keep `AUTOMERCH_DRY_RUN=true` while testing, then set to `false` when ready for real data.

4. **Security:** Never commit `.env` files or expose API keys in public repositories!

