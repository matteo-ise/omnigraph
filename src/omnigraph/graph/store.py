from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from omnigraph.graph.models import Edge, FileRecord, Node, Project

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class GraphStore:
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self):
        schema = SCHEMA_PATH.read_text()
        self.conn.executescript(schema)
        self.conn.commit()

    def upsert_node(self, node: Node):
        self.conn.execute(
            """INSERT INTO nodes (id, label, type, properties)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 label=excluded.label,
                 type=excluded.type,
                 properties=excluded.properties""",
            (node.id, node.label, node.type, json.dumps(node.properties)),
        )

    def upsert_file(self, file: FileRecord):
        self.upsert_node(Node(id=file.node_id, label=file.path.name, type="file"))
        self.conn.execute(
            """INSERT INTO files (node_id, path, mtime, size, ext, sha256)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(node_id) DO UPDATE SET
                 path=excluded.path,
                 mtime=excluded.mtime,
                 size=excluded.size,
                 ext=excluded.ext,
                 sha256=excluded.sha256""",
            (
                file.node_id,
                str(file.path),
                file.mtime,
                file.size,
                file.ext,
                file.sha256,
            ),
        )

    def add_edge(self, edge: Edge):
        self.conn.execute(
            """INSERT OR IGNORE INTO edges (src, dst, type, properties)
               VALUES (?, ?, ?, ?)""",
            (edge.src, edge.dst, edge.type, json.dumps(edge.properties)),
        )

    def upsert_project(self, project: Project):
        self.conn.execute(
            """INSERT INTO projects (id, root, name)
               VALUES (?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 root=excluded.root,
                 name=excluded.name""",
            (project.id, str(project.root), project.name),
        )

    def get_node(self, node_id: str) -> Node | None:
        row = self.conn.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
        if row is None:
            return None
        return Node(
            id=row["id"],
            label=row["label"],
            type=row["type"],
            properties=json.loads(row["properties"]),
        )

    def get_file(self, path: Path | str) -> FileRecord | None:
        row = self.conn.execute("SELECT * FROM files WHERE path=?", (str(path),)).fetchone()
        if row is None:
            return None
        return FileRecord(
            node_id=row["node_id"],
            path=Path(row["path"]),
            mtime=row["mtime"],
            size=row["size"],
            ext=row["ext"],
            sha256=row["sha256"],
        )

    def query_neighbors(self, node_id: str, depth: int = 1) -> list[Node]:
        visited = {node_id}
        current = {node_id}
        for _ in range(depth):
            next_ids = set()
            for nid in current:
                rows = self.conn.execute(
                    "SELECT dst FROM edges WHERE src=? UNION SELECT src FROM edges WHERE dst=?",
                    (nid, nid),
                ).fetchall()
                for row in rows:
                    neighbor_id = row["dst"] if row["dst"] != nid else row["src"]
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        next_ids.add(neighbor_id)
            current = next_ids
            if not current:
                break

        neighbors = []
        for nid in visited - {node_id}:
            node = self.get_node(nid)
            if node:
                neighbors.append(node)
        return neighbors

    def delete_file(self, path: Path | str):
        file_rec = self.get_file(path)
        if file_rec is None:
            return
        nid = file_rec.node_id
        self.conn.execute("DELETE FROM edges WHERE src=? OR dst=?", (nid, nid))
        self.conn.execute("DELETE FROM files WHERE node_id=?", (nid,))
        self.conn.execute("DELETE FROM nodes WHERE id=?", (nid,))

    def delete_subtree(self, node_id: str):
        neighbors = self.query_neighbors(node_id, depth=10)
        ids_to_delete = {node_id} | {n.id for n in neighbors}
        for nid in ids_to_delete:
            self.conn.execute("DELETE FROM edges WHERE src=? OR dst=?", (nid, nid))
            self.conn.execute("DELETE FROM files WHERE node_id=?", (nid,))
            self.conn.execute("DELETE FROM nodes WHERE id=?", (nid,))

    def get_stats(self) -> dict:
        nodes = self.conn.execute("SELECT COUNT(*) as c FROM nodes").fetchone()["c"]
        edges = self.conn.execute("SELECT COUNT(*) as c FROM edges").fetchone()["c"]
        files = self.conn.execute("SELECT COUNT(*) as c FROM files").fetchone()["c"]
        projects = self.conn.execute("SELECT COUNT(*) as c FROM projects").fetchone()["c"]
        return {"nodes": nodes, "edges": edges, "files": files, "projects": projects}

    def list_projects(self) -> list[Project]:
        rows = self.conn.execute("SELECT * FROM projects").fetchall()
        return [Project(id=r["id"], root=Path(r["root"]), name=r["name"]) for r in rows]

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.commit()
        self.close()
