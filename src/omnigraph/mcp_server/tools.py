from __future__ import annotations

from pathlib import Path

from omnigraph.config import get_config
from omnigraph.crawler.walker import walk
from omnigraph.extract import extract_file
from omnigraph.graph.builder import GraphBuilder
from omnigraph.graph.store import GraphStore
from omnigraph.search.hybrid import hybrid_search
from omnigraph.search.keyword import KeywordSearch


def search(query: str, k: int = 10, mode: str = "hybrid") -> list[dict]:
    config = get_config()
    with GraphStore(config.db_path) as store:
        results = hybrid_search(store.conn, query, k=k, mode=mode)
        return [
            {
                "file_id": r.file_id,
                "path": r.path,
                "score": r.score,
                "snippet": r.snippet,
            }
            for r in results
        ]


def get_file(path: str) -> dict:
    config = get_config()
    with GraphStore(config.db_path) as store:
        file_rec = store.get_file(path)
        if file_rec is None:
            raise ValueError(f"File not found in index: {path}")

        extracted = extract_file(Path(path))
        return {
            "node_id": file_rec.node_id,
            "path": str(file_rec.path),
            "size": file_rec.size,
            "mtime": file_rec.mtime,
            "ext": file_rec.ext,
            "text": extracted.text if extracted else "",
            "metadata": extracted.metadata if extracted else {},
        }


def list_projects() -> list[dict]:
    config = get_config()
    with GraphStore(config.db_path) as store:
        projects = store.list_projects()
        stats = store.get_stats()
        return [
            {
                "id": p.id,
                "root": str(p.root),
                "name": p.name,
                "total_nodes_in_db": stats["nodes"],
                "total_edges_in_db": stats["edges"],
            }
            for p in projects
        ]


def graph_query(node_id: str, depth: int = 2) -> dict:
    config = get_config()
    with GraphStore(config.db_path) as store:
        node = store.get_node(node_id)
        if node is None:
            raise ValueError(f"Node not found: {node_id}")

        neighbors = store.query_neighbors(node_id, depth=depth)

        # Get all edges between these nodes
        nodes_ids = {node_id} | {n.id for n in neighbors}
        placeholders = ",".join("?" for _ in nodes_ids)
        ids_list = list(nodes_ids)
        rows = store.conn.execute(
            f"SELECT * FROM edges WHERE src IN ({placeholders}) AND dst IN ({placeholders})",
            ids_list + ids_list,
        ).fetchall()

        edges = [
            {
                "src": r["src"],
                "dst": r["dst"],
                "type": r["type"],
            }
            for r in rows
        ]

        return {
            "center": {
                "id": node.id,
                "label": node.label,
                "type": node.type,
                "properties": node.properties,
            },
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "type": n.type,
                    "properties": n.properties,
                }
                for n in neighbors
            ],
            "edges": edges,
        }


def find_related(path: str, k: int = 5) -> list[dict]:
    config = get_config()
    with GraphStore(config.db_path) as store:
        file_rec = store.get_file(path)
        if file_rec is None:
            raise ValueError(f"File not found in index: {path}")

        neighbors = store.query_neighbors(file_rec.node_id, depth=2)
        related_files = []
        for n in neighbors:
            if n.type == "file" and n.id != file_rec.node_id:
                # Find path of this related file
                row = store.conn.execute(
                    "SELECT path FROM files WHERE node_id=?", (n.id,)
                ).fetchone()
                if row:
                    related_files.append({"file_id": n.id, "path": row["path"]})

        return related_files[:k]


def reindex(root: str | None = None) -> dict:
    config = get_config()
    roots_to_index = [Path(root)] if root else config.roots

    total_indexed = 0
    with GraphStore(config.db_path) as store:
        builder = GraphBuilder(store)
        kw = KeywordSearch(store.conn)

        for r in roots_to_index:
            r = r.resolve()
            entries = walk(r)
            for entry in entries:
                content = extract_file(entry.path)
                builder.build_from_file(entry, content, r)
                if content:
                    title = content.metadata.get("title", entry.path.name)
                    file_id = f"file:{entry.path.name}"
                    kw.index(file_id, str(entry.path), title, content.text)
                total_indexed += 1

        store.commit()
        stats = store.get_stats()

    return {
        "status": "success",
        "total_files_processed": total_indexed,
        "database_stats": stats,
    }
