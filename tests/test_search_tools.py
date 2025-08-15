import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.search_tools import search_web, fetch_page

def test_search_and_fetch():
    results = search_web("capital of france", max_results=3)
    assert isinstance(results, list) and len(results) > 0
    url = results[0].get("href") or results[0].get("url")
    page = fetch_page(url)
    assert "domain" in page and "text" in page
