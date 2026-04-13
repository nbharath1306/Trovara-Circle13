# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trovara is an AI-powered Django web application. A user submits a research topic, and a background agent (running in a thread) searches the web, reads sources, summarizes content via Groq LLM, and generates a full research report. The frontend polls the API to show live progress.

## Tech Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Async tasks:** Python `threading.Thread` (no Celery, no broker — single web process)
- **Database:** Supabase (PostgreSQL) via `dj-database-url`
- **LLM:** Groq API (`llama-3.3-70b-versatile` model)
- **Web search:** DuckDuckGo (`duckduckgo-search` library, no API key)
- **HTML parsing:** BeautifulSoup4
- **Frontend:** Single vanilla HTML/JS page (no framework), polls API every 3s
- **Deployment:** Render.com (single web service)

> **Architecture note:** The original docs (`TROVARA_*.md`) describe a Celery + Redis architecture. We **deliberately removed** that for simplicity — see "Why threading instead of Celery" below. The TROVARA_*.md files are kept for reference but the actual code uses threading.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations agent
python manage.py migrate

# Check for errors
python manage.py check

# Start Django dev server (only one process needed)
python manage.py runserver

# Collect static files (before deploy)
python manage.py collectstatic --noinput

# Test API
curl -X POST http://localhost:8000/api/research/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence"}'

curl http://localhost:8000/api/research/1/
```

Only one process needed — the agent runs in a thread spawned by the view.

## Architecture

### Request Flow

1. User POSTs topic to `/api/research/` (DRF view)
2. Django creates a `ResearchTask` record (status: pending)
3. View spawns a daemon thread running `run_trovara(task_id)` and returns immediately with the task ID
4. Thread runs the 4-step pipeline in the same process:
   - **Search:** DuckDuckGo -> URLs + snippets
   - **Read:** requests + BeautifulSoup -> raw text per URL (max 3000 chars each)
   - **Summarize:** Groq LLM -> 3-5 sentence summary per source
   - **Generate:** Groq LLM -> full markdown research report
5. Status updates saved to DB at each step: `pending -> searching -> reading -> summarizing -> generating -> done` (or `failed`)
6. Frontend polls `GET /api/research/<id>/` every 3 seconds to show live progress

### Why threading instead of Celery

For a low-traffic demo / school project, Celery + Redis is overkill. Threading gives us:
- 2 free services instead of 4 (just Render web + Supabase)
- No external broker (no Upstash / CloudAMQP / Redis Cloud signup)
- Same UX — frontend still polls, status still updates live
- Trade-off: if Render restarts/sleeps the instance mid-task, the task gets stuck in an in-progress state. User just resubmits. Acceptable for this scale.

The thread is `daemon=True` so it doesn't block process shutdown. `connection.close()` is called in `finally` to release the thread's DB connection back to the pool.

### Key Code Locations

- `agent/tasks.py` — Plain Python function `run_trovara(task_id)` running the 4-step pipeline
- `agent/views.py` — `perform_create` spawns a `threading.Thread` calling `run_trovara`
- `agent/services/search.py` — DuckDuckGo search wrapper
- `agent/services/scraper.py` — URL fetcher + BeautifulSoup text extractor
- `agent/services/llm.py` — Groq API calls (lazy client init via `_get_client()`)
- `agent/models.py` — Single model `ResearchTask` storing topic, status, intermediate results, and final report as JSON/text fields
- `agent/serializers.py` — Two serializers: `ResearchTaskListSerializer` (lightweight) and `ResearchTaskDetailSerializer` (full)
- `agent/views.py` — `ListCreateAPIView` + `RetrieveDestroyAPIView`
- `templates/index.html` — Single-page dashboard with vanilla JS fetch-based polling

### URL Structure

- `/` — Frontend dashboard (TemplateView)
- `/admin/` — Django admin
- `/api/research/` — List all tasks (GET) or submit new topic (POST)
- `/api/research/<id>/` — Get task detail (GET) or delete (DELETE)

## Environment Variables

Required in `.env` (see `.env.example`):
- `DJANGO_SECRET_KEY` — Django secret key
- `DEBUG` — `True` for local, `False` for production
- `ALLOWED_HOSTS` — Comma-separated hostnames
- `DATABASE_URL` — Supabase PostgreSQL connection string (use Session pooler, port 5432)
- `GROQ_API_KEY` — From console.groq.com

## Key Implementation Details

- Groq model must be `llama-3.3-70b-versatile`
- Groq client is initialized lazily via `_get_client()` to avoid import-time failures
- DuckDuckGo import: `from duckduckgo_search import DDGS`
- Database parsed with `dj_database_url.config()`; `ssl_require` is auto-enabled only for `postgres*` URLs (so sqlite still works locally)
- Static files served via WhiteNoise (`CompressedManifestStaticFilesStorage`)
- WhiteNoise middleware goes second in MIDDLEWARE (after SecurityMiddleware)
- CORS handled by `django-cors-headers` (currently allows all origins)
- Scraper limits page text to 3000 chars to control LLM token usage
- Agent makes 6 Groq calls per task (5 source summaries + 1 report generation)
- Threads are spawned with `daemon=True` and explicitly close their DB connection in `finally`

## Deployment (Render.com)

Single Render service from the repo:
- **Web service:** `gunicorn trovara.wsgi --log-file -`
- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`

The `render.yaml` Blueprint provisions this automatically. Set `DATABASE_URL` and `GROQ_API_KEY` as secrets in the Render dashboard.

## Documentation Files

The `TROVARA_*.md` files in the repo root are the **original spec** (Celery + Redis). The actual implementation uses the simpler threading approach described above. When in doubt, trust the code over those docs.
