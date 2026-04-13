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
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })
    return results
