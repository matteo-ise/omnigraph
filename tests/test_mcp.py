from pathlib import Path

import pytest

from omnigraph.crawler import walk
from omnigraph.extract import extract_file
from omnigraph.graph import GraphBuilder, GraphStore
from omnigraph.mcp_server.server import mcp


@pytest.fixture
def mcp_indexed_store(tmp_path: Path, monkeypatch):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "invoice.txt").write_text("Quarterly invoice for Q3 2024 amount $5000")
    (tree / "readme.md").write_text("# Project README\nThis is a sample project.")

    db_path = tmp_path / "test.db"

    # Mock the get_config to use our tmp_path database and roots
    from omnigraph.config import Config

    mock_config = Config(db_path=db_path, roots=[tree])
    monkeypatch.setattr("omnigraph.mcp_server.tools.get_config", lambda: mock_config)

    store = GraphStore(db_path)
    entries = walk(tree, extra_ignores=[".git"])
    builder = GraphBuilder(store)
    from omnigraph.search.keyword import KeywordSearch

    kw = KeywordSearch(store.conn)

    for entry in entries:
        content = extract_file(entry.path)
        builder.build_from_file(entry, content, tree)
        if content:
            title = content.metadata.get("title", entry.path.name)
            file_id = f"file:{entry.path.name}"
            kw.index(file_id, str(entry.path), title, content.text)

    store.commit()
    yield store, tree
    store.close()


def test_mcp_list_projects(mcp_indexed_store):
    import omnigraph.mcp_server.tools as mcp_tools

    projects = mcp_tools.list_projects()
    assert len(projects) == 1
    assert "tree" in projects[0].name


def test_mcp_search(mcp_indexed_store):
    import omnigraph.mcp_server.tools as mcp_tools

    results = mcp_tools.search("invoice", k=5)
    assert len(results) > 0
    assert "invoice" in results[0].path


def test_mcp_get_file(mcp_indexed_store):
    store, tree = mcp_indexed_store
    import omnigraph.mcp_server.tools as mcp_tools

    file_rec = store.get_file(tree / "invoice.txt")
    assert file_rec is not None

    result = mcp_tools.get_file(str(tree / "invoice.txt"))
    assert "invoice" in result.text


def test_mcp_graph_query(mcp_indexed_store):
    store, tree = mcp_indexed_store
    import omnigraph.mcp_server.tools as mcp_tools

    file_rec = store.get_file(tree / "invoice.txt")
    assert file_rec is not None

    result = mcp_tools.graph_query(file_rec.node_id, depth=1)
    assert result.center.id == file_rec.node_id
    assert len(result.nodes) > 0


def test_mcp_reindex(mcp_indexed_store):
    store, tree = mcp_indexed_store
    import omnigraph.mcp_server.tools as mcp_tools

    (tree / "new_mcp_file.txt").write_text("Hello from MCP reindexing test")

    result = mcp_tools.reindex(str(tree))
    assert result.status == "success"
    assert result.total_files_processed == 3

    res2 = mcp_tools.search("reindexing", k=3)
    assert len(res2) > 0
    assert any("new_mcp_file" in r.path for r in res2)
