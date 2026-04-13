# Trovara — Project Documentation

## Overview

An AI-powered Django web application where a user submits a research topic and an autonomous agent searches the web, reads sources, summarizes content, and generates a full research report — all running in the background via Celery.

## Free Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Web framework | Django 4.2 + DRF | REST API, ORM, admin panel |
| Background tasks | Celery | Autonomous agent runner |
| Message broker | Upstash Redis | Task queue between Django and Celery |
| Database | Supabase (PostgreSQL) | Stores tasks, results, reports |
| LLM | Groq API (Llama 3.3 70B) | Summarization + report generation |
| Web search | DuckDuckGo Search (Python lib) | Find relevant URLs for a topic |
| HTML parsing | BeautifulSoup4 | Extract clean text from web pages |
| Deployment | Render.com | Hosts Django web service + Celery worker |
| Secrets | python-dotenv | Manages API keys via .env file |

## Documents in This Repo

| File | Purpose |
|---|---|
| `README.md` | This file — project overview |
| `ARCHITECTURE.md` | System design, data flow, component diagram |
| `MODELS.md` | Database schema and Django models |
| `API_SPEC.md` | All REST API endpoints with request/response examples |
| `AGENT_LOGIC.md` | Step-by-step agent behavior in tasks.py |
| `SETUP.md` | Local development setup instructions |
| `DEPLOYMENT.md` | Render + Supabase + Upstash deployment guide |
| `ENV_VARIABLES.md` | All required environment variables |
| `REQUIREMENTS.md` | Python dependencies with explanations |
| `PROJECT_STRUCTURE.md` | Full folder and file structure |

## Quick Start for Claude Code

When using Claude Code to build this project, work in this order:

1. Set up Django project and install dependencies (`REQUIREMENTS.md`)
2. Configure settings and environment variables (`ENV_VARIABLES.md`)
3. Create database models (`MODELS.md`)
4. Build REST API views and serializers (`API_SPEC.md`)
5. Implement the agent task (`AGENT_LOGIC.md`)
6. Build the frontend HTML dashboard
7. Test locally (`SETUP.md`)
8. Deploy (`DEPLOYMENT.md`)

## Domain

**AI + Web** — Autonomous agent with multi-step reasoning, background task processing, external API integration, and a Django REST API backend.

## Assignment Alignment

| Requirement | How This Project Meets It |
|---|---|
| Extract key system goals | Topic → Search → Read → Summarize → Report |
| Build scalable Django solution | Celery handles async tasks — multiple users simultaneously |
| Implement APIs and core logic | DRF REST endpoints + multi-step agent in tasks.py |
| Domain: AI / Web | Core of project is an LLM-powered autonomous agent |
| Tools: Django, DRF, PostgreSQL, APIs, ML/AI | All used — Groq replaces OpenAI, Supabase provides PostgreSQL |
