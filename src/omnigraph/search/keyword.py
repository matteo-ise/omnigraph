from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class SearchResult:
    file_id: str
    path: str
    score: float
    snippet: str = ""


class KeywordSearch:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._init_fts()

    def _init_fts(self):
        self.conn.execute(
            """CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
               USING fts5(path, title, text, tokenize='porter')"""
        )

    def index(self, file_id: str, path: str, title: str, text: str):
        rowid = hash(file_id) & 0x7FFFFFFF
        self.conn.execute("DELETE FROM files_fts WHERE rowid=?", (rowid,))
        self.conn.execute(
            "INSERT INTO files_fts(rowid, path, title, text) VALUES (?, ?, ?, ?)",
            (rowid, path, title, text),
        )

    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        rows = self.conn.execute(
            """SELECT path, snippet(files_fts, 2, '<b>', '</b>', '...', 64) as snip,
                      rank
               FROM files_fts
               WHERE files_fts MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (query, k),
        ).fetchall()
        return [
            SearchResult(file_id="", path=r["path"], score=-r["rank"], snippet=r["snip"])
            for r in rows
        ]

    def delete(self, file_id: str):
        rowid = hash(file_id) & 0x7FFFFFFF
        self.conn.execute("DELETE FROM files_fts WHERE rowid=?", (rowid,))
