from pathlib import Path

import pytest

from omnigraph.crawler import walk
from omnigraph.extract import extract_file
from omnigraph.graph import GraphBuilder, GraphStore


@pytest.fixture
def temp_tree(tmp_path: Path):
    (tmp_path / "file1.txt").write_text("hello world #test")
    (tmp_path / "file2.md").write_text("---\ntitle: My Doc\n---\n# Content\nSome text here.")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "file3.py").write_text("print('hello')")
    return tmp_path


@pytest.fixture
def store(tmp_path: Path):
    db_path = tmp_path / "test.db"
    with GraphStore(db_path) as s:
        yield s


def test_build_from_files(temp_tree: Path, store: GraphStore):
    entries = walk(temp_tree, extra_ignores=[".git"])
    builder = GraphBuilder(store)

    for entry in entries:
        content = extract_file(entry.path)
        builder.build_from_file(entry, content, temp_tree)

    store.commit()
    stats = store.get_stats()
    assert stats["files"] >= 3
    assert stats["nodes"] > 3
    assert stats["edges"] > 0


def test_contains_edge(temp_tree: Path, store: GraphStore):
    entries = walk(temp_tree, extra_ignores=[".git"])
    builder = GraphBuilder(store)

    for entry in entries:
        content = extract_file(entry.path)
        builder.build_from_file(entry, content, temp_tree)

    store.commit()
    projects = store.list_projects()
    assert len(projects) == 1

    project_node = store.get_node(projects[0].id)
    assert project_node is not None

    neighbors = store.query_neighbors(projects[0].id, depth=1)
    assert len(neighbors) > 0


def test_tag_extraction(temp_tree: Path, store: GraphStore):
    entries = walk(temp_tree, extra_ignores=[".git"])
    builder = GraphBuilder(store)

    for entry in entries:
        content = extract_file(entry.path)
        builder.build_from_file(entry, content, temp_tree)

    store.commit()
    tag_node = store.get_node("tag:test")
    assert tag_node is not None
    assert tag_node.type == "tag"


def test_topic_extraction(temp_tree: Path, store: GraphStore):
    entries = walk(temp_tree, extra_ignores=[".git"])
    builder = GraphBuilder(store)

    for entry in entries:
        content = extract_file(entry.path)
        builder.build_from_file(entry, content, temp_tree)

    store.commit()
    stats = store.get_stats()
    topic_nodes = [n for n in store.query_neighbors("tag:test", depth=2) if n.type == "topic"]
    assert stats["nodes"] > 3
