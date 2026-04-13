import requests
from bs4 import BeautifulSoup

MAX_CHARS = 3000


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

        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = " ".join(text.split())

        return text[:MAX_CHARS]

    except Exception:
        return ""
