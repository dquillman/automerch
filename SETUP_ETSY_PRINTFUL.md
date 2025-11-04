# 🔑 Setup Etsy and Printful Credentials

Follow these steps to get real data (including images) from Etsy and connect to Printful.

---

## 📋 Step 1: Get Etsy API Credentials

### 1.1 Register Your App on Etsy

**⚠️ IMPORTANT:** Etsy requires HTTPS redirect URIs. For local development, you have two options:

#### Option A: Use ngrok (Recommended for Local Development)

1. **Install ngrok:**
   - Download from: https://ngrok.com/download
   - Or use: `winget install ngrok` (Windows)
   - Or: `choco install ngrok` (if you have Chocolatey)

2. **Start ngrok tunnel:**
   ```powershell
   ngrok http 8000
   ```
   This will give you an HTTPS URL like: `https://abc123.ngrok.io`

3. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

4. **Go to:** https://www.etsy.com/developers/register
5. **Click** "Register a new application"
6. **Fill in the form:**
   - **Application Name:** AutoMerch (or your choice)
   - **What best describes your application?** Choose "I want to sell items on Etsy"
   - **Redirect URI:** `https://abc123.ngrok.io/auth/etsy/callback` (use YOUR ngrok URL)
   - **Description:** "Automated listing management tool"
7. **Click** "Register application"
8. **After registration, you'll see:**
   - **Keystring (Client ID)** - Copy this
   - **Shared Secret (Client Secret)** - Copy this

**Important:** After registering, update your `.env` file with:
```env
ETSY_REDIRECT_URI=https://abc123.ngrok.io/auth/etsy/callback
```
(Replace `abc123.ngrok.io` with your actual ngrok URL)

#### Option B: Use a Production Domain (For Production Use)

If you have a production domain:
1. Use your production URL: `https://yourdomain.com/auth/etsy/callback`
2. Make sure your server is accessible at that URL
3. Register with Etsy using that URL

### 1.2 Get Your Shop ID

1. **Go to your Etsy shop** (e.g., `https://www.etsy.com/shop/YourShopName`)
2. **Look at the URL** - The shop ID is usually in the URL or:
3. **Go to:** https://www.etsy.com/your/shops/me/tools/settings
4. **Find "Shop ID"** in the settings

---

## 📋 Step 2: Get Printful API Key

### 2.1 Log into Printful

1. **Go to:** https://www.printful.com
2. **Log in** to your account (or create one if needed)

### 2.2 Create API Token

1. **Click** your profile icon (top right)
2. **Go to:** Settings → API
3. **Click** "Create API token" or "Printful Developers"
4. **Copy** your API key

**Note:** If you don't see the API section, you may need to enable developer mode first.

---

## 📋 Step 3: Create or Update .env File

### 3.1 Navigate to automerch_remote Directory

```powershell
cd G:\Users\daveq\automerch\automerch_remote
```

### 3.2 Create .env File

**If .env doesn't exist:**
```powershell
Copy-Item env.template .env
```

**Or create it manually:**
```powershell
New-Item .env -ItemType File
```

### 3.3 Edit .env File

Open `.env` in any text editor and add your credentials:

**If using ngrok:**
```env
# ==========================================
# Etsy OAuth Configuration
# ==========================================
ETSY_CLIENT_ID=your_actual_client_id_here
ETSY_CLIENT_SECRET=your_actual_secret_here
ETSY_SHOP_ID=your_actual_shop_id_here
ETSY_REDIRECT_URI=https://your-ngrok-url.ngrok.io/auth/etsy/callback
```
(Replace `your-ngrok-url.ngrok.io` with your actual ngrok URL)

**If using production domain:**
```env
# ==========================================
# Etsy OAuth Configuration
# ==========================================
ETSY_CLIENT_ID=your_actual_client_id_here
ETSY_CLIENT_SECRET=your_actual_secret_here
ETSY_SHOP_ID=your_actual_shop_id_here
ETSY_REDIRECT_URI=https://yourdomain.com/auth/etsy/callback
```

# ==========================================
# Printful API Configuration
# ==========================================
PRINTFUL_API_KEY=your_actual_printful_api_key_here

# ==========================================
# Database Configuration
# ==========================================
AUTOMERCH_DB=sqlite:///automerch.db

