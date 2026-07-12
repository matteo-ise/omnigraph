#!/usr/bin/env python3
"""Benchmark omnigraph indexing speed and search latency."""
from __future__ import annotations

import sys
import time
from pathlib import Path

from omnigraph.config import get_config
from omnigraph.crawler.walker import walk
from omnigraph.extract import extract_file
from omnigraph.graph.builder import GraphBuilder
from omnigraph.graph.store import GraphStore
from omnigraph.search.keyword import KeywordSearch


def benchmark_index(root: Path) -> dict:
    config = get_config()
    config.db_path.unlink(missing_ok=True)

    with GraphStore(config.db_path) as store:
        builder = GraphBuilder(store)
        kw = KeywordSearch(store.conn)

        start = time.perf_counter()
        entries = walk(root)
        crawl_time = time.perf_counter() - start

        index_start = time.perf_counter()
        total = 0
        for entry in entries:
            content = extract_file(entry.path)
            builder.build_from_file(entry, content, root)
            if content:
                title = content.metadata.get("title", entry.path.name)
                file_id = f"file:{entry.path.name}"
                kw.index(file_id, str(entry.path), title, content.text)
            total += 1
        store.commit()
        index_time = time.perf_counter() - index_start

        stats = store.get_stats()

    return {
        "files": total,
        "crawl_time_s": round(crawl_time, 3),
        "index_time_s": round(index_time, 3),
        "total_time_s": round(crawl_time + index_time, 3),
        "files_per_sec": round(total / index_time, 1) if index_time > 0 else 0,
        "db_nodes": stats["nodes"],
        "db_edges": stats["edges"],
    }


def benchmark_search(queries: list[str]) -> list[dict]:
    config = get_config()
    results = []
    with GraphStore(config.db_path) as store:
        kw = KeywordSearch(store.conn)
        for q in queries:
            start = time.perf_counter()
            hits = kw.search(q, k=10)
            elapsed = (time.perf_counter() - start) * 1000
            results.append({"query": q, "hits": len(hits), "latency_ms": round(elapsed, 2)})
    return results


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/fixtures")
    print(f"Benchmarking omnigraph on: {root}\n")

    idx = benchmark_index(root)
    print("=== Indexing ===")
    for k, v in idx.items():
        print(f"  {k}: {v}")

    print("\n=== Search ===")
    queries = ["test", "sample", "hello", "invoice", "readme"]
    results = benchmark_search(queries)
    for r in results:
        print(f"  '{r['query']}': {r['hits']} hits in {r['latency_ms']}ms")


if __name__ == "__main__":
    main()