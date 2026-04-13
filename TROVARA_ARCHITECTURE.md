# System Architecture

## High-Level Data Flow

```
User (Browser)
    |
    | POST /api/research/   { "topic": "quantum computing" }
    v
Django REST API (DRF View)
    |
    | 1. Creates ResearchTask in Supabase (status: pending)
    | 2. Enqueues Celery task with task_id
    v
Upstash Redis (Message Broker)
    |
    | Celery worker picks up the job
    v
Celery Worker — Agent (tasks.py)
    |
    |-- Step 1: Search web via DuckDuckGo → get URLs + snippets
    |-- Step 2: Fetch each URL via requests + parse with BeautifulSoup
    |-- Step 3: Send text to Groq API → get per-source summary
    |-- Step 4: Send all summaries to Groq API → generate final report
    |
    | Save results at each step to Supabase
    v
Supabase PostgreSQL
    |
    | Frontend polls GET /api/research/<id>/
    v
User sees completed report
```

## Component Breakdown

### Django + DRF (Web Layer)
- Receives user requests
- Creates and returns ResearchTask objects
- Exposes REST endpoints for submitting topics and polling status
- Serves the frontend HTML dashboard

### Celery (Agent Layer)
- Runs as a separate process from Django
- Picks up tasks from Redis queue
- Executes the full multi-step research pipeline
- Updates task status in PostgreSQL at each step

### Upstash Redis (Broker)
- Acts as the message queue between Django and Celery
- Django enqueues a task → Redis holds it → Celery consumes it
- Does NOT store final results (those go to PostgreSQL)

### Supabase PostgreSQL (Storage Layer)
- Stores all ResearchTask records
- Tracks status: pending → searching → reading → summarizing → done
- Stores search results, per-source summaries, and final report as JSON/text fields

### Groq API (LLM Layer)
- Called twice per research task:
  1. Once per source URL — generate a 3-5 sentence summary
  2. Once at the end — generate the full structured report from all summaries
- Model: llama-3.3-70b-versatile (free tier)

### DuckDuckGo Search (Search Layer)
- Python library, no API key required
- Returns top N results (title, URL, snippet) for a given query
- Agent fetches 5 URLs by default (configurable)

## Status Lifecycle

```
pending → searching → reading → summarizing → generating → done
                                                          → failed
```

Each status change is saved to PostgreSQL immediately so the frontend can show live progress.

## Concurrency Model

- Django handles HTTP requests (synchronous, but fast — just creates DB records and enqueues)
- Celery handles the slow AI work asynchronously
- Multiple users can submit topics simultaneously — each gets their own Celery task
- Celery worker processes tasks one at a time by default (can be scaled with concurrency setting)

## Frontend Architecture

- Single HTML page served by Django (no separate frontend framework needed)
- Uses vanilla JavaScript + fetch() to poll the API every 3 seconds
- Displays live status updates and final report when ready
- No React/Vue needed — keeps the project focused on Django
