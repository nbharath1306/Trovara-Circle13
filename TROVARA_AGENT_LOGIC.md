# Agent Logic — tasks.py

## Overview

The Celery task `run_trovara` is the brain of the project. It receives a `task_id`, loads the ResearchTask from the database, and runs a 4-step pipeline. At each step it updates the task status so the frontend can show live progress.

## The 4 Steps

```
Step 1: SEARCH    → DuckDuckGo → list of URLs + snippets
Step 2: READ      → requests + BeautifulSoup → raw text per URL
Step 3: SUMMARIZE → Groq LLM → 3-5 sentence summary per source
Step 4: GENERATE  → Groq LLM → full structured research report
```

---

## Main Task File

```python
# agent/tasks.py

from celery import shared_task
from .models import ResearchTask
from .services.search import search_web
from .services.scraper import fetch_page_text
from .services.llm import summarize_source, generate_report

@shared_task
def run_trovara(task_id: int):
    try:
        task = ResearchTask.objects.get(id=task_id)

        # ── Step 1: Search ──────────────────────────────────────────
        task.status = "searching"
        task.save(update_fields=["status", "updated_at"])

        results = search_web(task.topic, num_results=5)
        task.search_results = results
        task.save(update_fields=["search_results", "updated_at"])

        # ── Step 2: Read Sources ────────────────────────────────────
        task.status = "reading"
        task.save(update_fields=["status", "updated_at"])

        sources = []
        for result in results:
            text = fetch_page_text(result["url"])
            if text:
                sources.append({"url": result["url"], "text": text})
        task.sources_text = sources
        task.save(update_fields=["sources_text", "updated_at"])

        # ── Step 3: Summarize Each Source ───────────────────────────
        task.status = "summarizing"
        task.save(update_fields=["status", "updated_at"])

        summaries = []
        for source in sources:
            summary = summarize_source(task.topic, source["text"])
            summaries.append({"url": source["url"], "summary": summary})
        task.summaries = summaries
        task.save(update_fields=["summaries", "updated_at"])

        # ── Step 4: Generate Final Report ───────────────────────────
        task.status = "generating"
        task.save(update_fields=["status", "updated_at"])

        report = generate_report(task.topic, summaries)
        task.report = report
        task.status = "done"
        task.save(update_fields=["report", "status", "updated_at"])

    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.save(update_fields=["status", "error", "updated_at"])
```

---

## Service: Search (DuckDuckGo)

```python
# agent/services/search.py

from duckduckgo_search import DDGS

def search_web(query: str, num_results: int = 5) -> list[dict]:
    """
    Search DuckDuckGo and return top N results.
    Returns: [{ "title": str, "url": str, "snippet": str }]
    """
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=num_results):
            results.append({
                "title":   r.get("title", ""),
                "url":     r.get("href", ""),
                "snippet": r.get("body", ""),
            })
    return results
```

---

## Service: Scraper (BeautifulSoup)

```python
# agent/services/scraper.py

import requests
from bs4 import BeautifulSoup

MAX_CHARS = 3000  # Limit text sent to LLM to control token usage

def fetch_page_text(url: str) -> str:
    """
    Fetch a URL and return cleaned readable text.
    Returns empty string on any error.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Trovara Bot)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts, styles, nav, footer — keep only content
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        # Collapse multiple spaces/newlines
        text = " ".join(text.split())

        return text[:MAX_CHARS]

    except Exception:
        return ""
```

---

## Service: LLM (Groq)

```python
# agent/services/llm.py

import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"

def summarize_source(topic: str, text: str) -> str:
    """
    Ask Groq to summarize one source in the context of the research topic.
    Returns a 3-5 sentence summary string.
    """
    prompt = f"""You are a research assistant. 
Given the following web page content about "{topic}", write a concise 3-5 sentence summary 
of the most relevant and important information.

Web page content:
{text}

Summary:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate_report(topic: str, summaries: list[dict]) -> str:
    """
    Ask Groq to generate a full structured research report from all source summaries.
    Returns a markdown-formatted report string.
    """
    summaries_text = "\n\n".join(
        f"Source {i+1} ({s['url']}):\n{s['summary']}"
        for i, s in enumerate(summaries)
    )

    prompt = f"""You are an expert research analyst.
Based on the following source summaries about "{topic}", write a comprehensive, 
well-structured research report in Markdown format.

Include:
- An introduction explaining the topic
- Key findings and insights from the sources
- A conclusion summarizing the main takeaways

Source summaries:
{summaries_text}

Research Report (in Markdown):"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()
```

---

## Error Handling Strategy

| Error Type | What Happens |
|---|---|
| DuckDuckGo returns no results | `search_results` is empty list, agent still continues |
| URL fetch fails (timeout, 404) | `fetch_page_text` returns empty string, that URL is skipped |
| Groq API error (rate limit, etc.) | Exception caught in main task, status set to "failed", error saved |
| Database connection error | Exception propagates, Celery retries (or marks failed) |

## Groq Rate Limits (Free Tier)

- 30 requests per minute
- 14,400 requests per day
- With 5 sources + 1 report = 6 Groq calls per research task
- Free tier supports ~2,400 research tasks per day — more than enough
