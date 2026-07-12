from __future__ import annotations

import sqlite3
from dataclasses import dataclass

import sqlite_vec


@dataclass
class VectorResult:
    file_id: str
    score: float


class SemanticSearch:
    def __init__(self, conn: sqlite3.Connection, dimension: int = 384):
        self.conn = conn
        self.dimension = dimension
        self._init_vec()

    def _init_vec(self):
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self.conn.execute(
            f"""CREATE VIRTUAL TABLE IF NOT EXISTS files_vec
               USING vec0(file_id TEXT PRIMARY KEY, embedding float[{self.dimension}])"""
        )

    def index(self, file_id: str, embedding: bytes):
        self.conn.execute(
            """INSERT INTO files_vec(file_id, embedding)
               VALUES (?, ?)
               ON CONFLICT(file_id) DO UPDATE SET embedding=excluded.embedding""",
            (file_id, embedding),
        )

    def search(self, query_embedding: bytes, k: int = 10) -> list[VectorResult]:
        rows = self.conn.execute(
            """SELECT file_id, distance
               FROM files_vec
               WHERE embedding MATCH ?
               ORDER BY distance
               LIMIT ?""",
            (query_embedding, k),
        ).fetchall()
        return [VectorResult(file_id=r["file_id"], score=1.0 - r["distance"]) for r in rows]

    def delete(self, file_id: str):
        self.conn.execute("DELETE FROM files_vec WHERE file_id=?", (file_id,))
