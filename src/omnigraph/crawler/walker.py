from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from omnigraph.config import get_config
from omnigraph.crawler.ignores import IgnoreStack


@dataclass
class FileEntry:
    path: Path
    size: int
    mtime: float
    ext: str


def walk(
    root: Path | str,
    max_depth: int | None = None,
    extra_ignores: list[str] | None = None,
) -> list[FileEntry]:
    root = Path(root).resolve()
    config = get_config()
    if max_depth is None:
        max_depth = config.max_depth

    root_str = str(root)
    for blocked in config.blocked_paths:
        if root_str == blocked:
            raise ValueError(f"Refusing to crawl blocked path: {root}")
        if blocked != "/" and root_str.startswith(blocked.rstrip("/") + "/"):
            raise ValueError(f"Refusing to crawl blocked path: {root}")

    ignores = IgnoreStack(root, extra_patterns=extra_ignores or config.ignore_patterns)
    entries = []
    _walk_recursive(root, root, ignores, max_depth, 0, entries)
    return entries


def _walk_recursive(
    base: Path,
    current: Path,
    ignores: IgnoreStack,
    max_depth: int,
    depth: int,
    entries: list[FileEntry],
):
    if depth > max_depth:
        return
    try:
        with os.scandir(current) as it:
            for entry in it:
                try:
                    path = Path(entry.path).resolve()
                except (OSError, ValueError):
                    continue

                if entry.is_symlink():
                    continue

                if ignores.is_ignored(path):
                    continue

                if entry.is_dir(follow_symlinks=False):
                    _walk_recursive(base, path, ignores, max_depth, depth + 1, entries)
                elif entry.is_file(follow_symlinks=False):
                    try:
                        stat = entry.stat(follow_symlinks=False)
                        entries.append(
                            FileEntry(
                                path=path,
                                size=stat.st_size,
                                mtime=stat.st_mtime,
                                ext=path.suffix.lower(),
                            )
                        )
                    except OSError:
                        continue
    except PermissionError:
        return
