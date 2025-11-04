# 🧪 How to Test AutoMerch Lite

## Quick Test (5 minutes)

### Step 1: Run the Test Suite
```powershell
cd automerch_remote
python test_automerch_lite.py
```

**Expected:** You should see "✅ All tests passed!"

---

### Step 2: Start the Server
```powershell
python run_automerch_lite.py --mode lite
```

**You'll see:**
```
🚀 Starting AutoMerch Lite on port 8000
📖 API docs: http://localhost:8000/docs
📋 Drafts UI: http://localhost:8000/drafts
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this running** (don't close the terminal)

---

### Step 3: Open in Browser

Open these URLs in your web browser:

1. **Health Check**
   - http://localhost:8000/health
   - Should show: `{"ok":true,"status":"healthy"}`

2. **API Documentation**
   - http://localhost:8000/docs
   - Should show a Swagger UI with all API endpoints

3. **Drafts Queue UI**
   - http://localhost:8000/drafts
   - Should show the drafts queue page (empty at first)

---

### Step 4: Test Creating a Draft (Dry-Run Mode)

**Option A: Using PowerShell**
```powershell
# Open a NEW terminal window (keep server running)
cd automerch_remote
$body = '{"sku":"TEST-001","title":"Test Mug","description":"A test coffee mug","price":14.99,"taxonomy_id":6947}'
Invoke-RestMethod -Uri http://localhost:8000/api/drafts/new -Method POST -Body $body -ContentType "application/json"
```

**Option B: Using Python Script**
```powershell
# Open a NEW terminal window (keep server running)
cd automerch_remote
python examples/create_single_draft.py
```

**Option C: Using Browser**
1. Go to http://localhost:8000/docs
2. Find `POST /api/drafts/new`
3. Click "Try it out"
4. Enter this JSON:
```json
{
  "sku": "TEST-001",
  "title": "Test Coffee Mug",
  "description": "A beautiful test mug",
  "price": 14.99,
  "taxonomy_id": 6947,
  "tags": ["test", "mug"]
}
```
5. Click "Execute"

---

### Step 5: View the Draft

**Check the drafts queue:**
```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/drafts/queue
```

**Or visit in browser:**
- http://localhost:8000/drafts
- You should see your test draft listed

---

## 🎯 What to Test

### ✅ Basic Functionality
- [ ] Server starts without errors
- [ ] Health endpoint works
- [ ] API docs load
- [ ] Drafts UI loads
- [ ] Can create a draft
- [ ] Draft appears in queue

### ✅ API Endpoints
- [ ] `GET /health` - Returns healthy status
- [ ] `GET /api/drafts/queue` - Lists drafts (empty at first)
- [ ] `POST /api/drafts/new` - Creates new draft
- [ ] `GET /api/drafts/{id}` - Gets draft details

### ✅ Example Scripts
- [ ] `python examples/create_single_draft.py`
- [ ] `python examples/list_all_drafts.py`

---

## 🛑 When Done Testing

**Stop the server:**
- Go to the terminal where server is running
- Press `Ctrl+C`
- Server will stop

---

## ⚠️ Troubleshooting

**"Port 8000 already in use"**
```powershell
# Use a different port
python run_automerch_lite.py --mode lite --port 8001
```

**"Module not found"**
```powershell
# Install dependencies
python -m pip install sqlmodel fastapi uvicorn requests tenacity python-dotenv
```

**"Can't connect to server"**
- Make sure server is still running
- Check the terminal for errors
- Try restarting the server

---

## 📝 Test Checklist

After testing, you should be able to:
- ✅ Run test suite (all 8 tests pass)
- ✅ Start server successfully
- ✅ Access health endpoint
- ✅ View API documentation
- ✅ See drafts queue UI
- ✅ Create a draft (dry-run mode)
- ✅ View created draft in queue

---

## 🚀 Next Steps After Testing

1. **Add Etsy Credentials** to `.env`
2. **Test OAuth Flow** at `/auth/etsy/login`
3. **Create Real Drafts** (set `AUTOMERCH_DRY_RUN=false`)
4. **Review Code** on `feature/automerch-lite` branch
5. **Commit** when ready!




