from __future__ import annotations

from pathlib import Path

import pathspec


class IgnoreStack:
    def __init__(self, root: Path, extra_patterns: list[str] | None = None):
        self.root = root.resolve()
        patterns = list(extra_patterns or [])
        patterns.extend(self._load_gitignore_hierarchy(self.root))
        patterns.extend(self._load_omniignore(self.root))
        self.spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    def is_ignored(self, path: Path) -> bool:
        try:
            rel = path.resolve().relative_to(self.root)
        except ValueError:
            return True
        return self.spec.match_file(str(rel))

    def _load_gitignore_hierarchy(self, root: Path) -> list[str]:
        patterns = []
        for gitignore in root.rglob(".gitignore"):
            try:
                rel_dir = gitignore.parent.relative_to(root)
            except ValueError:
                continue
            for line in gitignore.read_text(errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                prefix = str(rel_dir) if str(rel_dir) != "." else ""
                if prefix:
                    patterns.append(f"{prefix}/{line}")
                else:
                    patterns.append(line)
        return patterns

    def _load_omniignore(self, root: Path) -> list[str]:
        omniignore = root / ".omniignore"
        if not omniignore.exists():
            return []
        return [
            line.strip()
            for line in omniignore.read_text(errors="ignore").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
