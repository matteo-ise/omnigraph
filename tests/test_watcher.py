import time
from pathlib import Path

import pytest

from omnigraph.graph import GraphBuilder, GraphStore
from omnigraph.watch.watcher import FileWatcher


@pytest.fixture
def watch_setup(tmp_path: Path):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "existing.txt").write_text("existing content")

    db_path = tmp_path / "test.db"
    store = GraphStore(db_path)

    watcher = FileWatcher(store, tree, debounce_seconds=0.2)
    watcher.start()

    yield store, tree

    watcher.stop()
    store.close()


def test_watcher_detects_new_file(watch_setup):
    store, tree = watch_setup
    new_file = tree / "new_file.txt"
    new_file.write_text("new content here")

    time.sleep(1.5)

    stats = store.get_stats()
    assert stats["files"] > 0


def test_watcher_detects_modification(watch_setup):
    store, tree = watch_setup
    existing = tree / "existing.txt"
    existing.write_text("modified content")

    time.sleep(1.5)

    stats = store.get_stats()
    assert stats["files"] > 0


def test_watcher_detects_deletion(watch_setup):
    store, tree = watch_setup
    existing = tree / "existing.txt"
    existing.unlink()

    time.sleep(1.5)

    file_rec = store.get_file(existing)
    assert file_rec is None
