# 🚀 AutoMerch Lite - Start Here!

## ✅ Setup Complete!

All tests passed (8/8). The app is ready to run!

---

## 📝 Quick Start

### 1. Configure Environment Variables

Edit `.env` and add your credentials:

```bash
# Required for OAuth
ETSY_CLIENT_ID=your_etsy_client_id
ETSY_CLIENT_SECRET=your_etsy_client_secret
ETSY_SHOP_ID=your_etsy_shop_id

# Keep this true for safe testing
AUTOMERCH_DRY_RUN=true
```

**To get Etsy credentials:**
1. Go to https://www.etsy.com/developers/register
2. Create an app
3. Get Client ID and Secret
4. Set Redirect URI: `http://localhost:8000/auth/etsy/callback`

---

### 2. Run the Application

**Option A: Run AutoMerch Lite only**
```bash
python run_automerch_lite.py --mode lite
```

**Option B: Run existing app (includes new routes)**
```bash
python run_automerch_lite.py --mode existing
```

**Option C: Run both side by side**
```bash
python run_automerch_lite.py --mode both
```

Or directly with uvicorn:
```bash
uvicorn automerch.api.app:app --reload
```

---

### 3. Access the Application

- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (automatic FastAPI docs)
- **Drafts Queue UI**: http://localhost:8000/drafts
- **Health Check**: http://localhost:8000/health

---

### 4. Complete OAuth Setup

1. Visit: http://localhost:8000/auth/etsy/login
2. Authorize the app with Etsy
3. You'll be redirected back with tokens stored

---

### 5. Create Your First Draft

**Via API:**
```bash
curl -X POST http://localhost:8000/api/drafts/new \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "MUG-001",
    "title": "Coffee Mug - Test",
    "description": "A beautiful coffee mug",
    "price": 14.99,
    "taxonomy_id": 6947,
    "tags": ["mug", "coffee", "gift"]
  }'
```

**Via Python Script:**
```bash
python examples/create_single_draft.py
```

**Via UI:**
- Visit http://localhost:8000/drafts
- Use the "Create Draft" button

---

## 🧪 Testing

**Run test suite:**
```bash
python test_automerch_lite.py
```

**Expected output:** All 8 tests should pass ✅

---

## 📚 Available Endpoints

### Authentication
- `GET /auth/etsy/login` - Start OAuth flow
- `GET /auth/etsy/callback` - OAuth callback
- `POST /auth/etsy/refresh` - Refresh token

### Drafts
- `POST /api/drafts/new` - Create single draft
- `POST /api/drafts/batch` - Create multiple drafts
- `GET /api/drafts/queue` - List all drafts
- `GET /api/drafts/{listing_id}` - Get draft details
- `GET /drafts` - Draft queue UI

### Assets
- `POST /api/assets/upload` - Upload asset metadata
- `GET /api/assets/{sku}` - Get assets for SKU

---

## 🎯 Example Workflows

### Create Draft from Product
```bash
python examples/create_draft_from_product.py MUG-001
```

### Batch Create Drafts
```bash
python examples/create_batch_drafts.py
```

### List All Drafts
```bash
python examples/list_all_drafts.py
```

---

## 🔧 Troubleshooting

**"No Etsy access token"**
- Complete OAuth flow at `/auth/etsy/login`
- Or set `ETSY_ACCESS_TOKEN` in `.env`

**"ETSY_SHOP_ID not set"**
- Add your shop ID to `.env`

**Import errors**
- Make sure you're in `automerch_remote/` directory
- Run: `python -m pip install -r requirements.txt`

**Port already in use**
- Change port: `python run_automerch_lite.py --port 8001`

---

## 🎉 Next Steps

1. ✅ Configure `.env` with your Etsy credentials
2. ✅ Run the app
3. ✅ Complete OAuth setup
4. ✅ Test creating a draft in dry-run mode
5. ✅ When ready, set `AUTOMERCH_DRY_RUN=false` for live API calls
6. ✅ Review drafts in Etsy Shop Manager
7. ✅ Publish when ready!

---

## 📖 Documentation

- `PLAN.md` - Original refactor plan
- `QUICK_START.md` - Quick reference guide
- `MIGRATION_GUIDE.md` - Integration with existing app
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `ALL_AGENTS_COMPLETE.md` - All tasks completed

---

**Happy Listing! 🚀**


