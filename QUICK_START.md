# Quick Start Guide - AutoMerch Lite

## 🚀 Get Started in 5 Minutes

### 1. Set Up Environment

```bash
cd automerch_remote
cp .env.sample .env
```

Edit `.env` and add your credentials:
```
ETSY_CLIENT_ID=your_client_id
ETSY_CLIENT_SECRET=your_client_secret
ETSY_SHOP_ID=your_shop_id
AUTOMERCH_DRY_RUN=true  # Set to false when ready for live API
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Option A: Run new AutoMerch Lite API
uvicorn automerch.api.app:app --reload

# Option B: Run existing app (has both old and new routes)
uvicorn app:app --reload
```

### 4. Test It Out

1. **OAuth Setup:**
   - Visit: http://localhost:8000/auth/etsy/login
   - Complete OAuth flow
   - You'll be redirected back with tokens stored

2. **View Drafts Queue:**
   - Visit: http://localhost:8000/drafts
   - See all your draft listings

3. **Create a Draft via API:**
   ```bash
   curl -X POST http://localhost:8000/api/drafts/new \
     -H "Content-Type: application/json" \
     -d '{
       "sku": "MUG-001",
       "title": "Coffee Mug - Adventure Awaits",
       "description": "Vibrant 11oz ceramic mug perfect for creative dreamers.",
       "price": 14.99,
       "taxonomy_id": 6947,
       "tags": ["coffee", "mug", "gift"]
     }'
   ```

## 📝 Example Python Usage

```python
from automerch.services.etsy.drafts import EtsyDraftsService

# Create a draft
service = EtsyDraftsService()
result = service.create_draft(
    title="ENFP Coffee Mug - Adventure Awaits",
    description="Vibrant 11oz ceramic mug perfect for creative dreamers.",
    price=14.99,
    taxonomy_id=6947,
    tags=["enfp", "coffee", "mug", "gift"],
    images=["mockup1.png", "mockup2.png"]
)

print(f"Created draft: {result['listing_id']}")
print(f"View at: {result['etsy_url']}")
```

## 🎯 Workflow

1. **Generate assets** → Save to Google Drive (or local)
2. **Generate SEO copy** → Title, description, tags
3. **Create draft** → Call `/api/drafts/new` for each SKU
4. **Review in Etsy** → Go to Drafts Queue, assign shipping, publish

## 📊 API Endpoints

- `GET /auth/etsy/login` - Start OAuth
- `POST /api/drafts/new` - Create single draft
- `POST /api/drafts/batch` - Create multiple drafts
- `GET /api/drafts/queue` - List all drafts
- `GET /drafts` - Draft queue UI
- `GET /health` - Health check
- `GET /docs` - API documentation (FastAPI auto-generated)

## 🔍 Check Status

```bash
# Health check
curl http://localhost:8000/health

# Get drafts
curl http://localhost:8000/api/drafts/queue
```

## 🛠️ Troubleshooting

**"No Etsy access token"**
- Run OAuth flow at `/auth/etsy/login`
- Or set `ETSY_ACCESS_TOKEN` in `.env`

**"ETSY_SHOP_ID not set"**
- Add `ETSY_SHOP_ID=your_shop_id` to `.env`

**Import errors**
- Make sure you're in `automerch_remote/` directory
- Check Python path: `export PYTHONPATH=$PYTHONPATH:.`

## ✅ Next Steps

1. Test with `AUTOMERCH_DRY_RUN=true`
2. Review drafts in Etsy Shop Manager
3. Set `AUTOMERCH_DRY_RUN=false` when ready
4. Integrate with your existing product management UI


