# Search Engine Tool

A command-line search engine that crawls [quotes.toscrape.com](https://quotes.toscrape.com/), builds an inverted index, and supports intelligent page retrieval with TF-IDF ranking and phrase proximity scoring.

## Overview

This project implements a web search engine with four core commands:

- **build** – crawl the target website and persist the inverted index
- **load** – restore a previously built index from disk
- **print <word>** – display the inverted-index entry for a single word
- **find <word1> [<word2> ...]** – retrieve pages that contain **all** supplied words (AND logic), ranked by relevance

### Advanced Features (Beyond Requirements)

- **TF-IDF Ranking** – results are scored by term frequency–inverse document frequency, giving higher rank to pages where query words are rare and frequent
- **Phrase Proximity Scoring** – multi-word queries receive a bonus when the words appear close together, surfacing pages with natural phrase matches
- **Performance Benchmarks** – included test suite verifies index construction and query latency under load

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Crawler   │ ───→ │   Indexer   │ ───→ │  JSON File  │
│  (requests) │      │  (in-memory)│      │ (data/index)│
│  6s delay   │      │  + metadata │      │             │
└─────────────┘      └─────────────┘      └──────┬──────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │   Search    │
                                           │  (TF-IDF +  │
                                           │  proximity) │
                                           └─────────────┘
```

### Inverted Index Structure

```json
{
  "_metadata": {
    "total_docs": 50,
    "avg_doc_length": 1234
  },
  "hello": {
    "https://quotes.toscrape.com/": {
      "frequency": 3,
      "positions": [12, 45, 67],
      "title": "Quotes to Scrape",
      "doc_length": 200
    }
  }
}
```

## Algorithm Complexity

| Operation | Time Complexity | Space Complexity |
|---|---|---|
| Crawl (N pages, 6s delay) | O(N) network time | O(N) page storage |
| Build index | O(N × W) | O(N × W) |
| Save / load index | O(1) disk I/O | O(N × W) in memory |
| Single-word search | O(1) index lookup | O(P) result pages |
| Multi-word search | O(k × P) | O(P) |

*Where N = number of pages, W = average words per page, k = query word count, P = pages containing query words*

## Design Decisions

### Why TF-IDF over raw frequency?
Raw word count biases toward long pages. TF-IDF normalises by document length (TF) and rewards rare query terms (IDF), producing more relevant rankings.

### Why JSON for index storage?
- Human-readable for debugging and coursework demonstration
- Language-agnostic and version-control friendly
- Trade-off: larger file size (~1 MB for 50 pages) vs. binary formats

### Why AND logic for multi-word queries?
Matches user expectation (Google default behaviour). Higher precision ensures every result is genuinely relevant to the full query.

### Proximity scoring
When a user searches for "good friends", pages where the words appear adjacent (e.g. "good friends") should outrank pages where they are scattered. The proximity bonus is computed as `1 / (1 + min_distance)`, so adjacent words yield the maximum bonus of 0.5.

## Installation

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests` – HTTP requests
- `beautifulsoup4` – HTML parsing
- `pytest` – testing framework
- `pytest-cov` – coverage reporting

## Usage

```bash
cd src
python main.py
```

Interactive shell:

```
> build
Starting crawl...
  Crawled [1/100]: https://quotes.toscrape.com
  ...
Crawled 50 pages. Building index...
Index saved to ../data/index.json

> load
Index loaded from ../data/index.json

> print love
Inverted index for 'love':
  URL:       https://quotes.toscrape.com/tag/love/
  Title:     Quotes to Scrape
  Frequency: 23
  Positions: [9, 35, 243, ...]

> find good friends
Found 18 page(s):
  URL:      https://quotes.toscrape.com/tag/friends/
  Title:    Quotes to Scrape
  Score:    0.0523  (TF-IDF: 0.0349, Proximity: 0.5)
  Freq:     {'good': 3, 'friends': 11}

> exit
```

## Testing

Run the full test suite (excludes slow network tests):

```bash
pytest tests/ -v -m "not slow"
```

Run with coverage report:

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

Run slow integration tests (require network):

```bash
pytest tests/ -v -m "slow"
```

## Project Structure

```
search-engine-tool/
├── src/
│   ├── __init__.py
│   ├── crawler.py      # Web crawling (HTTP + HTML parsing)
│   ├── indexer.py      # Inverted index construction + metadata
│   ├── search.py       # TF-IDF scoring, proximity, query processing
│   └── main.py         # CLI entry point
├── tests/
│   ├── conftest.py
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_search.py
│   ├── test_main.py
│   └── test_performance.py
├── data/
│   └── index.json      # Compiled index file
├── requirements.txt
├── .gitignore
└── README.md
```

## GenAI Usage Declaration

This project was developed with assistance from generative AI tools (Claude Code). AI was used for:

- Initial project scaffolding and module structure design
- TF-IDF and proximity scoring algorithm implementation
- Test case generation and edge-case identification
- README and documentation drafting

All AI-generated code was reviewed, modified, and validated by the author to ensure full understanding of every implementation detail.
