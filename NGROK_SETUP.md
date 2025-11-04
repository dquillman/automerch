# 🔗 Using ngrok for Etsy OAuth (Local Development)

Etsy requires HTTPS redirect URIs, but localhost uses HTTP. Use ngrok to create an HTTPS tunnel.

---

## Quick Setup

### 1. Install ngrok

**Windows (PowerShell):**
```powershell
# Using winget (Windows Package Manager)
winget install ngrok

# Or using Chocolatey
choco install ngrok

# Or download manually from: https://ngrok.com/download
```

**Mac:**
```bash
brew install ngrok
```

**Linux:**
```bash
# Download from https://ngrok.com/download
# Or use snap
sudo snap install ngrok
```

### 2. Sign up for ngrok (Free)

1. Go to: https://dashboard.ngrok.com/signup
2. Create a free account
3. Get your authtoken from the dashboard
4. Configure ngrok:
   ```powershell
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

### 3. Start ngrok Tunnel

**In a separate terminal/PowerShell window:**

```powershell
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### 4. Register Etsy App with ngrok URL

1. Go to: https://www.etsy.com/developers/register
2. Register your app with:
   - **Redirect URI:** `https://abc123.ngrok.io/auth/etsy/callback`
   - (Use YOUR ngrok URL, not the example)

### 5. Update .env File

```env
ETSY_REDIRECT_URI=https://abc123.ngrok.io/auth/etsy/callback
ETSY_CLIENT_ID=your_client_id
ETSY_CLIENT_SECRET=your_secret
```

### 6. Start Your App

```powershell
python run_automerch_lite.py --mode lite
```

### 7. Complete OAuth

Visit: `https://abc123.ngrok.io/auth/etsy/login` (use YOUR ngrok URL)

---

## Important Notes

⚠️ **ngrok URL Changes:**
- Free ngrok URLs change each time you restart ngrok
- You'll need to update Etsy redirect URI if you restart ngrok
- **Solution:** Use ngrok's paid plan for static URLs, or keep ngrok running

⚠️ **Keep ngrok Running:**
- Don't close the ngrok terminal window
- Keep it running while using OAuth and testing

---

## Alternative: ngrok Static Domain (Paid)

If you want a permanent URL:

1. **Upgrade ngrok plan** (paid feature)
2. **Reserve a static domain:**
   ```powershell
   ngrok config edit
   # Add: tunnels.myapp: proto: http, addr: 8000
   ```
3. **Start with static domain:**
   ```powershell
   ngrok start myapp
   ```
4. **Use this URL for Etsy registration** - it won't change!

---

## Troubleshooting

### "ngrok not found"
- Make sure ngrok is installed and in your PATH
- Try: `ngrok version` to verify installation

### "Connection refused"
- Make sure your app is running on port 8000
- Check: `http://localhost:8000` works in browser

### "ngrok URL changed"
- This happens with free ngrok accounts
- Update Etsy redirect URI when URL changes
- Or use paid ngrok for static domain

### "OAuth redirect mismatch"
- Make sure Etsy redirect URI matches exactly (including https://)
- Check `.env` file has correct `ETSY_REDIRECT_URI`
- Restart your app after changing `.env`

---

## Quick Reference

```powershell
# Start ngrok
ngrok http 8000

# Check ngrok status
ngrok api tunnels list

# View ngrok web interface
# Open: http://localhost:4040
```

---

**Once set up, you can use ngrok URL for Etsy OAuth!** 🎉



