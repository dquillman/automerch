# 🔧 Database Migration Fix

## Issue
The existing database table `product` was missing columns that the new model expects:
- `cost`
- `taxonomy_id` 
- `tags`

## Fix Applied
Added automatic migration in `automerch/core/db.py`:
- Checks existing Product table columns
- Adds missing columns automatically
- Runs on every `init_db()` call

## Verify Fix

**Check if columns exist:**
```python
from automerch.core.db import engine
from sqlmodel import text

with engine.connect() as conn:
    result = conn.exec_driver_sql("PRAGMA table_info('product')")
    cols = [row[1] for row in result]
    print("Columns:", cols)
```

**Should include:**
- `cost`
- `taxonomy_id`
- `tags`

## Restart Server

After the fix:
```powershell
python run_automerch_lite.py --mode lite
```

The migration runs automatically on startup now.

