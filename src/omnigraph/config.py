from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    db_path: Path = field(default_factory=lambda: Path.home() / ".omnigraph" / "omnigraph.db")
    roots: list[Path] = field(
        default_factory=lambda: [
            Path.home() / "Documents",
            Path.home() / "Projects",
        ]
    )
    ignore_patterns: list[str] = field(
        default_factory=lambda: [
            ".git",
            "node_modules",
            ".venv",
            "__pycache__",
            ".DS_Store",
            ".omnigraph",
            "*.pyc",
            ".ruff_cache",
            ".pytest_cache",
            ".mypy_cache",
            "*.egg-info",
            "dist",
            "build",
        ]
    )
    max_depth: int = 20
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 64
    hybrid_weight_keyword: float = 0.5
    hybrid_weight_semantic: float = 0.5
    code_provider: str | None = None
    blocked_paths: list[str] = field(
        default_factory=lambda: [
            "/",
            "/etc",
            "/System",
            "/usr",
            "/bin",
            "/sbin",
            "/private/etc",
            "/private/var/root",
            os.path.expanduser("~/.ssh"),
            os.path.expanduser("~/.config"),
            os.path.expanduser("~/.gnupg"),
            os.path.expanduser("~/.aws"),
            os.path.expanduser("~/.kube"),
        ]
    )

    def ensure_db_dir(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config
