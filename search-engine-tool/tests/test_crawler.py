"""Tests for the crawler module."""

import pytest
from unittest.mock import patch, MagicMock
from src.crawler import fetch_page, parse_page, crawl_website


# ------------------------------------------------------------------
# Unit tests (fast, no network)
# ------------------------------------------------------------------

def test_fetch_page_success_mocked():
    """Test fetch_page with a mocked successful response."""
    mock_response = MagicMock()
    mock_response.text = "<html><title>Quotes to Scrape</title></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("src.crawler.requests.get", return_value=mock_response):
        html = fetch_page("https://quotes.toscrape.com/")
        assert html is not None
        assert "Quotes to Scrape" in html


def test_fetch_page_failure_mocked():
    """Test fetch_page with a mocked failed response."""
    from requests import RequestException

    with patch("src.crawler.requests.get", side_effect=RequestException("Network error")):
        result = fetch_page("https://quotes.toscrape.com/")
        assert result is None


def test_parse_page_extracts_title():
    """Test that parse_page extracts the page title."""
    sample_html = """
    <html><head><title>Test Page</title></head>
    <body><p>Hello world</p><a href="/page/2/">Next</a></body></html>
    """
    result = parse_page(sample_html, "https://quotes.toscrape.com/")
    assert result["title"] == "Test Page"
    assert "Hello world" in result["text"]


def test_parse_page_extracts_links():
    """Test that parse_page resolves relative links correctly."""
    sample_html = """
    <html><head><title>Links</title></head>
    <body>
        <a href="/page/2/">Next</a>
        <a href="https://quotes.toscrape.com/page/3/">Direct</a>
        <a href="https://example.com/">External</a>
    </body></html>
    """
    result = parse_page(sample_html, "https://quotes.toscrape.com/")
    assert "https://quotes.toscrape.com/page/2/" in result["links"]
    assert "https://quotes.toscrape.com/page/3/" in result["links"]
    # External link should be excluded
    assert "https://example.com/" not in result["links"]


@pytest.mark.slow
def test_fetch_page_success_live():
    """Live test: fetch the real homepage (requires network)."""
    html = fetch_page("https://quotes.toscrape.com/")
    assert html is not None
    assert "Quotes to Scrape" in html


@pytest.mark.slow
def test_fetch_page_failure_live():
    """Live test: 404 response returns None."""
    result = fetch_page("https://quotes.toscrape.com/nonexistent-page-12345/")
    assert result is None


def test_parse_page_removes_scripts():
    """Script and style content should not appear in extracted text."""
    sample_html = """
    <html><head><title>Test</title></head>
    <body>
        <script>alert('hello');</script>
        <style>.red { color: red; }</style>
        <p>Real content</p>
    </body></html>
    """
    result = parse_page(sample_html, "https://quotes.toscrape.com/")
    assert "Real content" in result["text"]
    assert "alert" not in result["text"]
    assert "color: red" not in result["text"]


def test_parse_page_no_title():
    """Pages without a title should have an empty title field."""
    sample_html = "<html><body><p>No title here</p></body></html>"
    result = parse_page(sample_html, "https://quotes.toscrape.com/")
    assert result["title"] == ""


@pytest.mark.parametrize("max_pages,expected_max", [
    (1, 1),
    (3, 3),
])
def test_crawl_website_respects_max_pages(max_pages, expected_max):
    """Crawler should stop after max_pages."""
    pages = crawl_website(max_pages=max_pages)
    assert len(pages) <= expected_max


@pytest.mark.slow
def test_crawl_website_returns_pages():
    """Integration test: crawl the real site and verify we get pages."""
    pages = crawl_website()
    assert len(pages) > 0
    # The site has at least a homepage and several paginated pages
    urls = [p["url"] for p in pages]
    assert "https://quotes.toscrape.com/" in urls
