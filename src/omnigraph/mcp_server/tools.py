from __future__ import annotations

from pathlib import Path

from omnigraph.config import get_config
from omnigraph.crawler.walker import walk
from omnigraph.extract import extract_file
from omnigraph.graph.builder import GraphBuilder
from omnigraph.graph.store import GraphStore
from omnigraph.search.hybrid import hybrid_search
from omnigraph.search.keyword import KeywordSearch


from pydantic import BaseModel
from typing import Any

class SearchResultModel(BaseModel):
    file_id: str
    path: str
    score: float
    snippet: str
    provider: str

class FileDetailModel(BaseModel):
    node_id: str
    path: str
    size: int
    mtime: float
    ext: str
    text: str
    metadata: dict[str, Any]

class ProjectModel(BaseModel):
    id: str
    root: str
    name: str
    total_nodes_in_db: int
    total_edges_in_db: int

class GraphNodeModel(BaseModel):
    id: str
    label: str
    type: str
    properties: dict[str, Any]

class GraphEdgeModel(BaseModel):
    src: str
    dst: str
    type: str

class GraphQueryModel(BaseModel):
    center: GraphNodeModel
    nodes: list[GraphNodeModel]
    edges: list[GraphEdgeModel]

class RelatedFileModel(BaseModel):
    file_id: str
    path: str

class ErrorModel(BaseModel):
    error: str

def search(query: str, k: int = 10, mode: str = "hybrid") -> list[SearchResultModel] | ErrorModel:
    try:
        config = get_config()
        with GraphStore(config.db_path) as store:
            results = hybrid_search(store.conn, query, k=k, mode=mode)
            omnigraph_results = [
                SearchResultModel(
                    file_id=r.file_id,
                    path=r.path,
                    score=r.score,
                    snippet=r.snippet,
                    provider="omnigraph",
                )
                for r in results
            ]

        from omnigraph.integration import cbm_search, is_cbm_available, merge_results
        if is_cbm_available():
            cbm_results = cbm_search(query, k)
            merged = merge_results([r.model_dump() for r in omnigraph_results], cbm_results)
            return [SearchResultModel(**m) for m in merged]

        return omnigraph_results
    except Exception as e:
        return ErrorModel(error=str(e))


def get_file(path: str) -> FileDetailModel | ErrorModel:
    try:
        config = get_config()
        with GraphStore(config.db_path) as store:
            file_rec = store.get_file(path)
            if file_rec is None:
                return ErrorModel(error=f"File not found in index: {path}")

            extracted = extract_file(Path(path))
            return FileDetailModel(
                node_id=file_rec.node_id,
                path=str(file_rec.path),
                size=file_rec.size,
                mtime=file_rec.mtime,
                ext=file_rec.ext,
                text=extracted.text if extracted else "",
                metadata=extracted.metadata if extracted else {},
            )
    except Exception as e:
        return ErrorModel(error=str(e))


def list_projects() -> list[ProjectModel] | ErrorModel:
    try:
        config = get_config()
        with GraphStore(config.db_path) as store:
            projects = store.list_projects()
            stats = store.get_stats()
            return [
                ProjectModel(
                    id=p.id,
                    root=str(p.root),
                    name=p.name,
                    total_nodes_in_db=stats["nodes"],
                    total_edges_in_db=stats["edges"],
                )
                for p in projects
            ]
    except Exception as e:
        return ErrorModel(error=str(e))


def graph_query(node_id: str, depth: int = 2) -> GraphQueryModel | ErrorModel:
    try:
        config = get_config()
        with GraphStore(config.db_path) as store:
            node = store.get_node(node_id)
            if node is None:
                return ErrorModel(error=f"Node not found: {node_id}")

            neighbors = store.query_neighbors(node_id, depth=depth)

            nodes_ids = {node_id} | {n.id for n in neighbors}
            placeholders = ",".join("?" for _ in nodes_ids)
            ids_list = list(nodes_ids)
            rows = store.conn.execute(
                f"SELECT * FROM edges WHERE src IN ({placeholders}) AND dst IN ({placeholders})",
                ids_list + ids_list,
            ).fetchall()

            edges = [GraphEdgeModel(src=r["src"], dst=r["dst"], type=r["type"]) for r in rows]

            return GraphQueryModel(
                center=GraphNodeModel(id=node.id, label=node.label, type=node.type, properties=node.properties),
                nodes=[GraphNodeModel(id=n.id, label=n.label, type=n.type, properties=n.properties) for n in neighbors],
                edges=edges,
            )
    except Exception as e:
        return ErrorModel(error=str(e))


def find_related(path: str, k: int = 5) -> list[RelatedFileModel] | ErrorModel:
    try:
        config = get_config()
        with GraphStore(config.db_path) as store:
            file_rec = store.get_file(path)
            if file_rec is None:
                return ErrorModel(error=f"File not found in index: {path}")

            neighbors = store.query_neighbors(file_rec.node_id, depth=2)
            related_files = []
            for n in neighbors:
                if n.type == "file" and n.id != file_rec.node_id:
                    row = store.conn.execute("SELECT path FROM files WHERE node_id=?", (n.id,)).fetchone()
                    if row:
                        related_files.append(RelatedFileModel(file_id=n.id, path=row["path"]))

            return related_files[:k]
    except Exception as e:
        return ErrorModel(error=str(e))


class ReindexModel(BaseModel):
    status: str
    total_files_processed: int
    database_stats: dict[str, int]

def reindex(root: str | None = None) -> ReindexModel | ErrorModel:
    try:
        config = get_config()
        roots_to_index = [Path(root)] if root else config.roots

        total_indexed = 0
        with GraphStore(config.db_path) as store:
            builder = GraphBuilder(store)
            kw = KeywordSearch(store.conn)

            from omnigraph.embed.engine import Embedder
            from omnigraph.search.semantic import SemanticSearch
            embedder = Embedder()
            semantic = SemanticSearch(store.conn, dimension=embedder.dimension)

            for r in roots_to_index:
                r = r.resolve()
                entries = walk(r)
                for entry in entries:
                    content = extract_file(entry.path)
                    node_id = builder.build_from_file(entry, content, r)
                    if content:
                        title = content.metadata.get("title", entry.path.name)
                        file_id = node_id
                        kw.index(file_id, str(entry.path), title, content.text)
                        
                        semantic.delete(file_id)
                        chunks = content.chunks if content.chunks else embedder.chunk_text(content.text)
                        if chunks:
                            embeddings = embedder.encode(chunks)
                            for i, emb in enumerate(embeddings):
                                semantic.index(f"{file_id}:chunk{i}", emb)

                            for emb in embeddings:
                                results = semantic.search(emb, k=3)
                                for res in results:
                                    other_id = res.file_id.split(":")[0] + ":" + res.file_id.split(":")[1]
                                    if other_id != file_id and res.score > 0.8:
                                        from omnigraph.graph.models import Edge
                                        store.add_edge(Edge(src=file_id, dst=other_id, type="SIMILAR_TO", properties={"score": res.score}))
                                        store.add_edge(Edge(src=other_id, dst=file_id, type="SIMILAR_TO", properties={"score": res.score}))

                    total_indexed += 1

            store.commit()
            stats = store.get_stats()

        return ReindexModel(
            status="success",
            total_files_processed=total_indexed,
            database_stats=stats,
        )
    except Exception as e:
        return ErrorModel(error=str(e))
