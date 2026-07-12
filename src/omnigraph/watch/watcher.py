from __future__ import annotations

import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from omnigraph.crawler.walker import FileEntry
from omnigraph.extract import extract_file
from omnigraph.graph.builder import GraphBuilder
from omnigraph.graph.store import GraphStore
from omnigraph.search.keyword import KeywordSearch


class DebouncedHandler(FileSystemEventHandler):
    def __init__(
        self,
        store: GraphStore,
        builder: GraphBuilder,
        root: Path,
        debounce_seconds: float = 1.0,
    ):
        self.store = store
        self.builder = builder
        self.root = root
        self.debounce_seconds = debounce_seconds
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_delete(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle_delete(event.src_path)
            self._schedule(event.dest_path)

    def _schedule(self, path: str):
        with self._lock:
            self._pending[path] = time.time()
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._process_pending)
            self._timer.start()

    def _process_pending(self):
        with self._lock:
            pending = dict(self._pending)
            self._pending.clear()

        for path_str in pending:
            self._handle_upsert(path_str)

    def _handle_upsert(self, path_str: str):
        path = Path(path_str)
        if not path.exists() or not path.is_file():
            return

        try:
            stat = path.stat()
            entry = FileEntry(
                path=path,
                size=stat.st_size,
                mtime=stat.st_mtime,
                ext=path.suffix.lower(),
            )
            content = extract_file(path)
            self.builder.build_from_file(entry, content, self.root)

            if content:
                kw = KeywordSearch(self.store.conn)
                title = content.metadata.get("title", path.name)
                file_id = f"file:{path.name}"
                kw.index(file_id, str(path), title, content.text)

            self.store.commit()
        except Exception:
            pass

    def _handle_delete(self, path_str: str):
        path = Path(path_str)
        self.store.delete_file(path)
        kw = KeywordSearch(self.store.conn)
        kw.delete(f"file:{path.name}")
        self.store.commit()


class FileWatcher:
    def __init__(
        self,
        store: GraphStore,
        root: Path,
        debounce_seconds: float = 1.0,
    ):
        self.store = store
        self.root = root
        self.builder = GraphBuilder(store)
        self.handler = DebouncedHandler(store, self.builder, root, debounce_seconds)
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.handler, str(self.root), recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
