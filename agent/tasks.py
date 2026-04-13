from django.db import connection
from .models import ResearchTask
from .services.search import search_web
from .services.scraper import fetch_page_text
from .services.llm import summarize_source, generate_report


def run_trovara(task_id: int):
    """
    Run the 4-step research pipeline for a given ResearchTask.
    Designed to be invoked in a background thread from the view.
    """
    try:
        task = ResearchTask.objects.get(id=task_id)

        # Step 1: Search
        task.status = "searching"
        task.save(update_fields=["status", "updated_at"])

        results = search_web(task.topic, num_results=5)
        task.search_results = results
        task.save(update_fields=["search_results", "updated_at"])

        # Step 2: Read Sources
        task.status = "reading"
        task.save(update_fields=["status", "updated_at"])

        sources = []
        for result in results:
            text = fetch_page_text(result["url"])
            if text:
                sources.append({"url": result["url"], "text": text})
        task.sources_text = sources
        task.save(update_fields=["sources_text", "updated_at"])

        # Step 3: Summarize Each Source
        task.status = "summarizing"
        task.save(update_fields=["status", "updated_at"])

        summaries = []
        for source in sources:
            summary = summarize_source(task.topic, source["text"])
            summaries.append({"url": source["url"], "summary": summary})
        task.summaries = summaries
        task.save(update_fields=["summaries", "updated_at"])

        # Step 4: Generate Final Report
        task.status = "generating"
        task.save(update_fields=["status", "updated_at"])

        report = generate_report(task.topic, summaries)
        task.report = report
        task.status = "done"
        task.save(update_fields=["report", "status", "updated_at"])

    except Exception as e:
        try:
            task.status = "failed"
            task.error = str(e)
            task.save(update_fields=["status", "error", "updated_at"])
        except Exception:
            pass
    finally:
        # Release this thread's DB connection back to the pool
        connection.close()
