I want to build a personal "opportunity scout" that runs unattended on my Mac every night and sends me a digest by morning. Help me build it from scratch.

## What it should do

Every night it goes out, reads a bunch of places on the internet where people complain about things or share what they're working on, and figures out two categories for me:

1. **Projects I could actually build and ship** — small enough for one person, something I could publish, open-source, or charge a few bucks for.
2. **Startup-shaped problems** — recurring pains that multiple unrelated people are describing in the same week.

By 6am I want one Telegram message with the good stuff. Not a link dump — I want it to tell me *why* each thing matters and who has the problem.

## My constraints

- MacBook M4, 24GB unified memory. This is the only machine.
- Must be completely free to run. No paid APIs, no cloud hosting, no subscriptions.
- **Processing only runs between 02:00 and 05:00.** I don't want it eating resources or heating the machine while I'm using it.
- **The Telegram message must arrive at 06:00, no exceptions.**
- I want a local web UI I can open in a browser to read the archive, tune what it looks for, and see what happened during the run.

## Hard requirements — please design around these!

These matter more to me than any feature:

1. **Delivery must never depend on processing finishing.** If the pipeline dies at 3am, I still want a 6am message telling me it died. Two separate jobs, talking only through the database.
2. **Everything must be deadline-aware.** When the 5am window closes, stages should truncate gracefully and ship a partial result. Never hang, never run past the window.
3. **Cheap filtering before expensive filtering.** Don't run a local LLM over a thousand items — narrow it down with plain code first, then let the model see the survivors.
4. **All state in SQLite.** No in-memory pipeline state, no temp files. Any stage should be re-runnable on its own. I want crash recovery for free.
5. **The LLM extracts and ranks from real scraped text. It never brainstorms from a blank prompt.** I don't want generated slop about AI-powered todo apps.
6. **Dedupe properly.** I don't want to see the same Hacker News thread five mornings in a row.

## Stack I'm thinking

Push back if any of this is wrong for the job:

- Python 3.12 with `uv`
- `launchd` for scheduling (not cron — I need it to catch up after sleep) plus `pmset` to wake the machine
- Ollama running a ~14B model for scoring, plus a small embedding model
- `httpx` async + `tenacity` for fetching, `feedparser` for RSS, `trafilatura` for article text
- SQLite in WAL mode with FTS5 and sqlite-vec
- Pydantic for schema-locked LLM output — I don't want to parse freeform prose
- FastAPI + Jinja2 + HTMX + Tailwind for the local UI
- Telegram Bot API over plain HTTP
- Bot token in macOS Keychain, not in a config file

Sources I want to pull from: Hacker News (Algolia API), Reddit JSON endpoints, GitHub API, arXiv, Product Hunt, and arbitrary RSS feeds I can add later from the UI.

## What I don't want

No Docker, no Airflow or Prefect or Temporal, no vector database, no message queue, no React SPA, no agent framework. This is one user on one machine — I don't want an orchestrator that costs more RAM than the model.

## The UI

Five pages, read-mostly:

- **Today** — the digest, with thumbs up / thumbs down / save on each item
- **Archive** — full-text search across everything ever collected
- **Sources** — enable/disable, add an RSS URL, see which sources are failing
- **Profile** — my keyword boosts, block list, and the scoring prompt itself, all editable without touching code
- **Runs** — per-stage timings and item counts, so I can see where the 3 hours went

Plus a "run now" button with dry-run and limit flags so I can test without waiting until 2am.

## Later, once it works

I want it to learn my taste. My saved items should build up a preference signal that feeds back into the filtering, so month-three digests are better targeted than week-one digests without me editing prompts.

Further out I'm interested in distilling the scoring stage — using the big model's nightly outputs as training data to fine-tune something small and fast, so the filter can let through 400 items a night instead of 120. But only after the basic version is running and I've confirmed my feedback data is actually predictive. Design the LLM layer behind an interface so swapping backends is a config change, not a rewrite.

## How I want you to help

Build it in phases where each phase ends in something that actually works, not something half-finished.

**Start with Phase 0: the boring infrastructure.** Repo scaffold, database schema, the launchd agents, the wake schedule, the Telegram bot registered — and a fake hardcoded digest that gets delivered. I want to wake up to a message from my own machine before we write a single line of intelligence. I know that "does the Mac actually wake up and fire the job" is the thing that silently kills projects like this, so I want it proven first.

Don't write all the phases at once. Give me Phase 0, let me run it overnight, and we'll go from there.