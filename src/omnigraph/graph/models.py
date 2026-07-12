from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Node:
    id: str
    label: str
    type: str
    properties: dict = field(default_factory=dict)


@dataclass
class Edge:
    src: str
    dst: str
    type: str
    properties: dict = field(default_factory=dict)


@dataclass
class FileRecord:
    node_id: str
    path: Path
    mtime: float
    size: int
    ext: str
    sha256: str | None = None


@dataclass
class Project:
    id: str
    root: Path
    name: str
