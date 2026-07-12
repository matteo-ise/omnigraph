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
        import os
        import tomllib
        from pathlib import Path

        config_path = Path.home() / ".omnigraph" / "config.toml"
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    toml_data = tomllib.load(f)
                
                if "roots" in toml_data:
                    _config.roots = [Path(r).expanduser() for r in toml_data["roots"]]
                if "db_path" in toml_data:
                    _config.db_path = Path(toml_data["db_path"]).expanduser()
                if "ignore_patterns" in toml_data:
                    _config.ignore_patterns = toml_data["ignore_patterns"]
                if "max_depth" in toml_data:
                    _config.max_depth = int(toml_data["max_depth"])
                if "embedding_model" in toml_data:
                    _config.embedding_model = toml_data["embedding_model"]
                if "code_provider" in toml_data:
                    _config.code_provider = toml_data["code_provider"]
            except Exception as e:
                print(f"Failed to load config.toml: {e}")
                
        if "OMNIGRAPH_ROOTS" in os.environ:
            _config.roots = [Path(r.strip()).expanduser() for r in os.environ["OMNIGRAPH_ROOTS"].split(",")]
        if "OMNIGRAPH_DB_PATH" in os.environ:
            _config.db_path = Path(os.environ["OMNIGRAPH_DB_PATH"]).expanduser()
            
    return _config
