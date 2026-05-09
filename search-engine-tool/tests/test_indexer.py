"""Tests for the indexer module."""

import json
import os
import tempfile

import pytest

from src.indexer import (
    tokenize,
    build_index,
    save_index,
    load_index,
    get_metadata,
    get_document_frequency,
)


@pytest.mark.parametrize("text,expected", [
    ("Hello World!", ["hello", "world"]),
    ("UPPER lower MiXeD", ["upper", "lower", "mixed"]),
    ("", []),
    ("...!!!", []),
])
def test_tokenize_cases(text, expected):
    """Tokenize should handle various input cases."""
    assert tokenize(text) == expected


def test_tokenize_handles_apostrophes():
    """Tokenize should keep apostrophes inside words."""
    assert tokenize("Don't stop") == ["don't", "stop"]


def test_tokenize_special_characters():
    """Tokenize should handle special characters gracefully."""
    assert tokenize("hello@world#foo") == ["hello", "world", "foo"]
    assert tokenize("123 abc!!!") == ["123", "abc"]


def test_build_index_basic():
    """Build an index from two simple pages."""
    pages = [
        {"url": "http://a.com", "title": "A", "text": "hello world hello"},
        {"url": "http://b.com", "title": "B", "text": "hello foo"},
    ]
    index = build_index(pages)

    assert "_metadata" in index
    assert index["_metadata"]["total_docs"] == 2

    assert "hello" in index
    assert set(index["hello"].keys()) == {"http://a.com", "http://b.com"}

    # Page A has hello twice, 3 total words
    assert index["hello"]["http://a.com"]["frequency"] == 2
    assert index["hello"]["http://a.com"]["positions"] == [0, 2]
    assert index["hello"]["http://a.com"]["doc_length"] == 3

    # Page B has hello once, 2 total words
    assert index["hello"]["http://b.com"]["frequency"] == 1
    assert index["hello"]["http://b.com"]["positions"] == [0]
    assert index["hello"]["http://b.com"]["doc_length"] == 2

    # world only in A
    assert "world" in index
    assert "http://a.com" in index["world"]
    assert "http://b.com" not in index["world"]


def test_build_index_case_insensitive():
    """The index should treat 'Good' and 'good' as the same word."""
    pages = [
        {"url": "http://x.com", "title": "X", "text": "Good good GOOD"},
    ]
    index = build_index(pages)
    assert "good" in index
    assert "good" not in index or "Good" not in index
    assert index["good"]["http://x.com"]["frequency"] == 3


def test_build_index_empty_page():
    """An empty page should produce an empty index for words."""
    pages = [{"url": "http://empty.com", "title": "Empty", "text": ""}]
    index = build_index(pages)
    assert index["_metadata"]["total_docs"] == 1
    # No word entries besides metadata
    word_keys = [k for k in index.keys() if k != "_metadata"]
    assert word_keys == []


def test_save_and_load_index():
    """Round-trip test for save_index / load_index."""
    index = {
        "_metadata": {"total_docs": 1, "avg_doc_length": 5},
        "word": {
            "http://example.com": {
                "frequency": 5,
                "positions": [0, 3, 7],
                "title": "Example",
                "doc_length": 10,
            }
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        path = f.name
    try:
        save_index(index, path)
        loaded = load_index(path)
        assert loaded == index
    finally:
        os.remove(path)


def test_get_metadata():
    """get_metadata should return metadata or defaults."""
    index_with_meta = {"_metadata": {"total_docs": 10, "avg_doc_length": 50}}
    assert get_metadata(index_with_meta) == {"total_docs": 10, "avg_doc_length": 50}

    index_without_meta = {"hello": {}}
    assert get_metadata(index_without_meta) == {"total_docs": 0, "avg_doc_length": 0}


def test_get_document_frequency():
    """get_document_frequency should count documents containing a word."""
    index = {
        "hello": {
            "http://a.com": {},
            "http://b.com": {},
            "http://c.com": {},
        },
        "world": {
            "http://a.com": {},
        },
    }
    assert get_document_frequency(index, "hello") == 3
    assert get_document_frequency(index, "world") == 1
    assert get_document_frequency(index, "nonexistent") == 0
