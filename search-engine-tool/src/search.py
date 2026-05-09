"""
Search module for search-engine-tool.

Provides functionality to query the inverted index.
Supports:
- Single-word and multi-word (AND) queries
- TF-IDF ranking for result relevance
- Phrase proximity scoring (words closer together score higher)
"""

import math
from typing import Any

from src.indexer import get_metadata, get_document_frequency


def print_word_index(index: dict, word: str) -> None:
    """
    Print the inverted index entries for a single word.

    Args:
        index: The loaded inverted index.
        word: The word to look up (case-insensitive).
    """
    normalized = word.lower()
    entries = index.get(normalized)

    if not entries or normalized == "_metadata":
        print(f"No results found for '{word}'.")
        return

    print(f"\nInverted index for '{word}':")
    print("=" * 50)
    for url, stats in entries.items():
        print(f"  URL:      {url}")
        print(f"  Title:    {stats.get('title', 'N/A')}")
        print(f"  Frequency:{stats['frequency']}")
        print(f"  Positions:{stats['positions']}")
        print("-" * 50)


def compute_tf_idf(
    frequency: int,
    doc_length: int,
    total_docs: int,
    doc_freq: int,
) -> float:
    """
    Compute TF-IDF score for a term in a document.

    Uses a smoothed formulation to avoid division-by-zero:
        TF  = frequency / doc_length
        IDF = ln(total_docs / doc_freq)
    """
    if doc_length == 0 or doc_freq == 0:
        return 0.0

    tf = frequency / doc_length
    idf = math.log(total_docs / doc_freq)
    return tf * idf


def compute_proximity_score(
    positions_a: list[int],
    positions_b: list[int],
) -> float:
    """
    Compute a proximity bonus for two words.

    Finds the minimum distance between any occurrence of word A
    and any occurrence of word B. Closer words get a higher bonus.
    Returns 0 if no proximity can be computed.
    """
    if not positions_a or not positions_b:
        return 0.0

    min_dist = float("inf")
    i = j = 0
    # Two-pointer scan to find minimum absolute distance
    while i < len(positions_a) and j < len(positions_b):
        dist = abs(positions_a[i] - positions_b[j])
        if dist < min_dist:
            min_dist = dist
        if positions_a[i] < positions_b[j]:
            i += 1
        else:
            j += 1

    # Convert distance to a bonus: closer = higher bonus
    # Distance 1 (adjacent words) gets the maximum bonus of 1.0
    if min_dist == float("inf"):
        return 0.0
    return 1.0 / (1.0 + min_dist)


def find_pages(index: dict, query: str) -> list[dict]:
    """
    Find pages that contain all words in the query.

    Results are ranked by a composite score combining:
    1. TF-IDF relevance (higher = more relevant)
    2. Phrase proximity bonus (words closer together score higher)

    Args:
        index: The loaded inverted index.
        query: Space-separated query string.

    Returns:
        A list of result dictionaries sorted by composite score descending.
    """
    words = query.lower().split()
    words = [w.strip() for w in words if w.strip()]

    if not words:
        return []

    metadata = get_metadata(index)
    total_docs = metadata.get("total_docs", 0)

    # Start with pages containing the first word
    first_word = words[0]
    if first_word not in index:
        return []

    candidate_urls = set(index[first_word].keys())

    # Intersect with pages for remaining words (AND logic)
    for word in words[1:]:
        if word not in index:
            return []
        candidate_urls &= set(index[word].keys())

    results: list[dict] = []
    for url in candidate_urls:
        tf_idf_sum = 0.0
        frequencies = {}
        title = ""
        all_positions: dict[str, list[int]] = {}

        for word in words:
            stats = index[word][url]
            freq = stats["frequency"]
            doc_length = stats.get("doc_length", 1)
            doc_freq = get_document_frequency(index, word)

            tf_idf = compute_tf_idf(freq, doc_length, total_docs, doc_freq)
            tf_idf_sum += tf_idf
            frequencies[word] = freq
            all_positions[word] = stats["positions"]
            if not title:
                title = stats.get("title", "")

        # Compute phrase proximity bonus for multi-word queries
        proximity_bonus = 0.0
        if len(words) >= 2:
            for i in range(len(words) - 1):
                proximity_bonus += compute_proximity_score(
                    all_positions[words[i]],
                    all_positions[words[i + 1]],
                )
            proximity_bonus /= (len(words) - 1)  # average

        # Composite score: TF-IDF weighted by proximity
        composite_score = tf_idf_sum * (1.0 + proximity_bonus)

        results.append({
            "url": url,
            "title": title,
            "score": round(composite_score, 6),
            "tf_idf": round(tf_idf_sum, 6),
            "proximity_bonus": round(proximity_bonus, 4),
            "frequencies": frequencies,
        })

    # Sort by composite score descending
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def print_find_results(results: list[dict]) -> None:
    """Pretty-print results from find_pages."""
    if not results:
        print("No pages found matching the query.")
        return

    print(f"\nFound {len(results)} page(s):")
    print("=" * 60)
    for r in results:
        print(f"  URL:      {r['url']}")
        print(f"  Title:    {r['title']}")
        print(f"  Score:    {r['score']}  (TF-IDF: {r['tf_idf']}, Proximity: {r['proximity_bonus']})")
        print(f"  Freq:     {r['frequencies']}")
        print("-" * 60)
