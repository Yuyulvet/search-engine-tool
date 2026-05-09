"""Tests for the main CLI module."""

import os
import tempfile
import json

import pytest
from unittest.mock import patch, MagicMock

from src.main import SearchTool


@pytest.fixture
def sample_index_file():
    """Create a temporary index file for testing."""
    index = {
        "_metadata": {"total_docs": 2, "avg_doc_length": 5},
        "hello": {
            "http://a.com": {
                "frequency": 2, "positions": [0, 1], "title": "A", "doc_length": 5
            }
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        path = f.name
        json.dump(index, f)
    yield path
    os.remove(path)


class TestSearchTool:
    """Unit tests for the SearchTool class."""

    def test_init(self):
        """SearchTool should initialise with no index."""
        tool = SearchTool()
        assert tool.index is None

    def test_print_word_without_index(self, capsys):
        """print_word without loaded index should prompt user."""
        tool = SearchTool()
        tool.print_word("hello")
        captured = capsys.readouterr()
        assert "No index loaded" in captured.out

    def test_find_without_index(self, capsys):
        """find without loaded index should prompt user."""
        tool = SearchTool()
        tool.find(["hello"])
        captured = capsys.readouterr()
        assert "No index loaded" in captured.out

    def test_load_and_print(self, sample_index_file, capsys):
        """Load a real index file and print a word."""
        tool = SearchTool()
        with patch('src.main.INDEX_PATH', sample_index_file):
            tool.load()
            assert tool.index is not None
            tool.print_word("hello")
        captured = capsys.readouterr()
        assert "hello" in captured.out
        assert "http://a.com" in captured.out

    def test_load_and_find(self, sample_index_file, capsys):
        """Load a real index file and run a query."""
        tool = SearchTool()
        with patch('src.main.INDEX_PATH', sample_index_file):
            tool.load()
            tool.find(["hello"])
        captured = capsys.readouterr()
        assert "Found" in captured.out

    def test_load_missing_file(self, capsys):
        """Loading a non-existent index should print an error."""
        tool = SearchTool()
        with patch('src.main.INDEX_PATH', '/nonexistent/path.json'):
            tool.load()
        captured = capsys.readouterr()
        assert "not found" in captured.out
