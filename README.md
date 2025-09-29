# AutoMerch

A lightweight starter for automating print-on-demand merchandising workflows (listing creation, asset handling, scheduling). The current repo includes runnable stubs, a simple SQLite database, and a jobs folder you can extend.

## Features
- SQLite schema via SQLModel (creates utomerch.db on first run)
- Pluggable clients (etsy_client.py, printful_client.py) with stubbed methods
- Jobs scaffold under jobs/ (weekly report, pull metrics, prune/scale, list to Etsy, intake to assets)
- .env-based configuration and basic CI via GitHub Actions

## Requirements
- Python 3.11+
- pip / venv

## Quick Start
1. Clone and create a virtualenv
   - python -m venv .venv && . .venv/Scripts/Activate (Windows)
   - python -m venv .venv && source .venv/bin/activate (macOS/Linux)
2. Install deps
   - pip install -r requirements.txt
3. Configure environment
   - Copy .env.sample to .env and set values (see Configuration)
4. Initialize and run
   - python app.py (creates the DB and prints readiness)

## Configuration
Environment variables (via .env):
- OPENAI_API_KEY: Optional. For creative/LLM features if you add them.
- PRINTFUL_API_KEY: Optional. Used by printful_client.py when implemented.
- ETSY_ACCESS_TOKEN: Optional. Used by etsy_client.py when implemented.
- ETSY_SHOP_ID: Optional. Target shop when listing via Etsy API.
- GOOGLE_SVC_JSON: Optional. Path to a Google service account JSON for Sheets.
- AUTOMERCH_DB: SQLAlchemy URL for the DB. Default sqlite:///automerch.db.
- AUTOMERCH_DRY_RUN: Set 	rue to avoid calling live APIs.

> Note: config.py loads .env. Clients are stubbed; wire up env vars as you implement real API calls.

## Running Jobs
- Jobs live in jobs/ and expose a un() function (stubs).
- Example (once you implement): python -c "from jobs.list_to_etsy import run; run()"
- scheduler.py is a placeholder for integrating APScheduler or cron.

## Project Structure
- pp.py: Entry point; initializes DB via db.init_db().
- db.py: SQLModel/SQLAlchemy engine and metadata creation.
- models.py: Example Product and RunLog tables.
- etsy_client.py, printful_client.py: API client stubs.
- jobs/: Task scripts (stubs) you can flesh out.
- docs/: Notes and planning docs.

## CI
- .github/workflows/ci.yml installs dependencies and compiles sources for a basic syntax check on push/PR to main.

## Contributing
- Use a virtualenv and keep large artifacts/zips out of the repo.
- Open PRs against main. CI must pass.

## License
MIT — see LICENSE.


## Web Server
- Run: uvicorn app:app --reload
- Open: http://localhost:8000

