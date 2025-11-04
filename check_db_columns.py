"""Check Product table columns."""
from automerch.core.db import engine

with engine.connect() as conn:
    result = conn.exec_driver_sql("PRAGMA table_info('product')")
    cols = {row[1] for row in result}
    
    print("Product table columns:")
    for col in sorted(cols):
        print(f"  - {col}")
    
    print("\nRequired columns check:")
    required = {'cost', 'taxonomy_id', 'tags'}
    missing = required - cols
    if missing:
        print(f"  ❌ Missing: {missing}")
    else:
        print("  ✅ All required columns present!")




