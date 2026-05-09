"""
Main CLI entry point for the search-engine-tool.

Commands:
    build               Crawl the site and save the index.
    load                Load a previously saved index.
    print <word>        Show inverted index for a word.
    find <query ...>    Find pages containing all query words.
"""

import sys
import os

from src.crawler import crawl_website
from src.indexer import build_index, save_index, load_index
from src.search import print_word_index, find_pages, print_find_results

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "index.json")


class SearchTool:
    def __init__(self):
        self.index = None

    def build(self) -> None:
        """Crawl the website, build the index, and save it."""
        print("Starting crawl...")
        pages = crawl_website()
        print(f"Crawled {len(pages)} pages. Building index...")
        self.index = build_index(pages)
        save_index(self.index, INDEX_PATH)
        print(f"Index saved to {INDEX_PATH}")

    def load(self) -> None:
        """Load the index from disk."""
        if not os.path.exists(INDEX_PATH):
            print(f"Index file not found at {INDEX_PATH}. Run 'build' first.")
            return
        self.index = load_index(INDEX_PATH)
        print(f"Index loaded from {INDEX_PATH}")

    def print_word(self, word: str) -> None:
        """Print index entries for a word."""
        if self.index is None:
            print("No index loaded. Run 'load' or 'build' first.")
            return
        print_word_index(self.index, word)

    def find(self, query_words: list[str]) -> None:
        """Find pages matching the query."""
        if self.index is None:
            print("No index loaded. Run 'load' or 'build' first.")
            return
        query = " ".join(query_words)
        results = find_pages(self.index, query)
        print_find_results(results)


def main():
    tool = SearchTool()

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue

        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "build":
            tool.build()
        elif command == "load":
            tool.load()
        elif command == "print":
            if not args:
                print("Usage: print <word>")
                continue
            tool.print_word(args[0])
        elif command == "find":
            if not args:
                print("Usage: find <word> [<word> ...]")
                continue
            tool.find(args)
        elif command in ("exit", "quit"):
            print("Exiting.")
            break
        else:
            print(f"Unknown command: '{command}'. Available: build, load, print, find, exit")


if __name__ == "__main__":
    main()
