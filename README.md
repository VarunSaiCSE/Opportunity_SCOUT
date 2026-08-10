# Opportunity SCOUT 🛸

SCOUT is a lightweight, highly optimized, and Mac-native autonomous research agent. It is designed to run entirely locally, respecting strict time constraints, to discover, filter, and score opportunities (problems/pain points) from across the web.

## Architecture & Features

The system is decoupled into three primary components:
1. **The Ingestion Pipeline (`src/scout/processor.py`)**: Runs on a cron/launchd schedule. Scrapes Hackernews, Reddit, and RSS feeds, deduplicates content via local embeddings, and uses a local Ollama LLM to extract and score genuine problems.
2. **The Delivery Agent (`src/scout/delivery.py`)**: A separate lightweight script that queries the SQLite database for top-scored opportunities and sends a digest via a Telegram Bot.
3. **The Retro Web Dashboard (`src/scout/web/app.py`)**: A local FastAPI web server featuring a beautifully clean, Japanese grid-style terminal interface. It allows you to view the database of opportunities with dynamic hover states and magic portal animations on click.

## File Structure

- `IDEA.md` - The foundational system architecture and constraint specification.
- `schema.sql` - The SQLite database schema for tracking discoveries, problems, and evidence.
- `scripts/`
  - `add_sources.py` - Seed the database with RSS and Reddit endpoints.
  - `test_sources.py` - Quick test script for the ingestion logic.
- `src/scout/`
  - `db.py` - Database connection management and raw SQLite queries.
  - `llm.py` - Interactions with the local Ollama LLM utilizing Pydantic for strict JSON schema output.
  - `processor.py` - The core "Funnel" pipeline: Ingest -> Filter -> LLM Extract -> LLM Score.
  - `delivery.py` - Telegram Bot delivery logic.
  - `sources/`
    - `hn.py` - HackerNews Algolia API scraper.
    - `reddit.py` - Reddit `.rss` endpoint scraper to bypass JSON rate limits.
    - `rss.py` - Generic RSS feed scraper.
  - `web/`
    - `app.py` - FastAPI server routing and database querying.
    - `templates/` - Jinja2 HTML templates featuring the strict Japanese grid UI, Lucide icons, and CSS keyframe animations.

## Setup

1. **Install uv**: Uses `uv` for lightning-fast dependency management.
2. **Run Pipeline**: `uv run python -m scout.processor`
3. **Run Web UI**: `uv run uvicorn scout.web.app:app --port 8000`
4. **Send Digest**: `uv run python -m scout.delivery`

Everything runs locally on SQLite and Ollama. Keep your Telegram token secure.
