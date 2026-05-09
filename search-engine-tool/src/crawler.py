"""
Web crawler module for search-engine-tool.

Crawls https://quotes.toscrape.com/ and extracts page text content.
Respects a politeness window of at least 6 seconds between requests.
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


BASE_URL = "https://quotes.toscrape.com"
POLITENESS_DELAY = 6  # seconds between successive requests


def fetch_page(url: str) -> str | None:
    """
    Fetch the HTML content of a single page.

    Args:
        url: The URL to fetch.

    Returns:
        The raw HTML text, or None if the request fails.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_page(html: str, page_url: str) -> dict:
    """
    Parse HTML and extract useful text content and links.

    Args:
        html: Raw HTML string.
        page_url: The URL of the current page (for resolving relative links).

    Returns:
        A dictionary with:
            - 'url': the page URL
            - 'title': page title text
            - 'text': extracted visible text content
            - 'links': list of absolute internal URLs found on the page
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    text = soup.get_text(separator=" ", strip=True)

    links = set()
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        full_url = urljoin(page_url, href)
        # Stay within the target domain
        if urlparse(full_url).netloc == urlparse(BASE_URL).netloc:
            links.add(full_url)

    return {
        "url": page_url,
        "title": title,
        "text": text,
        "links": list(links),
    }


def crawl_website(start_url: str = BASE_URL, max_pages: int = 100) -> list[dict]:
    """
    Crawl the target website starting from start_url.

    Respects POLITENESS_DELAY seconds between requests.
    Limits crawling to max_pages to avoid excessive requests.
    Returns a list of page data dictionaries.
    """
    visited = set()
    pages = []
    to_visit = [start_url]

    while to_visit and len(pages) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        html = fetch_page(url)
        if html is None:
            continue

        page_data = parse_page(html, url)
        pages.append(page_data)
        print(f"  Crawled [{len(pages)}/{max_pages}]: {url}")

        # Discover new internal links (prioritise pagination pages)
        for link in page_data["links"]:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

        # Politeness window
        if to_visit and len(pages) < max_pages:
            time.sleep(POLITENESS_DELAY)

    return pages


if __name__ == "__main__":
    results = crawl_website()
    print(f"Crawled {len(results)} pages.")
    for p in results:
        print(f"  - {p['url']} | {p['title']}")
