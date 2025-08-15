# tests/test_search_tools.py
import pytest
from src.search_tools import search_web, fetch_page

def test_search_web_returns_results():
    results = search_web("capital of france", max_results=3)
    assert isinstance(results, list), "search_web should return a list"
    assert len(results) > 0, "Expected at least one search result"
    assert "title" in results[0] or "body" in results[0], "Each result should have content fields"

def test_fetch_page_returns_expected_keys():
    results = search_web("capital of france", max_results=1)
    url = results[0].get("href") or results[0].get("url")
    page_data = fetch_page(url)
    assert isinstance(page_data, dict), "fetch_page should return a dict"
    for key in ["url", "domain", "title", "text", "published"]:
        assert key in page_data, f"Expected '{key}' in page data"
