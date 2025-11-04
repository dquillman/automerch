# 🧪 AutoMerch Lite - Test Plan

## ✅ Already Tested

1. ✅ **POST /api/drafts/new** - Single draft creation (working!)

---

## 📋 What to Test Next

### Priority 1: Core Draft Features

#### 1. Batch Draft Creation
```bash
python examples/test_all_endpoints.py
```
- Tests: `POST /api/drafts/batch`
- Creates multiple drafts at once
- **Why:** Bulk processing is a key feature

#### 2. Drafts Queue View
```bash
# Test the API endpoint
curl http://localhost:8000/api/drafts/queue

# Or visit in browser
http://localhost:8000/drafts
```
- Tests: `GET /api/drafts/queue` and `GET /drafts`
- Lists all created drafts
- **Why:** Main UI for managing drafts

#### 3. Get Single Draft
```bash
# Use a listing_id from previous tests
curl http://localhost:8000/api/drafts/{listing_id}
```
- Tests: `GET /api/drafts/{listing_id}`
- Retrieves details for one draft
- **Why:** Needed for viewing/editing individual drafts

---

### Priority 2: Asset Management

#### 4. Upload Asset Metadata
```bash
curl -X POST "http://localhost:8000/api/assets/upload?sku=TEST-001&asset_type=mockup&drive_url=https://test.com"
```
- Tests: `POST /api/assets/upload`
- Stores asset information in database
- **Why:** Tracks mockups and print files

#### 5. Get Assets for SKU
```bash
curl http://localhost:8000/api/assets/TEST-001
```
- Tests: `GET /api/assets/{sku}`
- Retrieves all assets for a product
- **Why:** Links products to their images/files

---

### Priority 3: Authentication (Optional - needs real credentials)

#### 6. Etsy OAuth Flow
- Tests: `GET /auth/etsy/login`, `GET /auth/etsy/callback`, `POST /auth/etsy/refresh`
- **Note:** Requires real Etsy credentials
- **Why:** Only needed for live API calls (dry-run works without it)

---

## 🚀 Quick Test Everything

Run the comprehensive test script:

```powershell
python examples/test_all_endpoints.py
```

This tests **all endpoints** automatically and gives you a summary.

---

## 📝 Testing Checklist

- [ ] Health endpoint (`/health`)
- [ ] Create single draft (`POST /api/drafts/new`) ✅
- [ ] Create batch drafts (`POST /api/drafts/batch`)
- [ ] Get drafts queue (`GET /api/drafts/queue`)
- [ ] Get single draft (`GET /api/drafts/{listing_id}`)
- [ ] Upload asset (`POST /api/assets/upload`)
- [ ] Get assets (`GET /api/assets/{sku}`)
- [ ] Drafts UI page (`GET /drafts`)
- [ ] Auth endpoints (optional - needs credentials)

---

## 🎯 Recommended Order

1. **Start with batch drafts** - Most similar to what you already tested
2. **Test drafts queue** - See what you've created
3. **Test single draft retrieval** - Get details on one item
4. **Test asset management** - Track images/files
5. **Test UI page** - Visual interface

---

## 📊 Expected Results

All tests should return:
- ✅ Status 200 (except auth, which may redirect)
- ✅ Valid JSON responses
- ✅ Proper data structure

If something fails:
- Check server logs
- Verify server is running
- Check database is accessible
- See error messages in response

---

## 🔍 Debugging

If a test fails:
1. Check the response status code
2. Read the error message
3. Check server console for stack traces
4. Verify the endpoint exists: http://localhost:8000/docs

---

**Next Step:** Run `python examples/test_all_endpoints.py` to test everything at once! 🚀




