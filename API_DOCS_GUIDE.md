# 📖 How to Use the API Docs UI

## Using Swagger UI (http://localhost:8000/docs)

### Step-by-Step: Creating a Draft

1. **Open:** http://localhost:8000/docs

2. **Find the endpoint:** Look for `POST /api/drafts/new`

3. **Click "Try it out"** button

4. **Clear the default example** and paste this EXACT JSON:

```json
{
  "sku": "TEST-001",
  "title": "Test Coffee Mug",
  "description": "A beautiful test mug",
  "price": 14.99,
  "taxonomy_id": 6947,
  "tags": [],
  "images": null
}
```

**IMPORTANT:**
- Remove the default example that shows `"string"` placeholders
- Use real values for all fields
- Make sure `price` is a number (14.99), not a string
- Make sure `tags` is an array `[]`, not a string
- Make sure `images` is `null` or an array, not a string

5. **Click "Execute"**

---

## Common Mistakes in Swagger UI

### ❌ Wrong (default example):
```json
{
  "sku": "string",    ← Don't use literal "string"
  "title": "string",  ← Use actual text
  "price": "string"   ← Price must be a number
}
```

### ✅ Correct:
```json
{
  "sku": "TEST-001",
  "title": "My Coffee Mug",
  "description": "A beautiful mug",
  "price": 14.99,        ← Number, not string
  "taxonomy_id": 6947,   ← Number
  "tags": [],            ← Array, not string
  "images": null         ← null or []
}
```

---

## Quick Copy-Paste Template

**Minimal (required fields only):**
```json
{
  "sku": "MUG-001",
  "title": "Coffee Mug",
  "description": "A mug",
  "price": 14.99
}
```

**Full (all fields):**
```json
{
  "sku": "MUG-001",
  "title": "Coffee Mug - Adventure Awaits",
  "description": "Beautiful 11oz ceramic mug",
  "price": 14.99,
  "taxonomy_id": 6947,
  "tags": ["mug", "coffee", "gift"],
  "images": null
}
```

---

## Validation Error?

If you see validation errors:
1. Check that all required fields are present
2. Make sure `price` is a number (not quoted)
3. Make sure `tags` is an array `[]` (not a string)
4. Make sure `taxonomy_id` is a number (not quoted)
5. Make sure you cleared the default example first

---

## Test Via Script (Easier!)

Instead of using the UI, try:
```powershell
python examples/create_single_draft.py
```

Or:
```powershell
python test_draft_creation.py
```

These work perfectly and don't have UI quirks!

