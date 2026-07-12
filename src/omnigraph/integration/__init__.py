from __future__ import annotations

import shutil
import subprocess

from omnigraph.config import get_config


def is_cbm_available() -> bool:
    config = get_config()
    return config.code_provider == "cbm" and shutil.which("codebase-memory-mcp") is not None


def cbm_search(query: str, k: int = 10) -> list[dict]:
    if not is_cbm_available():
        return []
    try:
        result = subprocess.run(
            ["codebase-memory-mcp", "search", query, "--limit", str(k)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            return []
        import json

        return json.loads(result.stdout) if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, ValueError, OSError):
        return []


def merge_results(omnigraph_results: list[dict], cbm_results: list[dict]) -> list[dict]:
    seen = {r.get("path") for r in omnigraph_results if r.get("path")}
    merged = list(omnigraph_results)
    for r in cbm_results:
        path = r.get("path")
        if path and path not in seen:
            r["provider"] = "cbm"
            merged.append(r)
    return merged
