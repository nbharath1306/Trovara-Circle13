# Local Development Setup

## Prerequisites

Install these on your machine before starting:

- Python 3.11+
- PostgreSQL (or just use Supabase remote even for local dev)
- Redis (or use Upstash remote even for local dev)
- Git

## Step-by-Step Setup

### 1. Create the Django Project

```bash
# Create project folder
mkdir trovara
cd trovara

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install Django first
pip install django djangorestframework

# Create Django project
django-admin startproject trovara .

# Create the agent app
python manage.py startapp agent
```

### 2. Install All Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and fill in your keys:
# - DJANGO_SECRET_KEY (generate one)
# - DATABASE_URL (from Supabase)
# - REDIS_URL (from Upstash)
# - GROQ_API_KEY (from console.groq.com)
```

### 4. Set Up Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Click "New Project"
3. Give it a name: `trovara-db`
4. Set a database password (save it!)
5. Go to **Settings → Database → Connection string → URI**
6. Copy the URI and paste it as `DATABASE_URL` in your `.env`
7. Change `[YOUR-PASSWORD]` in the URI to your actual password

### 5. Set Up Upstash Redis

1. Go to [upstash.com](https://upstash.com) and create a free account
2. Click "Create Database"
3. Name it `trovara-redis`, choose a region
4. Copy the **Redis URL** (starts with `rediss://`)
5. Paste it as `REDIS_URL` in your `.env`

### 6. Get Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up / log in
3. Go to **API Keys → Create API Key**
4. Copy and paste it as `GROQ_API_KEY` in your `.env`

### 7. Run Database Migrations

```bash
python manage.py makemigrations agent
python manage.py migrate
```

### 8. Create Admin User

```bash
python manage.py createsuperuser
# Follow prompts to set username, email, password
```

### 9. Run the Development Server

You need TWO terminal windows running simultaneously:

**Terminal 1 — Django web server:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 — Celery worker:**
```bash
source venv/bin/activate
celery -A trovara worker --loglevel=info
```

### 10. Test the App

Open your browser and go to:
- **Frontend dashboard:** `http://localhost:8000/`
- **Django admin:** `http://localhost:8000/admin/`
- **API directly:** `http://localhost:8000/api/research/`

### 11. Test the API with curl

```bash
# Submit a research topic
curl -X POST http://localhost:8000/api/research/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "machine learning basics"}'

# Check status (replace 1 with your task id)
curl http://localhost:8000/api/research/1/
```

## Common Issues

| Problem | Solution |
|---|---|
| `django.db.OperationalError` | Check `DATABASE_URL` in `.env` is correct |
| Celery not picking up tasks | Make sure `REDIS_URL` is correct and Celery terminal is running |
| `groq.AuthenticationError` | Check `GROQ_API_KEY` is set and valid |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in your virtual environment |
| Port 8000 already in use | `python manage.py runserver 8001` |

## Static Files (for Production)

```bash
# Collect static files before deploying
python manage.py collectstatic --noinput
```
