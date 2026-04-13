# Python Requirements

## requirements.txt

```
django==4.2.11
djangorestframework==3.14.0
celery==5.3.6
django-celery-results==2.5.1
redis==5.0.3
dj-database-url==2.1.0
psycopg2-binary==2.9.9
python-dotenv==1.0.1
groq==0.9.0
requests==2.31.0
beautifulsoup4==4.12.3
duckduckgo-search==5.3.1
django-cors-headers==4.3.1
gunicorn==21.2.0
whitenoise==6.6.0
```

## What Each Package Does

| Package | Purpose |
|---|---|
| `django` | Core web framework — routing, ORM, admin, templates |
| `djangorestframework` | Adds serializers, API views, and JSON responses to Django |
| `celery` | Distributed task queue — runs the AI agent in the background |
| `django-celery-results` | Saves Celery task results to PostgreSQL (Django DB backend) |
| `redis` | Python client for Redis — Celery uses this to talk to Upstash |
| `dj-database-url` | Parses `DATABASE_URL` string into Django `DATABASES` config |
| `psycopg2-binary` | PostgreSQL adapter for Python — Django needs this to talk to Supabase |
| `python-dotenv` | Loads `.env` file into environment variables at startup |
| `groq` | Official Groq Python SDK — makes calls to Llama 3.3 model |
| `requests` | HTTP library — fetches web page content from URLs |
| `beautifulsoup4` | HTML parser — extracts clean readable text from web pages |
| `duckduckgo-search` | DuckDuckGo search library — finds URLs for a given topic (no API key) |
| `django-cors-headers` | Allows browser to call the API from a different origin |
| `gunicorn` | Production WSGI server — Render uses this to serve Django |
| `whitenoise` | Serves Django static files without a separate web server |

## Installation

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install all dependencies
pip install -r requirements.txt
```

## Version Notes

- Python 3.11+ recommended
- Django 4.2 is an LTS (Long Term Support) release — stable choice for a project
- `psycopg2-binary` is the easy install version — fine for development and small deployments
- `groq` SDK version 0.9.0+ supports the llama-3.3-70b-versatile model
