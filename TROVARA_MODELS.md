# Database Models

## Overview

Only one primary model is needed: `ResearchTask`. It stores everything — the input topic, current status, intermediate results, and the final report — in a single table. This keeps the schema simple for a university project.

## ResearchTask Model

```python
# agent/models.py

from django.db import models

class ResearchTask(models.Model):

    STATUS_CHOICES = [
        ("pending",     "Pending"),
        ("searching",   "Searching Web"),
        ("reading",     "Reading Sources"),
        ("summarizing", "Summarizing Content"),
        ("generating",  "Generating Report"),
        ("done",        "Done"),
        ("failed",      "Failed"),
    ]

    # --- Core fields ---
    topic       = models.CharField(max_length=500)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # --- Agent output fields ---
    search_results = models.JSONField(default=list, blank=True)
    # Stores: [{ "title": "...", "url": "...", "snippet": "..." }, ...]

    sources_text = models.JSONField(default=list, blank=True)
    # Stores: [{ "url": "...", "text": "first 3000 chars of page content" }, ...]

    summaries = models.JSONField(default=list, blank=True)
    # Stores: [{ "url": "...", "summary": "3-5 sentence summary from Groq" }, ...]

    report = models.TextField(blank=True)
    # Final generated research report (markdown formatted)

    error = models.TextField(blank=True)
    # Error message if status == "failed"

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.status}] {self.topic[:60]}"
```

## Field Explanations

| Field | Type | Purpose |
|---|---|---|
| `topic` | CharField | The research topic submitted by the user |
| `status` | CharField | Current stage of the agent pipeline |
| `created_at` | DateTimeField | When the task was submitted |
| `updated_at` | DateTimeField | Last time any field was updated |
| `search_results` | JSONField | Raw results from DuckDuckGo search |
| `sources_text` | JSONField | Scraped text content from each URL |
| `summaries` | JSONField | Per-source summaries from Groq LLM |
| `report` | TextField | Final complete research report |
| `error` | TextField | Error message if the task fails |

## Status Flow

```
"pending"     → Task created in DB, waiting for Celery to pick it up
"searching"   → Celery is running DuckDuckGo search
"reading"     → Celery is fetching and parsing web pages
"summarizing" → Celery is sending each source to Groq for summary
"generating"  → Celery is generating the final report
"done"        → Report is complete and saved
"failed"      → An error occurred, stored in the error field
```

## Migration Commands

```bash
# Create migrations
python manage.py makemigrations agent

# Apply migrations to Supabase PostgreSQL
python manage.py migrate

# Verify tables created
python manage.py dbshell
# \dt   (lists tables in psql)
```

## Admin Registration

```python
# agent/admin.py

from django.contrib import admin
from .models import ResearchTask

@admin.register(ResearchTask)
class ResearchTaskAdmin(admin.ModelAdmin):
    list_display  = ["topic", "status", "created_at", "updated_at"]
    list_filter   = ["status"]
    search_fields = ["topic"]
    readonly_fields = ["created_at", "updated_at", "search_results",
                       "sources_text", "summaries", "report", "error"]
```

## Sample Database Record

```json
{
  "id": 1,
  "topic": "quantum computing basics",
  "status": "done",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:45Z",
  "search_results": [
    { "title": "What is Quantum Computing?", "url": "https://...", "snippet": "..." },
    { "title": "Quantum Computing Explained", "url": "https://...", "snippet": "..." }
  ],
  "sources_text": [
    { "url": "https://...", "text": "Quantum computing uses quantum bits..." }
  ],
  "summaries": [
    { "url": "https://...", "summary": "This source explains quantum bits (qubits)..." }
  ],
  "report": "# Research Report: Quantum Computing Basics\n\n## Introduction\n...",
  "error": ""
}
```