# ==========================================
# Dry Run Mode
# ==========================================
# Set to "false" to get REAL data from Etsy (including images)
# Set to "true" to use mock/test data (safe for testing)
AUTOMERCH_DRY_RUN=false
```

**Important:** 
- Replace `your_actual_client_id_here` with your real Etsy Client ID
- Replace `your_actual_secret_here` with your real Etsy Secret
- Replace `your_actual_shop_id_here` with your real Shop ID
- Replace `your_actual_printful_api_key_here` with your real Printful API key
- **Set `AUTOMERCH_DRY_RUN=false`** to get real images from Etsy!

---

## 📋 Step 4: Complete Etsy OAuth

### 4.1 Start ngrok (If using Option A)

**In a separate terminal window:**
```powershell
ngrok http 8000
```

**Copy the HTTPS URL** that ngrok provides (e.g., `https://abc123.ngrok.io`)

**Important:** Keep ngrok running while you complete OAuth!

### 4.2 Start the Server

```powershell
cd G:\Users\daveq\automerch\automerch_remote
python run_automerch_lite.py --mode lite
```

### 4.3 Complete OAuth Flow

**If using ngrok:**
1. **Open browser:** `https://your-ngrok-url.ngrok.io/auth/etsy/login` (use YOUR ngrok URL)
2. **You'll be redirected to Etsy** to authorize the app
3. **Click "Allow"** to grant permissions
4. **You'll be redirected back** - tokens will be saved automatically

**If using production domain:**
1. **Open browser:** `https://yourdomain.com/auth/etsy/login`
2. **You'll be redirected to Etsy** to authorize the app
3. **Click "Allow"** to grant permissions
4. **You'll be redirected back** - tokens will be saved automatically

**Alternative:** If OAuth doesn't work, you can manually set:
```env
ETSY_ACCESS_TOKEN=your_access_token_here
```

---

## 📋 Step 5: Test Your Setup

### 5.1 Test Research with Real Images

1. **Make sure `AUTOMERCH_DRY_RUN=false`** in `.env`
2. **Restart the server** (if it's running)
3. **Go to:** http://localhost:8000/research
4. **Enter a search term** (e.g., "coffee mug")
5. **Click "Research"**
6. **You should now see REAL images** from Etsy listings!

### 5.2 Verify Credentials

Check the server console for any errors. If you see:
- ✅ "OAuth token saved" - Etsy is working!
- ❌ "No Etsy access token" - Complete OAuth again
- ❌ "Invalid API key" - Check your Printful key

---

## 🎯 Quick Reference

### Etsy URLs:
- **Developer Portal:** https://www.etsy.com/developers/register
- **OAuth Settings:** https://www.etsy.com/your/apps
- **Shop Settings:** https://www.etsy.com/your/shops/me/tools/settings

### Printful URLs:
- **Dashboard:** https://www.printful.com/dashboard
- **API Settings:** https://www.printful.com/dashboard/api

### Important Environment Variables:

| Variable | Where to Get It |
|----------|----------------|
| `ETSY_CLIENT_ID` | Etsy Developer Portal → Your App → Keystring |
| `ETSY_CLIENT_SECRET` | Etsy Developer Portal → Your App → Shared Secret |
| `ETSY_SHOP_ID` | Your Etsy Shop Settings → Shop ID |
| `PRINTFUL_API_KEY` | Printful Dashboard → Settings → API → Create Token |

---

## ⚠️ Troubleshooting

### "No images showing in research"
- ✅ Make sure `AUTOMERCH_DRY_RUN=false` in `.env`
- ✅ Restart the server after changing `.env`
- ✅ Complete OAuth flow at `/auth/etsy/login`
- ✅ Check server console for error messages

### "OAuth not working"
- ✅ Check that `ETSY_REDIRECT_URI` matches exactly: `http://localhost:8000/auth/etsy/callback`
- ✅ Verify Client ID and Secret are correct (no extra spaces)
- ✅ Make sure the app is registered on Etsy

### "Printful errors"
- ✅ Verify API key is correct
- ✅ Check Printful account status (some features require active subscription)
- ✅ Keep `AUTOMERCH_DRY_RUN=true` if you only need Etsy

---

## 🔒 Security Notes

⚠️ **NEVER commit `.env` to git!**

The `.env` file contains sensitive credentials. It's already in `.gitignore`, but double-check before committing!

---

## ✅ Success Checklist

- [ ] Etsy app registered
- [ ] Etsy Client ID added to `.env`
- [ ] Etsy Client Secret added to `.env`
- [ ] Etsy Shop ID added to `.env`
- [ ] Printful API key added to `.env`
- [ ] `AUTOMERCH_DRY_RUN=false` in `.env`
- [ ] Server restarted
- [ ] OAuth flow completed
- [ ] Research shows real images!

---

**Once complete, you'll get real Etsy listings with actual images in your research results!** 🎉

