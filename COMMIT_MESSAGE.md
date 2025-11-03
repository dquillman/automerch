# Git Commit Message for AutoMerch Lite

## Suggested Commit Message:

```
feat: Add AutoMerch Lite - Drafts-first Etsy automation

Implements AutoMerch Lite refactor plan with new package structure:

Core Features:
- New automerch/ package with modular structure
- OAuth2 authentication for Etsy
- Draft listing creation service
- Enhanced error handling with retries
- Rate limit management

New Structure:
- automerch/core/ - Settings, DB, OAuth
- automerch/models/ - Data models (Product, Listing, Asset, Token)
- automerch/services/ - Etsy, Printful, Drive clients
- automerch/api/ - FastAPI routes and app
- automerch/ui/ - Draft queue UI

API Endpoints:
- POST /api/drafts/new - Create single draft
- POST /api/drafts/batch - Bulk draft creation
- GET /api/drafts/queue - List all drafts
- GET /drafts - Enhanced UI with search/filters

Tools & Scripts:
- run_automerch_lite.py - Unified entry point
- test_automerch_lite.py - Comprehensive test suite
- Example scripts for common workflows

Fixes:
- Renamed http.py to http_client.py (Python stdlib conflict)
- Fixed relative import paths
- Added robust error handling and logging

Documentation:
- PLAN.md - Original refactor plan
- AGENT_ASSIGNMENTS.md - Work division
- START_HERE.md - Getting started guide
- QUICK_START.md - Quick reference

All tests passing (8/8)
```


