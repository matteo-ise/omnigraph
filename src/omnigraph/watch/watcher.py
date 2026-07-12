from __future__ import annotations

import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from omnigraph.crawler.walker import FileEntry
from omnigraph.embed.engine import Embedder
from omnigraph.extract import extract_file
from omnigraph.graph.builder import GraphBuilder
from omnigraph.graph.store import GraphStore
from omnigraph.search.keyword import KeywordSearch
from omnigraph.search.semantic import SemanticSearch


class DebouncedHandler(FileSystemEventHandler):
    def __init__(
        self,
        store: GraphStore,
        builder: GraphBuilder,
        roots: list[Path],
        debounce_seconds: float = 1.0,
    ):
        self.store = store
        self.builder = builder
        self.roots = roots
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
            # Find which root it belongs to
            root_path = next((r for r in self.roots if path.is_relative_to(r)), self.roots[0])
            node_id = self.builder.build_from_file(entry, content, root_path)

            if content:
                kw = KeywordSearch(self.store.conn)
                embedder = Embedder()
                semantic = SemanticSearch(self.store.conn, dimension=embedder.dimension)

                title = content.metadata.get("title", path.name)
                file_id = node_id
                kw.index(file_id, str(path), title, content.text)

                semantic.delete(file_id)
                chunks = content.chunks if content.chunks else embedder.chunk_text(content.text)
                if chunks:
                    embeddings = embedder.encode(chunks)
                    for i, emb in enumerate(embeddings):
                        semantic.index(f"{file_id}:chunk{i}", emb)

                    for emb in embeddings:
                        results = semantic.search(emb, k=3)
                        for r in results:
                            other_id = r.file_id.split(":")[0] + ":" + r.file_id.split(":")[1]
                            if other_id != file_id and r.score > 0.8:
                                from omnigraph.graph.models import Edge

                                self.store.add_edge(
                                    Edge(
                                        src=file_id,
                                        dst=other_id,
                                        type="SIMILAR_TO",
                                        properties={"score": r.score},
                                    )
                                )
                                self.store.add_edge(
                                    Edge(
                                        src=other_id,
                                        dst=file_id,
                                        type="SIMILAR_TO",
                                        properties={"score": r.score},
                                    )
                                )

            self.store.commit()
        except Exception:
            pass

    def _handle_delete(self, path_str: str):
        path = Path(path_str)
        self.store.delete_file(path)
        kw = KeywordSearch(self.store.conn)
        file_id = f"file:{path.name}"
        kw.delete(file_id)

        embedder = Embedder()
        semantic = SemanticSearch(self.store.conn, dimension=embedder.dimension)
        semantic.delete(file_id)

        self.store.commit()


class FileWatcher:
    def __init__(
        self,
        store: GraphStore,
        roots: list[Path] | Path,
        debounce_seconds: float = 1.0,
    ):
        self.store = store
        self.roots = roots if isinstance(roots, list) else [roots]
        self.builder = GraphBuilder(store)
        self.handler = DebouncedHandler(store, self.builder, self.roots, debounce_seconds)
        self.observer = Observer()

    def start(self):
        for root in self.roots:
            self.observer.schedule(self.handler, str(root), recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def run(self):
        import signal

        self._running = True

        def handle_sigint(sig, frame):
            self._running = False

        signal.signal(signal.SIGINT, handle_sigint)
        signal.signal(signal.SIGTERM, handle_sigint)

        self.start()
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
