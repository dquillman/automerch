# 🔧 Quick Fix: Validation Error

## The Problem
You're seeing a generic validation error with "string" placeholders. This happens when you use the default example in Swagger UI.

## The Solution

### Option 1: Use Correct JSON (Recommended)

In Swagger UI at http://localhost:8000/docs:

1. Find `POST /api/drafts/new`
2. Click "Try it out"
3. **DELETE the default example**
4. Paste this:

```json
{
  "sku": "MUG-001",
  "title": "Coffee Mug",
  "description": "A test mug",
  "price": 14.99
}
```

**Key points:**
- ✅ `price` is a NUMBER (14.99), NOT a string ("14.99")
- ✅ `tags` should be an array `[]`, NOT a string
- ✅ All strings use actual text, NOT the word "string"

### Option 2: Use the Script (Easiest!)

```powershell
python examples/create_single_draft.py
```

This works perfectly and avoids UI issues.

---

## After Restart

After restarting the server, validation errors will now show:
- Which field has the problem
- What the error is
- What value you sent

Much more helpful!

---

## Valid JSON Template

**Minimal (just required fields):**
```json
{
  "sku": "MUG-001",
  "title": "My Coffee Mug",
  "description": "Description here",
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
  "tags": ["mug", "coffee"],
  "images": null
}
```

---

**Restart server and try again!** ✅




