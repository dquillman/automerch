# Multi-Shop Support

AutoMerch Lite now supports managing multiple Etsy shops! This allows you to:

- Connect multiple Etsy shops via OAuth
- Store OAuth tokens separately for each shop
- Set a default shop for operations
- Create listings and manage drafts for specific shops
- Switch between shops when creating drafts

## Database Changes

### New Models

1. **EtsyShop** - Stores shop information
   - `shop_id` (primary key)
   - `shop_name` - Display name
   - `is_active` - Whether shop is enabled
   - `is_default` - Whether this is the default shop
   - `shop_url` - Link to shop on Etsy
   - `created_at`, `updated_at`

2. **OAuthToken** - Updated to support per-shop tokens
   - Added `shop_id` field
   - Unique constraint on `(provider, shop_id)`
   - Supports both legacy tokens (without shop_id) and new tokens (with shop_id)

3. **Listing** - Updated to track shop association
   - Added `shop_id` field to track which shop a listing belongs to

### Migration

The database automatically migrates existing data:
- OAuth tokens without `shop_id` continue to work (legacy mode)
- New columns are added to existing tables
- Existing listings are preserved (shop_id will be NULL for legacy listings)

## API Changes

### Shop Management Endpoints

- `GET /api/shops` - List all shops
- `GET /api/shops/default` - Get default shop
- `GET /api/shops/{shop_id}` - Get shop details
- `POST /api/shops` - Create or update shop
- `DELETE /api/shops/{shop_id}` - Delete shop
- `POST /api/shops/{shop_id}/set-default` - Set default shop

### Draft Creation

When creating drafts, you can specify a `shop_id`:

```json
{
  "sku": "MUG-001",
  "title": "Coffee Mug",
  "description": "...",
  "price": 14.99,
  "shop_id": "12345678"  // Optional - uses default if not provided
}
```

Or use query parameter:
```
POST /api/drafts/new?shop_id=12345678
```

### OAuth Callback

The OAuth callback now automatically detects the shop ID from the Etsy API:

```
GET /auth/etsy/callback?code=...&shop_id=12345678
```

If `shop_id` is not provided, it will be automatically detected from the connected Etsy account.

## Usage

### Adding a Shop

1. Go to **Settings** page
2. Click **"Connect via OAuth"** to authenticate
3. The shop will be automatically added when you complete OAuth

Or manually:
1. Enter shop ID in the "Add New Shop" field
2. Click **"Add Shop"**
3. Then connect via OAuth to enable it

### Setting Default Shop

1. Go to **Settings** page
2. Find the shop in the list
3. Click **"Set Default"** button

The default shop will be used for all operations when no shop is specified.

### Creating Drafts for Specific Shop

When creating a draft via API, include `shop_id` in the request:

```bash
curl -X POST http://localhost:8000/api/drafts/new \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "MUG-001",
    "title": "My Product",
    "description": "...",
    "price": 14.99,
    "shop_id": "12345678"
  }'
```

Or use query parameter:
```bash
curl -X POST "http://localhost:8000/api/drafts/new?shop_id=12345678" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Backward Compatibility

- Legacy OAuth tokens (without shop_id) continue to work
- Existing code that doesn't specify shop_id will use the default shop or fall back to legacy behavior
- Environment variable `ETSY_SHOP_ID` still works for single-shop setups

## UI Features

The Settings page now includes:
- **Shop Management Section** - List all connected shops
- **Add Shop Button** - Manually add shop IDs
- **OAuth Connection** - Connect shops via OAuth
- **Set Default** - Mark a shop as default
- **Delete Shop** - Remove shops (also removes OAuth tokens)

## Technical Details

### Dependency Injection

The `EtsyClient` dependency automatically:
1. Uses `shop_id` from query parameter if provided
2. Falls back to default shop if available
3. Falls back to legacy token (without shop_id) if no shop is configured

### OAuth Flow

1. User clicks "Connect via OAuth"
2. Redirected to Etsy OAuth
3. After authorization, callback receives code
4. Code is exchanged for tokens
5. Shop ID is automatically detected from Etsy API
6. Token is stored with shop_id association
7. Shop record is created/updated

### Token Management

- Each shop has its own OAuth token
- Tokens are automatically refreshed when expired
- Tokens can be manually refreshed via `/auth/etsy/refresh`
- Deleting a shop also removes its OAuth tokens




