from __future__ import annotations
import requests
import datetime as dt
from ddgs import DDGS
from bs4 import BeautifulSoup

# ✅ Absolute imports instead of relative
from src.utils import domain_from_url
from config.settings import MAX_SEARCH_RESULTS, REQUEST_TIMEOUT, USER_AGENT

# Headers for web requests
headers = {"User-Agent": USER_AGENT}


def search_web(query: str, max_results: int | None = None):
    """
    Search the web using DuckDuckGo (via ddgs) and return a list of search results.
    """
    limit = max_results or MAX_SEARCH_RESULTS
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=limit, safesearch="moderate", region="in-en"))


def fetch_page(url: str) -> dict:
    """
    Fetch and parse a web page. Returns dict with keys:
    url, domain, title, text, published, and optionally error.
    """
    try:
        res = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else ""
        text = " ".join([p.get_text(" ", strip=True) for p in soup.find_all("p")])[:2000]

        # Naive date extraction
        date_meta = soup.find("meta", {"property": "article:published_time"}) or soup.find("meta", {"name": "date"})
        published = None
        if date_meta and date_meta.get("content"):
            try:
                published = dt.datetime.fromisoformat(
                    date_meta["content"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
            except Exception:
                published = None

        return {
            "url": url,
            "domain": domain_from_url(url),
            "title": title,
            "text": text,
            "published": published
        }

    except Exception as e:
        return {
            "url": url,
            "domain": domain_from_url(url),
            "title": "",
            "text": "",
            "published": None,
            "error": str(e)
        }
