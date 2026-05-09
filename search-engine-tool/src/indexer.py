"""
Indexer module for search-engine-tool.

Builds an inverted index from crawled pages with TF-IDF support.
The index maps each normalised (lowercased) word to a dictionary
of page URLs containing statistics for that word.

Index structure:
{
    "_metadata": {
        "total_docs": int,
        "avg_doc_length": float
    },
    word: {
        url: {
            "frequency": int,
            "positions": [int, ...],
            "title": str,
            "doc_length": int
        },
        ...
    },
    ...
}
"""

import json
import math
import re
from collections import defaultdict


def tokenize(text: str) -> list[str]:
    """
    Extract words from text, lowercasing and stripping punctuation.
    """
    return re.findall(r"[a-z0-9']+", text.lower())


def build_index(pages: list[dict]) -> dict:
    """
    Build an inverted index from a list of crawled pages.

    Args:
        pages: List of page dictionaries with keys 'url', 'title', 'text'.

    Returns:
        Inverted index dictionary with metadata for TF-IDF scoring.
    """
    index: dict = defaultdict(dict)
    total_doc_length = 0

    for page in pages:
        url = page["url"]
        title = page.get("title", "")
        full_text = page.get("text", "")
        tokens = tokenize(full_text)
        doc_length = len(tokens)
        total_doc_length += doc_length

        # Track positions of each word in this page
        word_positions: dict[str, list[int]] = defaultdict(list)
        for pos, word in enumerate(tokens):
            word_positions[word].append(pos)

        for word, positions in word_positions.items():
            index[word][url] = {
                "frequency": len(positions),
                "positions": positions,
                "title": title,
                "doc_length": doc_length,
            }

    # Store metadata for TF-IDF calculations at top level
    avg_doc_length = total_doc_length / len(pages) if pages else 0
    metadata = {
        "total_docs": len(pages),
        "avg_doc_length": round(avg_doc_length, 2),
    }

    result = dict(index)
    result["_metadata"] = metadata
    return result


def get_metadata(index: dict) -> dict:
    """Return index metadata, or defaults if missing (backwards compatibility)."""
    return index.get("_metadata", {"total_docs": 0, "avg_doc_length": 0})


def get_document_frequency(index: dict, word: str) -> int:
    """Return the number of documents containing the given word."""
    entries = index.get(word, {})
    return len(entries)


def save_index(index: dict, filepath: str) -> None:
    """Serialise the inverted index to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def load_index(filepath: str) -> dict:
    """Load an inverted index from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
