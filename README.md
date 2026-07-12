# omnigraph

> Local knowledge graph across all your drives — auto-indexing, hybrid search, MCP-integrated. Everything findable, nothing leaves your machine.

[![CI](https://github.com/YOUR/omnigraph/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR/omnigraph/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What it does

`omnigraph` crawls configurable roots on your computer (`~/Documents`, `~/Projects`, external drives), extracts content from every file type (text, Markdown, PDF, DOCX, XLSX, code, images, media), builds a SQLite knowledge graph, and provides hybrid search (BM25 keyword + local vector embeddings). A file watcher keeps everything up to date automatically. An MCP server exposes 6 tools so any coding agent (Claude Code, OpenCode, Codex) can query your entire machine.

**Everything stays local.** No cloud, no API keys, no telemetry.

## Quick Start

```bash
pip install -e ".[dev]"

# Index your fixtures
python -m omnigraph crawl --root tests/fixtures

# Search
python -m omnigraph search "invoice"

# Stats
python -m omnigraph stats

# Web UI (D3 graph viewer)
python -m omnigraph serve --web --port 8765
# → open http://localhost:8765
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `omnigraph crawl [--root X] [--watch] [--dry-run]` | Crawl and index directories |
| `omnigraph search <query> [--limit 20] [--mode hybrid\|keyword\|semantic]` | Search the graph |
| `omnigraph show <path>` | Show file details + extracted text |
| `omnigraph graph <node-id> [--depth 2]` | Show local neighborhood |
| `omnigraph stats` | Database statistics |
| `omnigraph reindex [--root X]` | Manual reindex |
| `omnigraph serve [--port 8765] [--web]` | Start MCP server or Web UI |

## MCP Integration

### OpenCode

Add to `~/.config/opencode/opencode.json`:

```json
{
  "mcpServers": {
    "omnigraph": {
      "command": "python",
      "args": ["-m", "omnigraph", "serve"]
    }
  }
}
```

### Claude Code

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "omnigraph": {
      "command": "python",
      "args": ["-m", "omnigraph", "serve"]
    }
  }
}
```

### 6 MCP Tools

1. **`search(query, k=10, mode="hybrid")`** — hybrid keyword + semantic search
2. **`get_file(path)`** — full text + metadata of an indexed file
3. **`list_projects()`** — all indexed roots + stats
4. **`graph_query(node_id, depth=2)`** — subgraph neighborhood as JSON
5. **`find_related(path, k=5)`** — related files via shared tags/topics/folders
6. **`reindex(root=None)`** — trigger full or partial reindex

## Architecture

```
omnigraph/
├── src/omnigraph/
│   ├── cli.py           # typer CLI
│   ├── config.py        # roots, ignores, blocked paths, embedding model
│   ├── crawler/         # ignore-aware walker (pathspec + os.scandir)
│   ├── extract/         # extractors per file type
│   ├── graph/           # SQLite graph store + builder
│   ├── embed/           # sentence-transformers engine
│   ├── search/          # BM25 (FTS5) + vector (sqlite-vec) + hybrid reranker
│   ├── watch/           # watchdog file watcher with debouncing
│   ├── mcp_server/      # FastMCP server + 6 tools
│   ├── web/             # FastAPI + D3.js graph viewer
│   └── integration/     # cbm-mcp optional integration
├── tests/               # pytest (31 tests)
└── scripts/benchmark.py # indexing speed + search latency
```

**Data flow:**
```
Crawler → Extractor → Graph Builder → Embedder → SQLite (FTS5 + sqlite-vec)
    → Watcher (auto-update) → Search (hybrid) → MCP / CLI / Web UI
```

## Configuration

Edit `~/.omnigraph/config` or set environment variables. Key options:

- **Roots:** `~/Documents`, `~/Projects` (configurable in `config.py`)
- **Ignores:** `.omniignore` + `.gitignore` hierarchy + hardcoded patterns
- **Blocked paths:** `/`, `/etc`, `/System`, `~/.ssh`, `~/.config` (never crawled)
- **Embedding model:** `all-MiniLM-L6-v2` (90MB, cached after first run)
- **DB path:** `~/.omnigraph/omnigraph.db`

## Supported File Types

| Type | Extensions | Method |
|------|-----------|--------|
| Text | `.txt`, `.md`, `.mdx`, `.rst`, `.org`, `.csv`, `.json`, `.yaml` | Direct read + frontmatter |
| PDF | `.pdf` | pypdf + pdfplumber fallback |
| DOCX | `.docx` | python-docx |
| XLSX | `.xlsx`, `.xls` | openpyxl |
| Code | `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.c`, `.cpp`, ... | Text chunking + pygments language detection |
| Image | `.jpg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp` | EXIF via Pillow |
| Media | `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wav`, `.mov` | ID3 metadata via mutagen |

## Privacy & Security

- Everything local. No cloud calls, no API keys, no telemetry.
- Crawler **refuses** to crawl system paths (`/`, `/etc`, `/System`, `~/.ssh`, `~/.config`).
- No `os.system` or `subprocess` with unsanitized input.
- Only HuggingFace model download + PyPI installs (both official).
- DB stored under `~/.omnigraph/` — use FileVault + `.omniignore` for sensitive folders.

## Benchmark

```bash
python scripts/benchmark.py tests/fixtures
```

Sample output:
```
=== Indexing ===
  files: 3
  index_time_s: 0.05
  files_per_sec: 60.0

=== Search ===
  'invoice': 1 hits in 0.3ms
```

## Related

- [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) — deep code repo indexing. `omnigraph` can delegate code subgraphs to cbm-mcp (`code_provider: cbm` in config).

## License

[MIT](LICENSE)