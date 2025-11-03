# 🔧 Debugging Internal Server Error

## Quick Fixes

### Most Common Issue: Missing OAuth Token

If you're trying to create a draft without OAuth:

**Error:** "No Etsy access token"

**Solution:**
1. In dry-run mode, drafts should still work - this might be a bug
2. Or complete OAuth: http://localhost:8000/auth/etsy/login

### Check Which Endpoint Failed

**Check server logs:**
- Look at the terminal where server is running
- Error message will show which route failed

**Common failing endpoints:**
- `/api/drafts/new` - Needs OAuth token (now shows better error)
- `/drafts` - Template path issue (now has fallback)
- `/api/drafts/queue` - Database issue (now has error handling)

---

## Test Specific Endpoints

**Test health (should always work):**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

**Test drafts queue (should work even if empty):**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/drafts/queue
```

**Test creating draft (needs token or will show 401):**
```powershell
$body = '{"sku":"TEST","title":"Test","description":"Test","price":19.99}'
Invoke-RestMethod -Uri http://localhost:8000/api/drafts/new -Method POST -Body $body -ContentType "application/json"
```

---

## Error Messages Now Show:

- ✅ 401 for missing OAuth token (with helpful message)
- ✅ 500 with details for other errors
- ✅ Template errors show fallback HTML
- ✅ Database errors are caught and reported

---

## Restart Server

After fixes, restart:
```powershell
# Stop server (Ctrl+C in terminal)
# Then restart:
python run_automerch_lite.py --mode lite
```

