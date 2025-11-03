# 🧪 How to Test AutoMerch Lite

## Quick Test Steps

### 1. Run Test Suite
```powershell
cd automerch_remote
python test_automerch_lite.py
```

**Expected:** All 8 tests should pass ✅

---

### 2. Start the Server
```powershell
cd automerch_remote
python run_automerch_lite.py --mode lite --reload
```

**Expected output:**
```
🚀 Starting AutoMerch Lite on port 8000
📖 API docs: http://localhost:8000/docs
📋 Drafts UI: http://localhost:8000/drafts
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 3. Test in Browser

Open these URLs in your browser:

- **Health Check**: http://localhost:8000/health
  - Should return: `{"ok":true,"status":"healthy"}`

- **API Documentation**: http://localhost:8000/docs
  - Should show FastAPI Swagger UI with all endpoints

- **Drafts Queue UI**: http://localhost:8000/drafts
  - Should show the drafts queue page

---

### 4. Test API Endpoints (via curl or browser)

**Health endpoint:**
```powershell
curl http://localhost:8000/health
```

**Get drafts queue:**
```powershell
curl http://localhost:8000/api/drafts/queue
```

**Create a test draft (dry-run mode):**
```powershell
curl -X POST http://localhost:8000/api/drafts/new `
  -H "Content-Type: application/json" `
  -d '{"sku":"TEST-001","title":"Test Product","description":"Test","price":19.99,"taxonomy_id":6947}'
```

---

### 5. Test Example Scripts

**Create single draft:**
```powershell
python examples/create_single_draft.py
```

**List all drafts:**
```powershell
python examples/list_all_drafts.py
```

---

## ✅ What Should Work

- ✅ All imports successful
- ✅ Database initializes
- ✅ FastAPI app starts
- ✅ Health endpoint responds
- ✅ API docs available
- ✅ Draft creation (dry-run mode)
- ✅ All endpoints accessible

---

## ❌ Common Issues

**Port 8000 already in use:**
```powershell
python run_automerch_lite.py --mode lite --port 8001
```

**Import errors:**
```powershell
python -m pip install sqlmodel fastapi uvicorn
```

**Database errors:**
- Check that `automerch.db` can be created
- Check file permissions

---

## 🎯 Full Test Checklist

- [ ] Test suite passes (8/8)
- [ ] Server starts without errors
- [ ] Health endpoint works
- [ ] API docs load
- [ ] Drafts UI loads
- [ ] Can create draft (dry-run)
- [ ] Can list drafts
- [ ] OAuth URL generation works

