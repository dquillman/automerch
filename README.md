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


## Scheduler
- Add schedules at /schedules to run jobs on an interval.
- Jobs log to the Logs page after each run.

## Products
- Fields: SKU, name, description, price. Add/update/delete from /products.

## Real API Integrations
- Etsy: Set `ETSY_ACCESS_TOKEN` and `ETSY_SHOP_ID`. In `jobs/list_to_etsy.py`, the draft listing uses `etsy_client.create_listing_draft`.
- Printful: Set `PRINTFUL_API_KEY`. Jobs call `printful_client` functions.
- Safety: `AUTOMERCH_DRY_RUN=true` prevents live API calls. Set `false` to enable.

## Docker
- Build and run: `docker compose up --build`
- Environment: copy `.env.sample` to `.env` and fill values.
- GHCR: Images are published to `ghcr.io/dquillman/automerch` on pushes to `main`.
## Etsy App Setup
- Create an app at Etsy Developers and note Client ID/Secret.
- Redirect URI: `http://localhost:8000/auth/etsy/callback` (or your deployed URL).
- Add to `.env`: `ETSY_CLIENT_ID`, `ETSY_CLIENT_SECRET`, optional `ETSY_REDIRECT_URI`.
- Visit `/integrations` and click Connect Etsy. With `AUTOMERCH_DRY_RUN=true`, actions are safe.

## Per-Product Actions
- In `/products`, edit fields (variant_id, thumbnail_url) and use:
  - “List to Etsy (draft)” to create a draft listing and store `etsy_listing_id`.
  - “Create in Printful” to create a product and store `printful_variant_id`.
## Images and Uploads
- Upload a product image via the edit panel on `/products`. The file is saved under `/media/products` and the URL is stored in `thumbnail_url`.
- Note: External APIs (Etsy/Printful) fetch media from accessible URLs. Local `/media` works for local testing; for production, host images on a public URL or upload directly via each API.

## Etsy Listing Management
- “List to Etsy (draft)” creates a draft listing and attempts to upload the product image.
- “Publish Etsy Listing” sets the listing state to `active`.
## S3 Bucket Policy (example)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::YOUR_BUCKET_NAME/*"]
    }
  ]
}

## IAM Policy for Uploader (example)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:PutObjectAcl"],
      "Resource": ["arn:aws:s3:::YOUR_BUCKET_NAME/*"]
    }
  ]
}
## Catalog
- Browse `/catalog` to search and paginate products, with image previews and links.

## Exports
- `GET /api/export/products.json` and `GET /api/export/products.csv` for data export.
