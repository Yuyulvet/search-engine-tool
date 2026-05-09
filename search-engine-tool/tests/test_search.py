"""Tests for the search module."""

import pytest
import math

from src.search import (
    print_word_index,
    find_pages,
    print_find_results,
    compute_tf_idf,
    compute_proximity_score,
)


@pytest.fixture
def sample_index():
    """A small inverted index for testing search logic with metadata."""
    return {
        "_metadata": {"total_docs": 3, "avg_doc_length": 5},
        "hello": {
            "http://a.com": {"frequency": 2, "positions": [0, 2], "title": "Page A", "doc_length": 5},
            "http://b.com": {"frequency": 1, "positions": [0], "title": "Page B", "doc_length": 4},
        },
        "world": {
            "http://a.com": {"frequency": 1, "positions": [1], "title": "Page A", "doc_length": 5},
        },
        "foo": {
            "http://b.com": {"frequency": 3, "positions": [1, 2, 3], "title": "Page B", "doc_length": 4},
        },
    }


# ------------------------------------------------------------------
# TF-IDF tests
# ------------------------------------------------------------------

def test_compute_tf_idf_basic():
    """TF-IDF should be frequency/length * ln(total_docs/doc_freq)."""
    score = compute_tf_idf(frequency=2, doc_length=10, total_docs=100, doc_freq=10)
    expected_tf = 2 / 10
    expected_idf = math.log(100 / 10)
    assert score == pytest.approx(expected_tf * expected_idf, rel=1e-4)


def test_compute_tf_idf_zero_doc_length():
    """Zero doc_length should return 0 to avoid division by zero."""
    assert compute_tf_idf(1, 0, 100, 5) == 0.0


def test_compute_tf_idf_zero_doc_freq():
    """Zero doc_freq should return 0."""
    assert compute_tf_idf(1, 10, 100, 0) == 0.0


# ------------------------------------------------------------------
# Proximity tests
# ------------------------------------------------------------------

def test_compute_proximity_score_adjacent():
    """Adjacent words (distance 1) should get high bonus."""
    score = compute_proximity_score([0, 5], [1, 6])
    # min distance is 1 (0 vs 1)
    expected = 1.0 / (1.0 + 1)
    assert score == pytest.approx(expected)


def test_compute_proximity_score_far_apart():
    """Distant words should get low bonus."""
    score = compute_proximity_score([0], [100])
    expected = 1.0 / (1.0 + 100)
    assert score == pytest.approx(expected)


def test_compute_proximity_score_empty():
    """Empty positions should return 0."""
    assert compute_proximity_score([], [1, 2]) == 0.0
    assert compute_proximity_score([1, 2], []) == 0.0


# ------------------------------------------------------------------
# Search query tests
# ------------------------------------------------------------------

def test_find_single_word(sample_index):
    """Find pages with a single word."""
    results = find_pages(sample_index, "hello")
    assert len(results) == 2
    urls = {r["url"] for r in results}
    assert urls == {"http://a.com", "http://b.com"}


def test_find_multi_word_and_logic(sample_index):
    """Find pages containing ALL query words (AND logic)."""
    results = find_pages(sample_index, "hello world")
    assert len(results) == 1
    assert results[0]["url"] == "http://a.com"


def test_find_no_match(sample_index):
    """Query with a non-existent word returns empty list."""
    results = find_pages(sample_index, "nonexistent")
    assert results == []


def test_find_empty_query(sample_index):
    """Empty query returns empty list."""
    results = find_pages(sample_index, "")
    assert results == []


def test_find_results_are_sorted(sample_index):
    """Results should be sorted by composite score descending."""
    results = find_pages(sample_index, "hello")
    # Page A has higher TF-IDF (freq 2, doc_length 5) vs Page B (freq 1, doc_length 4)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_find_includes_score_fields(sample_index):
    """Results should include TF-IDF, proximity_bonus, and composite score."""
    results = find_pages(sample_index, "hello world")
    assert len(results) == 1
    r = results[0]
    assert "score" in r
    assert "tf_idf" in r
    assert "proximity_bonus" in r
    assert "frequencies" in r


def test_find_proximity_bonus_for_multiword(sample_index):
    """Multi-word queries should have a proximity bonus."""
    results = find_pages(sample_index, "hello world")
    assert len(results) == 1
    # hello at [0,2], world at [1] → min distance = 1
    assert results[0]["proximity_bonus"] > 0


def test_print_word_index_found(sample_index, capsys):
    """print_word_index should output stats for a found word."""
    print_word_index(sample_index, "world")
    captured = capsys.readouterr()
    assert "world" in captured.out
    assert "http://a.com" in captured.out


def test_print_word_index_not_found(sample_index, capsys):
    """print_word_index should report when a word is absent."""
    print_word_index(sample_index, "missing")
    captured = capsys.readouterr()
    assert "No results found" in captured.out


def test_print_word_index_ignores_metadata(sample_index, capsys):
    """print_word_index should not treat _metadata as a searchable word."""
    print_word_index(sample_index, "_metadata")
    captured = capsys.readouterr()
    assert "No results found" in captured.out
