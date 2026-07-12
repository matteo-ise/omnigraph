from pathlib import Path

import pytest

from omnigraph.crawler import walk
from omnigraph.extract import extract_file
from omnigraph.graph import GraphBuilder, GraphStore
from omnigraph.search.keyword import KeywordSearch


@pytest.fixture
def indexed_store(tmp_path: Path):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "invoice.txt").write_text("Quarterly invoice for Q3 2024 amount $5000")
    (tree / "readme.md").write_text("# Project README\nThis is a sample project.")
    (tree / "notes.txt").write_text("Meeting notes: discuss roadmap and priorities")

    db_path = tmp_path / "test.db"
    store = GraphStore(db_path)

    entries = walk(tree, extra_ignores=[".git"])
    builder = GraphBuilder(store)
    kw = KeywordSearch(store.conn)

    for entry in entries:
        content = extract_file(entry.path)
        builder.build_from_file(entry, content, tree)
        if content:
            title = content.metadata.get("title", entry.path.name)
            kw.index(f"file:{entry.path.name}", str(entry.path), title, content.text)

    store.commit()
    yield store, tree
    store.close()


def test_keyword_search_invoice(indexed_store):
    store, _ = indexed_store
    kw = KeywordSearch(store.conn)
    results = kw.search("invoice")
    assert len(results) > 0
    assert any("invoice" in r.path.lower() for r in results)


def test_keyword_search_readme(indexed_store):
    store, _ = indexed_store
    kw = KeywordSearch(store.conn)
    results = kw.search("readme")
    assert len(results) > 0


def test_keyword_search_no_results(indexed_store):
    store, _ = indexed_store
    kw = KeywordSearch(store.conn)
    results = kw.search("xyznonexistent123")
    assert len(results) == 0
