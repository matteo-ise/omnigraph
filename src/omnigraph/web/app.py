from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from omnigraph.config import get_config
from omnigraph.graph.store import GraphStore
from omnigraph.search.hybrid import hybrid_search

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="omnigraph web", version="0.1.0")

    @app.get("/api/search", response_class=JSONResponse)
    def api_search(q: str, k: int = 20, mode: str = "keyword"):
        config = get_config()
        with GraphStore(config.db_path) as store:
            results = hybrid_search(store.conn, q, k=k, mode=mode)
            return [
                {
                    "file_id": r.file_id,
                    "path": r.path,
                    "score": r.score,
                    "snippet": r.snippet,
                }
                for r in results
            ]

    @app.get("/api/file/{file_id}", response_class=JSONResponse)
    def api_file(file_id: str):
        from omnigraph.extract import extract_file

        config = get_config()
        with GraphStore(config.db_path) as store:
            node = store.get_node(file_id)
            if node is None:
                return {"error": "not found"}
            row = store.conn.execute("SELECT * FROM files WHERE node_id=?", (file_id,)).fetchone()
            if row is None:
                return {"error": "no file record"}
            path = row["path"]
            content = extract_file(Path(path))
            return {
                "node_id": file_id,
                "path": path,
                "metadata": content.metadata if content else {},
                "text": content.text[:2000] if content else "",
            }

    @app.get("/api/graph/{node_id}", response_class=JSONResponse)
    def api_graph(node_id: str, depth: int = 2):

        config = get_config()
        with GraphStore(config.db_path) as store:
            node = store.get_node(node_id)
            if node is None:
                return {"error": "not found"}

            neighbors = store.query_neighbors(node_id, depth=depth)
            nodes_ids = {node_id} | {n.id for n in neighbors}
            ids_list = list(nodes_ids)
            placeholders = ",".join("?" for _ in ids_list)
            rows = store.conn.execute(
                f"SELECT * FROM edges WHERE src IN ({placeholders}) AND dst IN ({placeholders})",
                ids_list + ids_list,
            ).fetchall()

            return {
                "nodes": [
                    {
                        "id": node.id,
                        "label": node.label,
                        "type": node.type,
                    }
                ]
                + [
                    {
                        "id": n.id,
                        "label": n.label,
                        "type": n.type,
                    }
                    for n in neighbors
                ],
                "links": [
                    {"source": r["src"], "target": r["dst"], "type": r["type"]} for r in rows
                ],
            }

    @app.get("/api/stats", response_class=JSONResponse)
    def api_stats():
        config = get_config()
        with GraphStore(config.db_path) as store:
            return store.get_stats()

    @app.get("/", response_class=HTMLResponse)
    def index():
        html_path = STATIC_DIR / "index.html"
        return HTMLResponse(html_path.read_text())

    return app
