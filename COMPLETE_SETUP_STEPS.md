# 🚀 Complete Setup Steps - Step by Step

## Current Status ✅
- ✅ Shop ID: `49206429` (added to .env)
- ✅ Etsy App: Registered (waiting for activation)

---

## Step 1: Get Etsy Client ID and Secret

### 1.1 Check if App is Active
1. **Go to:** https://www.etsy.com/your/apps
2. **Find your "AutoMerch" app**
3. **Check status:** Should say "Active" or "Active (Pending Review)"

### 1.2 Get Credentials
Once your app is **Active**:
1. **Click on your app** (AutoMerch)
2. **You'll see:**
   - **Keystring (Client ID)** - Copy this
   - **Shared Secret (Client Secret)** - Copy this
3. **Save these somewhere safe** (you'll need them)

---

## Step 2: Add Credentials to Cloud Run

### Option A: Via Command Line (I'll help you with this)

Once you have your Client ID and Secret, I'll run this command for you:

```powershell
gcloud run services update automerch \
  --update-env-vars="ETSY_CLIENT_ID=your_client_id,ETSY_CLIENT_SECRET=your_secret,ETSY_SHOP_ID=49206429,ETSY_REDIRECT_URI=https://automerch-715156784717.us-central1.run.app/auth/etsy/callback,AUTOMERCH_DRY_RUN=false" \
  --region us-central1 \
  --project automerch-app
```

**Just share your Client ID and Secret with me, and I'll run it!**

### Option B: Via Cloud Console

1. **Go to:** https://console.cloud.google.com/run?project=automerch-app
2. **Click** on `automerch` service
3. **Click** "EDIT & DEPLOY NEW REVISION"
4. **Scroll to** "Variables & Secrets" tab
5. **Add these variables:**
   - `ETSY_CLIENT_ID` = `your_client_id`
   - `ETSY_CLIENT_SECRET` = `your_secret`
   - `ETSY_SHOP_ID` = `49206429`
   - `ETSY_REDIRECT_URI` = `https://automerch-715156784717.us-central1.run.app/auth/etsy/callback`
   - `AUTOMERCH_DRY_RUN` = `false`
6. **Click** "DEPLOY"

---

## Step 3: Complete Etsy OAuth

### 3.1 Start OAuth Flow
1. **Visit:** https://automerch-715156784717.us-central1.run.app/auth/etsy/login
2. **You'll be redirected to Etsy**
3. **Click "Allow"** to authorize the app
4. **You'll be redirected back** - OAuth is complete!

### 3.2 Verify It Worked
- Check: https://automerch-715156784717.us-central1.run.app/api/shops
- You should see your shop information
- Shop ID should be confirmed as `49206429`

---

## Step 4: Get Printful API Key (Optional)

### 4.1 Log into Printful
1. **Go to:** https://www.printful.com
2. **Log in** (or create account if needed)

### 4.2 Get API Key
1. **Click** your profile icon (top right)
2. **Go to:** Settings → **API**
3. **Click** "Create API token" or "Generate API key"
4. **Copy** your API key

### 4.3 Add to Cloud Run
```powershell
gcloud run services update automerch \
  --update-env-vars="PRINTFUL_API_KEY=your_printful_key" \
  --region us-central1 \
  --project automerch-app
```

---

## ✅ Checklist

- [x] Shop ID added to .env (`49206429`)
- [ ] Etsy app is active
- [ ] Client ID obtained
- [ ] Client Secret obtained
- [ ] Credentials added to Cloud Run
- [ ] OAuth flow completed
- [ ] Printful API key obtained (optional)
- [ ] Printful API key added to Cloud Run (optional)

---

## 🎯 What to Do Right Now

1. **Check if your Etsy app is active:**
   - Go to: https://www.etsy.com/your/apps
   - Is it showing "Active" status?

2. **If active, get your Client ID and Secret**
   - Click on your app
   - Copy the Keystring (Client ID)
   - Copy the Shared Secret (Client Secret)

3. **Share them with me** and I'll add everything to Cloud Run for you!

---

**Ready? Let's check if your app is active first!**

