# 🔍 How to Find Your Etsy Shop ID

Your Etsy Shop ID is a number (usually 8-10 digits) that uniquely identifies your shop. Here are multiple ways to find it:

---

## Method 1: Shop Settings Page (Easiest & Most Reliable)

### Step-by-Step:

1. **Log into your Etsy account**
   - Go to: https://www.etsy.com
   - Make sure you're logged in

2. **Go to Shop Manager**
   - Click your profile icon (top right)
   - Click **"Shop Manager"** from the dropdown
   - Or go directly to: https://www.etsy.com/your/shops/me/dashboard

3. **Navigate to Shop Settings**
   - In the left sidebar, click **"Settings"**
   - Or go directly to: https://www.etsy.com/your/shops/me/tools/settings

4. **Find Shop ID**
   - Scroll down the settings page
   - Look for a section labeled **"Shop ID"** or **"Shop Information"**
   - Your Shop ID will be a number (like `12345678` or `87654321`)
   - **Copy this number**

---

## Method 2: From Your Shop URL

### If your shop URL looks like this:
```
https://www.etsy.com/shop/YourShopName
```

### Steps:
1. **Go to your shop page** (the public-facing page)
2. **Right-click** anywhere on the page
3. **Select "View Page Source"** (or press `Ctrl+U` on Windows)
4. **Press `Ctrl+F`** to open search
5. **Search for:** `shop_id` or `shopId`
6. **Look for a number** after `shop_id` like: `"shop_id":12345678`
7. **Copy that number**

---

## Method 3: Using Browser Developer Tools

### Steps:
1. **Go to your shop page:** `https://www.etsy.com/shop/YourShopName`
2. **Press `F12`** (or right-click → "Inspect")
3. **Click the "Console" tab**
4. **Type this and press Enter:**
   ```javascript
   window.__INITIAL_STATE__.shop.id
   ```
   Or try:
   ```javascript
   document.querySelector('[data-shop-id]').dataset.shopId
   ```
5. **The Shop ID will appear** as a number

---

## Method 4: From Shop Listings Page

### Steps:
1. **Go to:** https://www.etsy.com/your/shops/me/tools/listings
2. **Right-click** on any listing
3. **Click "Inspect"** or press `F12`
4. **Search for:** `shop_id` in the HTML
5. **Look for the number** associated with your shop

---

## Method 5: Via Etsy API (After OAuth)

### If you've already set up OAuth:

1. **Complete OAuth flow** (visit `/auth/etsy/login`)
2. **Check your app's API endpoint:**
   - Go to: `https://automerch-715156784717.us-central1.run.app/api/shops`
   - Your shop ID will be automatically detected and shown
   - Or check: `https://automerch-715156784717.us-central1.run.app/settings`

---

## Method 6: Contact Etsy Support

If none of the above methods work:

1. **Go to:** https://www.etsy.com/help
2. **Contact Etsy Support**
3. **Ask:** "What is my Shop ID?"
4. **They'll provide it** (usually within 24 hours)

---

## Visual Guide for Method 1 (Recommended)

```
1. Login to Etsy
   ↓
2. Click Profile Icon (top right)
   ↓
3. Click "Shop Manager"
   ↓
4. Click "Settings" (left sidebar)
   ↓
5. Scroll down to "Shop Information"
   ↓
6. Find "Shop ID: 12345678" ← This is it!
```

---

## What Does a Shop ID Look Like?

- **Format:** Usually 8-10 digits
- **Examples:** 
  - `12345678`
  - `87654321`
  - `1234567890`
- **Not:** Your shop name (like "MyCoolShop")
- **Not:** Your username
- **It's a NUMBER only**

---

## Troubleshooting

### "I can't find Shop ID in Settings"
- Try Method 2 (View Page Source)
- Or wait until after OAuth (Method 5) - it auto-detects!

### "I don't see Settings in Shop Manager"
- Make sure you're the shop owner
- Some accounts may have different layouts
- Try the direct URL: https://www.etsy.com/your/shops/me/tools/settings

### "The number I found doesn't work"
- Make sure it's just numbers (no letters)
- Copy it exactly (no spaces)
- Verify it's 8-10 digits long

---

## Pro Tip: You Don't Need It Immediately!

**Good news:** Your Shop ID can be **auto-detected** when you complete the OAuth flow!

1. Set up your Client ID and Secret first
2. Complete OAuth at `/auth/etsy/login`
3. Your Shop ID will be automatically detected and saved
4. You can check it later at `/api/shops`

---

## Quick Reference URLs

- **Shop Manager:** https://www.etsy.com/your/shops/me/dashboard
- **Shop Settings:** https://www.etsy.com/your/shops/me/tools/settings
- **Shop Listings:** https://www.etsy.com/your/shops/me/tools/listings
- **Your Shop Page:** https://www.etsy.com/shop/YourShopName (replace with your shop name)

---

**Still having trouble?** Let me know which method you tried and what you see, and I can help troubleshoot!

