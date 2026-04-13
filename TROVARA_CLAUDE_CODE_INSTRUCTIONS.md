# Claude Code — Build Instructions

## How to Use This Documentation

When you open Claude Code, paste this prompt to get started:

---

**Starter Prompt for Claude Code:**

```
I want to build an Trovara Django project. 
I have complete documentation in the following files:

- README.md          — Project overview and stack
- ARCHITECTURE.md    — System design and data flow
- MODELS.md          — Database model (ResearchTask)
- API_SPEC.md        — REST API endpoints and serializers
- AGENT_LOGIC.md     — Celery agent task and service files
- ENV_VARIABLES.md   — Environment variable setup
- REQUIREMENTS.md    — Python dependencies
- PROJECT_STRUCTURE.md — Full folder layout
- SETUP.md           — Local development steps
- DEPLOYMENT.md      — Render deployment guide
- FRONTEND.md        — HTML dashboard template

Please build this project step by step:
1. Create the Django project and app structure
2. Set up settings.py, celery.py, and __init__.py
3. Create the ResearchTask model and migrations
4. Build the serializers and views
5. Set up the URL routing
6. Create agent/services/ folder with search.py, scraper.py, llm.py
7. Implement tasks.py (the Celery agent)
8. Create the frontend template (templates/index.html)
9. Create .env.example and .gitignore
10. Create Procfile for Render deployment

Use the free stack: Groq (not OpenAI), DuckDuckGo search (not SerpAPI), 
Supabase for PostgreSQL, Upstash for Redis, Render for deployment.
```

---

## Build Order (Follow This Exactly)

Claude Code should build files in this sequence to avoid import errors:

```
1.  requirements.txt
2.  .env.example
3.  .gitignore
4.  Procfile
5.  trovara/settings.py
6.  trovara/celery.py
7.  trovara/__init__.py
8.  trovara/urls.py
9.  trovara/wsgi.py
10. agent/__init__.py
11. agent/apps.py
12. agent/models.py
13. python manage.py makemigrations agent
14. python manage.py migrate
15. agent/serializers.py
16. agent/views.py
17. agent/urls.py
18. agent/admin.py
19. agent/services/__init__.py
20. agent/services/search.py
21. agent/services/scraper.py
22. agent/services/llm.py
23. agent/tasks.py
24. templates/index.html
```

## Important Decisions Claude Code Must Make

### Model name for Groq
```python
MODEL = "llama-3.3-70b-versatile"
```

### DuckDuckGo import
```python
from duckduckgo_search import DDGS
```

### Celery broker setting
```python
CELERY_BROKER_URL = os.getenv("REDIS_URL")
```

### Database parsing
```python
import dj_database_url
DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"), ssl_require=True)}
```

### Static files (WhiteNoise)
```python
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

## Testing Commands to Run After Build

```bash
# 1. Check for import errors
python manage.py check

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Start web server (Terminal 1)
python manage.py runserver

# 4. Start Celery worker (Terminal 2)
celery -A trovara worker --loglevel=info

# 5. Test API
curl -X POST http://localhost:8000/api/research/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence"}'
```

## What Success Looks Like

- `python manage.py check` returns no errors
- Django admin accessible at `/admin/`
- POST to `/api/research/` returns a task with `status: "pending"`
- Celery terminal shows the agent running steps
- GET to `/api/research/1/` eventually shows `status: "done"` with a report
- Frontend at `http://localhost:8000/` shows the dashboard and live updates
