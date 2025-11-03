# Environment Variables Setup Guide

## Quick Setup

1. **Create `.env` file** in the `automerch_remote` directory
2. **Copy the template** from `.env.example` 
3. **Fill in your credentials** (see below)

## Required Credentials

### Etsy API Credentials

1. **Register your app** at https://www.etsy.com/developers/register
2. **Create a new app** with these settings:
   - App Name: AutoMerch Lite (or your choice)
   - Redirect URI: `http://localhost:8000/auth/etsy/callback`
   - OAuth Scopes: `listings_r listings_w shops_r profile_r`
3. **Copy your credentials:**
   - Client ID (keystring)
   - Client Secret (shared secret)
   - Shop ID (found in your Etsy shop URL)

**Example:**
```env
ETSY_CLIENT_ID=abc123xyz789
ETSY_CLIENT_SECRET=def456uvw012
ETSY_SHOP_ID=123456789
```

### Printful API Key

1. **Log in** to your Printful account at https://www.printful.com
2. **Navigate to** Settings → API
3. **Click** "Printful Developers" or "Create API token"
4. **Copy** your API key

**Example:**
```env
PRINTFUL_API_KEY=abcdef1234567890
```

## Complete .env File Example

```env
# Etsy Configuration
ETSY_CLIENT_ID=your_actual_client_id
ETSY_CLIENT_SECRET=your_actual_secret
ETSY_SHOP_ID=123456789
ETSY_REDIRECT_URI=http://localhost:8000/auth/etsy/callback

# Printful Configuration
PRINTFUL_API_KEY=your_actual_api_key

# Database (default - usually fine)
AUTOMERCH_DB=sqlite:///automerch.db

# Dry Run Mode (start with true for safe testing)
AUTOMERCH_DRY_RUN=true
```

## Testing Your Setup

### With Dry Run Mode (Safe - No Real API Calls)

```bash
# Set in .env
AUTOMERCH_DRY_RUN=true
```

The app will work but won't make real API calls. Perfect for testing!

### Without Dry Run (Real API Calls)

```bash
# Set in .env
AUTOMERCH_DRY_RUN=false
```

⚠️ **Warning:** This will make real API calls to Etsy and Printful!

## Verification

After setting up `.env`, start the server:

```bash
python run_automerch_lite.py --mode lite
```

Visit:
- http://localhost:8000 - Dashboard
- http://localhost:8000/docs - API Documentation
- http://localhost:8000/auth/etsy/login - Test OAuth (if credentials set)

## Troubleshooting

### "No Etsy access token" error
- Make sure `ETSY_CLIENT_ID` and `ETSY_CLIENT_SECRET` are set
- Visit `/auth/etsy/login` to complete OAuth flow

### "PRINTFUL_API_KEY not set" error
- Set `PRINTFUL_API_KEY` in `.env`
- Or keep `AUTOMERCH_DRY_RUN=true` to bypass

### File not loading
- Make sure `.env` is in the `automerch_remote` directory
- Restart the server after changing `.env`
- Check that `python-dotenv` is installed: `pip install python-dotenv`

## Security Notes

⚠️ **Never commit `.env` to git!** 

The `.env` file is already in `.gitignore` to prevent accidental commits. Keep your API keys secret!

