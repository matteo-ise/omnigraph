from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from omnigraph.config import get_config
from omnigraph.search.keyword import KeywordSearch
from omnigraph.search.semantic import SemanticSearch


@dataclass
class HybridResult:
    file_id: str
    path: str
    score: float
    snippet: str = ""


def hybrid_search(
    conn: sqlite3.Connection,
    query: str,
    k: int = 10,
    mode: str = "hybrid",
) -> list[HybridResult]:
    config = get_config()
    keyword_weight = config.hybrid_weight_keyword
    semantic_weight = config.hybrid_weight_semantic

    if mode == "keyword":
        kw = KeywordSearch(conn)
        results = kw.search(query, k)
        return [
            HybridResult(file_id=r.file_id, path=r.path, score=r.score, snippet=r.snippet)
            for r in results
        ]

    if mode == "semantic":
        from omnigraph.embed import Embedder

        embedder = Embedder()
        query_vec = embedder.encode_query(query)
        sem = SemanticSearch(conn, embedder.dimension)
        results = sem.search(query_vec, k)
        return [HybridResult(file_id=r.file_id, path="", score=r.score) for r in results]

    kw = KeywordSearch(conn)
    kw_results = kw.search(query, k * 2)

    from omnigraph.embed import Embedder

    embedder = Embedder()
    query_vec = embedder.encode_query(query)
    sem = SemanticSearch(conn, embedder.dimension)
    sem_results = sem.search(query_vec, k * 2)

    scores: dict[str, float] = {}
    paths: dict[str, str] = {}
    snippets: dict[str, str] = {}
    node_ids: dict[str, str] = {}

    max_kw = max((r.score for r in kw_results), default=1.0) or 1.0
    for r in kw_results:
        key = r.path
        scores[key] = scores.get(key, 0) + keyword_weight * (r.score / max_kw)
        paths[key] = r.path
        snippets[key] = r.snippet
        # Look up node_id
        row = conn.execute("SELECT node_id FROM files WHERE path=?", (r.path,)).fetchone()
        if row:
            node_ids[key] = row["node_id"]

    max_sem = max((r.score for r in sem_results), default=1.0) or 1.0
    for r in sem_results:
        # r.file_id is like "file:hash:chunk_i"
        node_id = r.file_id.rsplit(":", 1)[0]
        
        # Look up path from node_id
        row = conn.execute("SELECT path FROM files WHERE node_id=?", (node_id,)).fetchone()
        if row:
            key = row["path"]
            scores[key] = scores.get(key, 0) + semantic_weight * (r.score / max_sem)
            if key not in paths:
                paths[key] = key
            if key not in snippets:
                snippets[key] = "" # semantic doesn't have snippets currently
            node_ids[key] = node_id

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
    return [
        HybridResult(
            file_id=node_ids.get(key, ""),
            path=key,
            score=score,
            snippet=snippets.get(key, ""),
        )
        for key, score in ranked
    ]
