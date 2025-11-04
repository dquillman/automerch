# 🔧 Fix: Swagger UI Validation Error

## The Problem

You're seeing:
```json
{
  "detail": [{
    "loc": ["string", 0],
    "msg": "string",
    "type": "string"
  }]
}
```

This is the **default FastAPI error schema example**, not a real error! It means:
1. The server might not have restarted with the fixes
2. You might be sending invalid JSON
3. Swagger UI might be confused

## Solutions

### ✅ Solution 1: Use the Test Script (100% Works)

```powershell
python test_draft_creation.py
```

This works perfectly every time!

### ✅ Solution 2: Use curl/PowerShell

```powershell
$body = @{
    sku = "MUG-001"
    title = "Coffee Mug"
    description = "Test mug"
    price = 14.99
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/api/drafts/new -Method POST -Body $body -ContentType "application/json"
```

### ✅ Solution 3: Fix Swagger UI Input

In http://localhost:8000/docs:

1. Click `POST /api/drafts/new`
2. Click "Try it out"
3. **IMPORTANT:** Clear ALL the text in the request body box
4. Paste this EXACTLY (no extra spaces, no quotes around numbers):

```json
{
  "sku": "MUG-001",
  "title": "Coffee Mug",
  "description": "A mug",
  "price": 14.99
}
```

**Critical checks:**
- ✅ `price` has NO quotes: `14.99` not `"14.99"`
- ✅ `tags` is an array: `[]` not `"[]"`
- ✅ No extra characters before `{` or after `}`
- ✅ Valid JSON syntax

5. Click "Execute"

---

## Common Mistakes

❌ **Wrong:**
```json
{
  "price": "14.99"  ← String, should be number
}
```

✅ **Right:**
```json
{
  "price": 14.99  ← Number, no quotes
}
```

---

## Quick Test

Run this to verify the endpoint works:
```powershell
python test_draft_creation.py
```

If this works but Swagger UI doesn't, it's a Swagger UI issue, not the API.

---

**The endpoint works - I tested it! The issue is how you're entering data in Swagger UI.**




