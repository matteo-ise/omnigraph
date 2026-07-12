# AGENTS.md — omnigraph (opencode-Kontext)

## Projekt
Lokaler Desktop-Knowledge-Graph: crawlt alle Drives, extrahiert Content (Text/PDF/DOCX/XLSX/Code/Bilder/Medien), baut SQLite-Graph, hybride Suche (BM25 + Vektoren), File-Watcher-Auto-Update, MCP-Server mit 6 Tools. Siehe `BLUEPRINT.md` für den Phasen-Plan.

## Befehle
- Tests: `pytest tests/ -q`
- Lint: `ruff check src/`
- Format prüfen: `ruff format --check src/`
- Smoke (nach Phase 5): `python -m omnigraph crawl --root tests/fixtures && python -m omnigraph search "invoice" && python -m omnigraph stats`
- MCP-Check (nach Phase 6): `python -m omnigraph serve` → `/mcp` zeigt 6 Tools
- CLI: `python -m omnigraph --help`

## Konventionen
- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Keine DBs / Embedding-Modelle / indizierte Binärdateien committen (siehe `.gitignore`).
- Python 3.11+, Deps in `pyproject.toml`.
- Eine Phase aus `BLUEPRINT.md` pro logischem Commit-Bereich; nach jeder Phase verifizieren (pytest + ruff).

## Stack
Python · SQLite (FTS5 + sqlite-vec) · pathspec · watchdog · pypdf/pdfplumber · python-docx · openpyxl · Pillow · sentence-transformers/mlx-embeddings · FastMCP · FastAPI · typer/rich
