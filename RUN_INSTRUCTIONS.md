# 🚀 How to Run AutoMerch Lite

## Quick Start

### From the `automerch` directory:
```powershell
cd automerch_remote
python run_automerch_lite.py --mode lite
```

### Or run directly:
```powershell
python automerch_remote\run_automerch_lite.py --mode lite
```

### Or use uvicorn directly:
```powershell
cd automerch_remote
uvicorn automerch.api.app:app --reload
```

---

## 📍 Directory Structure

```
automerch/
├── automerch_remote/          ← You need to be HERE
│   ├── run_automerch_lite.py  ← The script
│   ├── automerch/              ← The package
│   └── ...
└── ...
```

---

## ✅ Verify You're in the Right Place

```powershell
# Check current directory
Get-Location

# Should show: G:\Users\daveq\automerch\automerch_remote

# Check if file exists
Test-Path run_automerch_lite.py
# Should return: True
```

---

## 🎯 Run Options

**Mode 1: AutoMerch Lite only (recommended)**
```powershell
cd automerch_remote
python run_automerch_lite.py --mode lite --reload
```

**Mode 2: Existing app**
```powershell
cd automerch_remote
python run_automerch_lite.py --mode existing --reload
```

**Mode 3: Both side by side**
```powershell
cd automerch_remote
python run_automerch_lite.py --mode both
```

---

## 🌐 Access the App

Once running, open in browser:
- **Main**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Drafts UI**: http://localhost:8000/drafts
- **Health**: http://localhost:8000/health

---

## ⚠️ Troubleshooting

**"can't open file"**
- Make sure you're in `automerch_remote` directory
- Or use full path: `python automerch_remote\run_automerch_lite.py`

**"Port already in use"**
- Change port: `python run_automerch_lite.py --mode lite --port 8001`
- Or stop other process using port 8000

**Import errors**
- Make sure you're in `automerch_remote` directory
- Install dependencies: `python -m pip install -r requirements.txt`





