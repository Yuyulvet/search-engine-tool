"""Performance tests for search-engine-tool."""

import time
import pytest

from src.indexer import build_index, tokenize
from src.search import find_pages


def test_index_build_performance():
    """Building an index for 100 pages should complete in under 1 second."""
    large_pages = [
        {"url": f"http://page{i}.com", "title": f"Page {i}", "text": "word " * 1000}
        for i in range(100)
    ]
    start = time.time()
    index = build_index(large_pages)
    elapsed = time.time() - start

    assert elapsed < 1.0, f"Index build took {elapsed:.2f}s, expected < 1.0s"
    assert index["_metadata"]["total_docs"] == 100


def test_search_performance():
    """Searching a large index should complete in under 100ms."""
    large_pages = [
        {"url": f"http://page{i}.com", "title": f"Page {i}", "text": f"hello world page{i}"}
        for i in range(1000)
    ]
    index = build_index(large_pages)

    start = time.time()
    for _ in range(100):
        results = find_pages(index, "hello world")
    elapsed = time.time() - start

    avg_time = elapsed / 100
    assert avg_time < 0.02, f"Avg search took {avg_time:.4f}s, expected < 20ms"


def test_tokenize_performance():
    """Tokenizing a large text should be efficient."""
    large_text = "hello world " * 10000

    start = time.time()
    tokens = tokenize(large_text)
    elapsed = time.time() - start

    assert len(tokens) == 20000
    assert elapsed < 0.5, f"Tokenize took {elapsed:.2f}s, expected < 0.5s"
