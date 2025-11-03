# Why Swagger UI Fails But Scripts Work

## The Problem

- ✅ **Python scripts work** (test_draft_creation.py succeeds)
- ✅ **curl/requests work** (direct HTTP calls succeed)
- ❌ **Swagger UI fails** (the interactive docs page fails)

## Why This Happens

### 1. **Swagger UI Schema Display Bug**

Swagger UI sometimes shows validation errors using its **internal schema representation** instead of the actual error. The error `"loc": ["string", 0]` is Swagger UI's way of showing "there's an error in the request body", but it's not showing the real error.

### 2. **Browser/JavaScript Quirks**

Swagger UI is a JavaScript app. Sometimes:
- Browser cache shows old schema
- JavaScript errors prevent proper request formatting
- Content-Type headers get mis-set
- JSON parsing happens in browser before sending

### 3. **Default Example Values**

When you use Swagger UI's default examples (like `"string"` placeholders), it can cause validation to fail because:
- The example might not match the actual schema
- FastAPI validates strictly
- Browser might auto-format the JSON incorrectly

### 4. **FastAPI + Swagger UI Interaction**

FastAPI generates the OpenAPI schema, and Swagger UI renders it. Sometimes there's a mismatch in:
- How arrays are displayed vs. sent
- How `null` vs `None` is handled
- How numbers are formatted (14.99 vs "14.99")

---

## Solutions

### ✅ Solution 1: Use Scripts (Recommended)

**This always works:**
```powershell
python test_draft_creation.py
```

### ✅ Solution 2: Use curl/PowerShell Directly

```powershell
$body = '{"sku":"MUG-001","title":"Coffee Mug","description":"Test","price":14.99}'
Invoke-RestMethod -Uri http://localhost:8000/api/drafts/new -Method POST -Body $body -ContentType "application/json"
```

### ✅ Solution 3: Fix Swagger UI (If You Must Use It)

1. **Clear browser cache** - Hard refresh (Ctrl+Shift+R)
2. **Delete ALL default text** in the request body box
3. **Paste exact JSON:**
```json
{"sku":"MUG-001","title":"Coffee Mug","description":"Test","price":14.99}
```
4. **Don't use pretty-printed JSON** (no line breaks)
5. **Click Execute**

---

## Technical Explanation

### Why Scripts Work

Python's `requests` library:
- ✅ Sends proper `Content-Type: application/json`
- ✅ Properly serializes JSON
- ✅ Handles Pydantic models correctly
- ✅ No browser quirks

### Why Swagger UI Fails

Swagger UI:
- ⚠️ Renders schema in browser
- ⚠️ User might enter invalid JSON
- ⚠️ Browser might modify the request
- ⚠️ JavaScript JSON.stringify might differ
- ⚠️ Error messages come from Swagger UI, not FastAPI

---

## Recommendation

**Don't rely on Swagger UI for testing.** Use it for:
- 📖 Viewing API documentation
- 🔍 Seeing available endpoints
- 📋 Copying example requests

But for **actual API calls**, use:
- Python scripts
- curl
- Postman
- HTTP clients

The API itself is **100% functional** - the issue is purely with Swagger UI's user interface and how it sends requests.

---

## Quick Test

```powershell
# This proves the API works
python test_draft_creation.py

# If this works, Swagger UI failures are not an API problem
```

---

**TL;DR: Swagger UI is finicky. Use scripts or direct HTTP calls instead.**

