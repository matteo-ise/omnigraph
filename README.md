# omnigraph

> Dein Mac als Knowledge Graph — alles indiziert, alles durchsuchbar, alles lokal.

<p align="center">
  <img src="https://img.shields.io/badge/Dark_Mode-only-14130F?style=flat-square" alt="Dark Mode"/>
  <img src="https://img.shields.io/badge/license-MIT-19C332?style=flat-square" alt="MIT"/>
  <img src="https://img.shields.io/badge/macOS-14%2B-000000?style=flat-square" alt="macOS"/>
  <img src="https://img.shields.io/badge/Python-3.11%2B-14130F?style=flat-square" alt="Python"/>
</p>

<!-- Screenshot -->

**Läuft 100% lokal und offline.** Keine Cloud, keine API-Keys, keine Telemetrie.

[![CI](https://github.com/matteoise/omnigraph/actions/workflows/ci.yml/badge.svg)](https://github.com/matteoise/omnigraph/actions/workflows/ci.yml)

---

## Was es macht

`omnigraph` crawlt konfigurierbare Roots auf deinem Mac (`~/Documents`, `~/Projects`, externe Festplatten), extrahiert Inhalte aus jedem Dateityp (Text, Markdown, PDF, DOCX, PPTX, XLSX, Code, IPYNB, EPUB, HTML, Bilder, Medien), baut einen SQLite-Knowledge-Graphen auf und bietet hybride Suche (BM25 Keyword + lokale Vektoren). Ein File-Watcher hält alles automatisch aktuell. Ein MCP-Server stellt 6 Tools bereit, damit jeder Coding-Agent (Claude Code, OpenCode, Codex) deinen gesamten Mac abfragen kann.

Inklusive **Interactive D3.js Web Graph Viewer** mit Zoom/Pan für visuelle Erkundung deines Wissens.

---

## Quick Start

```bash
pip install -e ".[dev]"

# Dateien indizieren
python -m omnigraph crawl --root ~/Documents

# Suchen
python -m omnigraph search "rechnung"

# Stats
python -m omnigraph stats

# Web UI (interaktiver D3-Graph)
python -m omnigraph serve --web --port 8765
# → http://localhost:8765 öffnen
```

---

## CLI Commands

| Befehl | Beschreibung |
|--------|-------------|
| `omnigraph crawl [--root X] [--watch] [--dry-run]` | Verzeichnisse crawlen und indizieren |
| `omnigraph search <query> [--limit 20] [--mode hybrid\|keyword\|semantic]` | Graph durchsuchen |
| `omnigraph show <path>` | Datei-Details + extrahierter Text |
| `omnigraph graph <node-id> [--depth 2]` | Lokale Nachbarschaft anzeigen |
| `omnigraph stats` | Datenbank-Statistiken |
| `omnigraph reindex [--root X]` | Manuelles Reindizieren |
| `omnigraph serve [--port 8765] [--web]` | MCP-Server oder Web UI starten |

---

## Vergleich

| Feature | omnigraph | macOS Spotlight | codebase-memory-mcp |
|---------|-----------|-----------------|---------------------|
| Hybride Suche (BM25 + Vektoren) | ✅ | ❌ | ❌ |
| Knowledge Graph | ✅ | ❌ | ❌ |
| Alle Dateitypen (PDF, EPUB, ...) | ✅ | Teilweise | ❌ |
| Code-Extraktion (AST-Chunking) | ✅ | ❌ | ✅ |
| MCP-Integration | ✅ | ❌ | ✅ |
| 100% lokal, keine Cloud | ✅ | ✅ | ✅ |
| Open Source | ✅ | ❌ | ✅ |

---

## Privacy

- **Keine Cloud** — alles läuft lokal auf deinem Mac
- **Keine Telemetrie** — kein Phone-Home, kein Tracking
- **Keine API-Keys** — keine Registrierung, keine Accounts
- **Open Source (MIT)** — du siehst genau was passiert
- Crawler **verweigert** System-Pfade (`/`, `/etc`, `/System`, `~/.ssh`, `~/.config`)
- DB unter `~/.omnigraph/` — FileVault + `.omniignore` für sensible Ordner

---

## MCP Integration

### OpenCode

In `~/.config/opencode/opencode.json` eintragen:

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

In `.mcp.json` eintragen:

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

1. **`search(query, k=10, mode="hybrid")`** — hybride Keyword + semantische Suche
2. **`get_file(path)`** — vollständiger Text + Metadaten einer indizierten Datei
3. **`list_projects()`** — alle indizierten Roots + Stats
4. **`graph_query(node_id, depth=2)`** — Subgraph-Nachbarschaft als JSON
5. **`find_related(path, k=5)`** — verwandte Dateien via SIMILAR_TO-Kanten
6. **`reindex(root=None)`** — vollständiges oder partielles Reindex triggern

---

## Architektur

```
omnigraph/
├── src/omnigraph/
│   ├── cli.py           # typer CLI
│   ├── config.py        # roots, ignores, blocked paths, embedding model
│   ├── crawler/         # ignore-aware walker (pathspec + os.scandir)
│   ├── extract/         # extractors per file type (inkl. AST-Chunking)
│   ├── graph/           # SQLite graph store + builder (mit SIMILAR_TO-Kanten)
│   ├── embed/           # sentence-transformers engine
│   ├── search/          # BM25 (FTS5) + vector (sqlite-vec) + hybrid reranker
│   ├── watch/           # watchdog file watcher mit debouncing
│   ├── mcp_server/      # FastMCP server + 6 Tools (Pydantic validiert)
│   ├── web/             # FastAPI + D3.js interaktiver Graph-Viewer
│   └── integration/     # cbm-mcp optionale Integration
├── tests/               # pytest
└── scripts/benchmark.py # indexing speed + search latency
```

**Datenfluss:**
```
Crawler → Extractor → Graph Builder → Embedder → SQLite (FTS5 + sqlite-vec)
    → Watcher (auto-update) → Search (hybrid) → MCP / CLI / Web UI
```

---

## Konfiguration

`~/.omnigraph/config.toml` bearbeiten oder Umgebungsvariablen setzen:

- **Roots:** `~/Documents`, `~/Projects` (via `config.toml` oder `OMNIGRAPH_ROOTS`)
- **Ignores:** `.omniignore` + `.gitignore`-Hierarchie + hardcodierte Patterns
- **Blocked Paths:** `/`, `/etc`, `/System`, `~/.ssh`, `~/.config` (nie gecrawlt)
- **Embedding-Modell:** `all-MiniLM-L6-v2` (90MB, nach erstem Run gecacht)
- **DB-Pfad:** `~/.omnigraph/omnigraph.db` (via `OMNIGRAPH_DB_PATH`)

---

## Unterstützte Dateitypen

| Typ | Endungen | Methode |
|-----|----------|---------|
| Text | `.txt`, `.md`, `.mdx`, `.rst`, `.org`, `.csv`, `.json`, `.yaml` | Direktes Lesen + Frontmatter |
| Web | `.html`, `.htm`, `.xhtml` | BeautifulSoup4 |
| Buch | `.epub` | EbookLib + BeautifulSoup4 |
| PDF | `.pdf` | pypdf + pdfplumber Fallback |
| Word | `.docx` | python-docx |
| PPTX | `.pptx`, `.ppt` | python-pptx |
| Excel | `.xlsx`, `.xls` | openpyxl |
| Code | `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.c`, `.cpp`, ... | AST-Chunking (Python) + Text + pygments |
| Notebook | `.ipynb` | nbformat |
| Bild | `.jpg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp` | EXIF via Pillow |
| Medien | `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wav`, `.mov` | ID3-Metadaten via mutagen |

---

## Benchmark

```bash
python scripts/benchmark.py tests/fixtures
```

Beispielausgabe:
```
=== Indexing ===
  files: 3
  crawl_time_s: 0.003
  index_time_s: 0.572
  total_time_s: 0.574
  files_per_sec: 5.2
  db_nodes: 6
  db_edges: 7

=== Search ===
  'test': 3 hits in 0.14ms
  'sample': 3 hits in 0.04ms
  'hello': 2 hits in 0.03ms
```

---

## Verwandt

- [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) — tiefes Code-Repo-Indexing. `omnigraph` kann Code-Subgraphen an cbm-mcp delegieren (`code_provider: cbm` in config).

---

## Lizenz

[MIT](LICENSE)

---

## Mehr von Matteo Ise

| Projekt | Beschreibung |
|---------|-------------|
| [**OpenLoom**](https://github.com/matteo-ise/open-loom) | Video aufnehmen + Meetings transkribieren |
| [**OpenLingo**](https://github.com/matteo-ise/open-lingo) | Lokales DeepL + Grammarly |
| [**Omnigraph**](https://github.com/matteo-ise/omnigraph) | Knowledge Graph über deinen Mac |

**Alle Apps:** Dark-Mode · Local-first · Privacy-first · Kostenlos · Open Source (MIT)