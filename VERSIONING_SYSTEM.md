# Versioning System

Your AutoMerch app now has a complete versioning system!

## How It Works

1. **Version Source**: The version is read from `VERSION` file (currently `0.1.22`)
2. **Fallback**: If `VERSION` file doesn't exist, it tries:
   - Environment variable `AUTOMERCH_VERSION`
   - Git commit hash + date
   - Default: `1.0.0`

3. **Display**: Version appears in the header of all pages as `v0.1.22` (or current version)

## Current Version

Check `automerch_remote/VERSION` file - it currently contains:
```
0.1.22
```

## Updating the Version

To update the version:

1. **Edit the VERSION file:**
   ```bash
   # Edit automerch_remote/VERSION
   # Change to: 0.1.23 (or whatever version you want)
   ```

2. **Or set environment variable:**
   ```bash
   export AUTOMERCH_VERSION=0.1.23
   ```

3. **Restart the app** - the version will update automatically

## Version Display

The version appears:
- In the header navigation bar of all pages (top right)
- Via API endpoint: `/version` returns `{"version": "0.1.22"}`
- In health check: `/health` includes version in response

## Files Updated

✅ `automerch_remote/automerch/api/app.py` - Uses version from `version.py`
✅ `automerch_remote/automerch/ui/dashboard/dashboard.html` - Shows version in header
✅ `automerch_remote/automerch/ui/shared/nav.html` - Shows version in shared nav
✅ `automerch_remote/automerch/ui/research/research.html` - Shows version in header

## Remaining Pages

The following pages still need version added (if they have navigation):
- `automerch_remote/automerch/ui/products/create.html`
- `automerch_remote/automerch/ui/products/printful.html`
- `automerch_remote/automerch/ui/assets/assets.html`
- `automerch_remote/automerch/ui/drafts/create.html`
- `automerch_remote/automerch/ui/settings/settings.html`
- `automerch_remote/automerch/ui/analytics/analytics.html`
- `automerch_remote/automerch/ui/research/detail.html`
- `automerch_remote/automerch/ui/workflow/workflow.html`

These can be updated manually by adding the version span and script (see dashboard.html as example).

