# Environment Variables

## .env File (Local Development)

Create a file named `.env` in the root of your project (same level as `manage.py`).
**Never commit this file to Git.**

```env
# ── Django ──────────────────────────────────────────────────────
DJANGO_SECRET_KEY=your-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ── Database (Supabase PostgreSQL) ──────────────────────────────
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# ── Redis (Upstash) ─────────────────────────────────────────────
REDIS_URL=rediss://default:[YOUR-PASSWORD]@[YOUR-ENDPOINT].upstash.io:6379

# ── Groq LLM ────────────────────────────────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Variable Reference

| Variable | Required | Where to Get It |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | Yes | `True` for local, `False` for production |
| `ALLOWED_HOSTS` | Yes | `localhost,127.0.0.1` locally; your Render domain in production |
| `DATABASE_URL` | Yes | Supabase → Project → Settings → Database → Connection string |
| `REDIS_URL` | Yes | Upstash → Your database → REST URL (use the `rediss://` TLS URL) |
| `GROQ_API_KEY` | Yes | console.groq.com → API Keys → Create new key |

## Django Settings — How to Use Them

```python
# trovara/settings.py

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY   = os.getenv("DJANGO_SECRET_KEY")
DEBUG        = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

# Database — parses DATABASE_URL automatically
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

# Celery — Redis broker
CELERY_BROKER_URL        = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND    = "django-db"
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
```

## .gitignore Entry

Make sure your `.gitignore` includes:

```
.env
*.pyc
__pycache__/
db.sqlite3
```

## Production Environment Variables on Render

When deploying to Render, add each variable in:
**Render Dashboard → Your Service → Environment → Add Environment Variable**

Set `DEBUG=False` and `ALLOWED_HOSTS=your-app-name.onrender.com` in production.
