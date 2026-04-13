# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trovara is an AI-powered Django web application. A user submits a research topic, and an autonomous Celery agent searches the web, reads sources, summarizes content via Groq LLM, and generates a full research report in the background.

## Tech Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Async tasks:** Celery with Upstash Redis as broker
- **Database:** Supabase (PostgreSQL) via `dj-database-url`
- **LLM:** Groq API (`llama-3.3-70b-versatile` model)
- **Web search:** DuckDuckGo (`duckduckgo-search` library, no API key)
- **HTML parsing:** BeautifulSoup4
- **Frontend:** Single vanilla HTML/JS page (no framework), polls API every 3s
- **Deployment:** Render.com (web service + background worker)

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations agent
python manage.py migrate

# Check for errors
python manage.py check

# Start Django dev server (Terminal 1)
python manage.py runserver

# Start Celery worker (Terminal 2)
celery -A trovara worker --loglevel=info

# Collect static files (before deploy)
python manage.py collectstatic --noinput

# Test API
curl -X POST http://localhost:8000/api/research/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence"}'

curl http://localhost:8000/api/research/1/
```

Both the Django server and Celery worker must be running simultaneously for the app to function.

## Architecture

### Request Flow

1. User POSTs topic to `/api/research/` (DRF view)
2. Django creates a `ResearchTask` record (status: pending), enqueues Celery task
3. Celery worker picks up the job from Redis and runs a 4-step pipeline:
   - **Search:** DuckDuckGo -> URLs + snippets
   - **Read:** requests + BeautifulSoup -> raw text per URL (max 3000 chars each)
   - **Summarize:** Groq LLM -> 3-5 sentence summary per source
   - **Generate:** Groq LLM -> full markdown research report
4. Status updates saved to DB at each step: `pending -> searching -> reading -> summarizing -> generating -> done` (or `failed`)
5. Frontend polls `GET /api/research/<id>/` every 3 seconds to show live progress

### Key Code Locations

- `trovara/celery.py` — Celery app config; imported in `trovara/__init__.py` to auto-load
- `agent/tasks.py` — The core agent: single Celery task `run_trovara` running the 4-step pipeline
- `agent/services/search.py` — DuckDuckGo search wrapper
- `agent/services/scraper.py` — URL fetcher + BeautifulSoup text extractor
- `agent/services/llm.py` — Groq API calls (summarize per source + generate report)
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
- `DATABASE_URL` — Supabase PostgreSQL connection string
- `REDIS_URL` — Upstash Redis URL (must use `rediss://` TLS)
- `GROQ_API_KEY` — From console.groq.com

## Build Order

When building from scratch, create files in this order to avoid import errors:

1. `requirements.txt`, `.env.example`, `.gitignore`, `Procfile`
2. `trovara/settings.py`, `trovara/celery.py`, `trovara/__init__.py`, `trovara/urls.py`, `trovara/wsgi.py`
3. `agent/` app files: models -> makemigrations -> migrate -> serializers -> views -> urls -> admin
4. `agent/services/`: `search.py`, `scraper.py`, `llm.py`
5. `agent/tasks.py`
6. `templates/index.html`

## Key Implementation Details

- Groq model must be `llama-3.3-70b-versatile`
- DuckDuckGo import: `from duckduckgo_search import DDGS`
- Celery broker uses `REDIS_URL` env var; result backend is `django-db`
- Database parsed with `dj_database_url.config()` with `ssl_require=True`
- Static files served via WhiteNoise (`CompressedManifestStaticFilesStorage`)
- WhiteNoise middleware goes second in MIDDLEWARE (after SecurityMiddleware)
- CORS handled by `django-cors-headers` (currently allows all origins)
- Scraper limits page text to 3000 chars to control LLM token usage
- Agent makes 6 Groq calls per task (5 source summaries + 1 report generation)

## Deployment (Render.com)

Two Render services from the same repo:
- **Web service:** `gunicorn trovara.wsgi --log-file -`
- **Background worker:** `celery -A trovara worker --loglevel=info`

Build command for web: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`

## Documentation Files

The `TROVARA_*.md` files in the repo root contain detailed specifications for every component (architecture, models, API, agent logic, frontend, deployment, env vars, setup). Consult these when building or modifying specific parts.
