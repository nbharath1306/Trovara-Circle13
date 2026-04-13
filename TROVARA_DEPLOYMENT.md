# Deployment Guide — Render + Supabase + Upstash

## Overview

You will deploy two services on Render:
1. **Web Service** — runs `gunicorn` (serves Django + DRF)
2. **Background Worker** — runs `celery` (the AI agent)

Both connect to the same Supabase database and Upstash Redis.

---

## Step 1 — Prepare Your Code for Production

### Add Procfile (root of project)

```
web: gunicorn trovara.wsgi --log-file -
worker: celery -A trovara worker --loglevel=info
```

### Add/update requirements.txt

Make sure `gunicorn` and `whitenoise` are included (see REQUIREMENTS.md).

### Update settings.py for production

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

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",    # add this
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_celery_results",
    "agent",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # add this (second position)
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

CELERY_BROKER_URL      = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND  = "django-db"
CELERY_ACCEPT_CONTENT  = ["json"]
CELERY_TASK_SERIALIZER = "json"

STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "trovara.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

### Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — Trovara project"
git remote add origin https://github.com/YOUR_USERNAME/trovara.git
git push -u origin main
```

---

## Step 2 — Deploy Web Service on Render

1. Go to [render.com](https://render.com) and sign up with GitHub
2. Click **New → Web Service**
3. Connect your GitHub repository
4. Configure the service:

| Setting | Value |
|---|---|
| Name | `trovara-web` |
| Region | Singapore (closest to India) |
| Branch | `main` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| Start Command | `gunicorn trovara.wsgi --log-file -` |
| Instance Type | Free |

5. Add environment variables (click "Add Environment Variable" for each):

```
DJANGO_SECRET_KEY    = (generate a new one)
DEBUG                = False
ALLOWED_HOSTS        = trovara-web.onrender.com
DATABASE_URL         = (your Supabase connection string)
REDIS_URL            = (your Upstash Redis URL)
GROQ_API_KEY         = (your Groq API key)
```

6. Click **Create Web Service**
7. Wait 3-5 minutes for the first deploy

---

## Step 3 — Deploy Celery Worker on Render

1. Click **New → Background Worker**
2. Connect the same GitHub repository
3. Configure:

| Setting | Value |
|---|---|
| Name | `trovara-worker` |
| Branch | `main` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `celery -A trovara worker --loglevel=info` |
| Instance Type | Free |

4. Add the same environment variables as the web service:

```
DJANGO_SECRET_KEY    = (same as web service)
DEBUG                = False
DATABASE_URL         = (your Supabase connection string)
REDIS_URL            = (your Upstash Redis URL)
GROQ_API_KEY         = (your Groq API key)
```

5. Click **Create Background Worker**

---

## Step 4 — Verify Deployment

1. Open your web service URL: `https://trovara-web.onrender.com`
2. Submit a test research topic
3. Check Render logs for both services:
   - Web service logs should show incoming requests
   - Worker logs should show Celery picking up and running the task

---

## Important Notes

### Free Tier Limitations on Render
- Free web services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Free background workers have limited compute hours per month
- For a university demo, this is perfectly fine

### Upstash Redis — Use TLS URL
Make sure your `REDIS_URL` starts with `rediss://` (with double `s`) not `redis://`. Upstash requires TLS connections.

### Supabase Connection Pooling
For production, use the **connection pooler** URL from Supabase (port 6543) instead of the direct connection (port 5432). This handles multiple concurrent connections better.

---

## Deployment Checklist

- [ ] `Procfile` added to root
- [ ] `gunicorn` and `whitenoise` in `requirements.txt`
- [ ] `DEBUG=False` in production environment
- [ ] `ALLOWED_HOSTS` set to Render domain
- [ ] `STATIC_ROOT` and WhiteNoise configured
- [ ] Code pushed to GitHub
- [ ] Web service deployed on Render
- [ ] Celery worker deployed on Render
- [ ] All 4 environment variables set on both services
- [ ] Test task submitted and completed successfully
