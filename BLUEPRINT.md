# omnigraph — Bauplan

> Lokaler Knowledge Graph über deinen ganzen Computer. Indiziert Dateien über alle Drives hinweg (Dokumente, Markdown, PDFs, Code, Notizen, Office), modelliert Beziehungen, aktualisiert sich selbst per File-Watcher und beantwortet Suchanfragen in Millisekunden — hybrid aus Keyword- (BM25) und Semantik-Suche (lokale Embeddings). MCP-integriert, damit jeder Coding-Agent (Claude Code, OpenCode, Codex) deinen Computer befragen kann.

---

## 1. Kontext-Brief (für frischen Agent, kalt startbar)

**Was das Projekt ist:** Ein lokaler Desktop-Knowledge-Graph. Anders als [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) (das nur Code-Repos indiziert und production-ready ist), deckt `omnigraph` **alle Dateitypen über alle Drives** ab: Dokumente, PDFs, Markdown, Notizen, Office-Dateien, Code, Bilder-Metadaten. Es baut einen Graphen (Datei → Projekt → Thema → Tag → Link) und bietet schnelle hybride Suche + einen MCP-Server, den Coding-Agenten abfragen können.

**Warum es existiert:** Du willst, dass alles auf deinem Computer schnell findbar ist — über alle Laufwerke, automatisch aktuell, ohne Cloud. Spotlight/mdfind ist schnell aber flach (keine Semantik, kein Graph, keine Agent-Schnittstelle). cbm-mcp ist tief, aber nur Code. `omnigraph` schliesst die Lücke: desktop-weit, semantisch, graph-basiert, MCP-ready.

**Beziehung zu cbm-mcp:** Nicht konkurrenzierend — ergänzend. `omnigraph` kann cbm-mcp für Code-Dateien einbinden (delegierter Code-Subgraph) und selbst den Rest (Dokumente, PDFs, Notizen, Office) übernehmen. Siehe Phase 6 (Integration).

**Lizenz:** MIT.

---

## 2. Ziele & Non-Goals

**Ziele**
- Desktop-weites Crawlen konfigurierbarer Roots (z.B. `~/Documents`, `~/Projects`, externe Drives) mit Ignore-Regeln (`.omniignore`, `.gitignore`-Hierarchie).
- Content-Extraktion pro Dateityp: Text/MD (direkt), PDF (`pypdf`/`pdfplumber`), DOCX (`python-docx`), XLSX (`openpyxl`), Code (Lightweight-Tree-Sitter oder reines Text-Chunking v1), Bilder (EXIF/Metadaten via `Pillow`), Audio/Video (ID3-Metadaten).
- Graph-Modell: `File`, `Project`, `Folder`, `Topic`, `Tag`, `Link`, `Mention`. Kanten: `CONTAINS`, `TAGGED`, `MENTIONS`, `LINKS_TO`, `PART_OF_PROJECT`, `SIMILAR_TO`.
- Hybride Suche: BM25 (SQLite FTS5) + Vektor-Semantik (lokale Embeddings, `sentence-transformers` oder `mlx-embeddings`).
- Auto-Update via File-Watcher (`watchdog`) — inkrementelle Re-Indizierung bei Änderung.
- MCP-Server-Schnittstelle: 6+ Tools (`search`, `get_file`, `list_projects`, `graph_query`, `find_related`, `reindex`).
- CLI (`omnigraph crawl`, `search`, `graph`, `serve`) + minimales Web-UI (FastAPI) zum Browsen.
- Alles lokal, keine Cloud, keine API-Keys.

**Non-Goals (v1)**
- Vollständige Code-Semantik (überlasse cbm-mcp; v1 behandelt Code als Text + Metadaten).
- OCR für gescannte PDFs/Bilder (v1.1 via `tesseract` oder Apple Vision).
- Cloud-Sync / Multi-Device.
- GUI-Desktop-App (v1 = CLI + Web-UI; native App v2).
- Vollständige Graph-Visualisierung à la Neo4j-Bloom (v1 = einfache Web-Graph-Ansicht).

---

## 3. Tech-Stack

| Schicht | Wahl | Begründung |
|--------|------|-----------|
| Sprache | Python 3.11+ | miniconda3 vorhanden; reiche Libs für Datei-Parsing + Vektoren |
| Storage | SQLite (FTS5) + `sqlite-vec` (Vektoren) oder `lancedb` | Eine lokale Datei, robust, FTS5 built-in |
| Crawler | `pathspec` (gitignore-Parser) + `os.scandir`-Walker | performant, ignore-aware |
| File-Watcher | `watchdog` | Standard für plattformübergreifendes FS-Monitoring |
| PDF | `pypdf` (Text) + `pdfplumber` (Tabellen/Fallback) | reif, gratis |
| DOCX | `python-docx` | Standard |
| XLSX | `openpyxl` | Standard |
| Code-Parsing | v1: reines Text-Chunking + `pygments`-Spracherkennung; v1.1: Tree-Sitter | Keep it simple für v1 |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) oder `mlx-embeddings` auf Apple Silicon | lokal, klein, schnell |
| MCP-Server | `mcp` Python SDK (FastMCP) | offiziell, stdio + HTTP |
| CLI | `typer` + `rich` | konsistent mit voicemeet-pro |
| Web-UI | `fastapi` + `uvicorn` + minimales HTML/JS (D3-Graph) | leichtgewichtig |
| Tests | `pytest` | Standard |

**System-Voraussetzungen:**
- macOS (Apple Silicon empfohlen für MLX-Embeddings; Intel geht mit sentence-transformers).
- Python 3.11+.
- Für Code-Subgraph (optional, Phase 6): `codebase-memory-mcp` installiert.

---

## 4. Architektur

```
omnigraph/
├── README.md
├── BLUEPRINT.md            (diese Datei)
├── AGENTS.md               (opencode-Kontext)
├── pyproject.toml
├── .gitignore
├── src/omnigraph/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              (typer: crawl, search, graph, serve, reindex)
│   ├── config.py           (Roots, Ignores, Modell-Pfade)
│   ├── crawler/
│   │   ├── walker.py       (ignore-aware Verzeichnis-Walk)
│   │   └── ignores.py      (.omniignore + .gitignore-Hierarchie via pathspec)
│   ├── extract/
│   │   ├── base.py         (Extractor-Interface)
│   │   ├── text.py         (.txt, .md, .mdx, .rst, .org)
│   │   ├── pdf.py          (pypdf + pdfplumber)
│   │   ├── docx.py
│   │   ├── xlsx.py
│   │   ├── code.py         (Text-Chunking + pygments-Sprache)
│   │   ├── image.py        (EXIF via Pillow)
│   │   ├── media.py        (ID3/Metadaten via mutagen)
│   │   └── registry.py     (Dateityp → Extractor-Map)
│   ├── graph/
│   │   ├── models.py       (Node/Edge-Dataclasses)
│   │   ├── store.py        (SQLite-Graph-CRUD)
│   │   ├── schema.sql      (Tabellen: nodes, edges, files, embeddings)
│   │   └── builder.py      (rohe Datei-Metadaten → Graph-Knoten/-Kanten)
│   ├── search/
│   │   ├── keyword.py      (BM25 via FTS5)
│   │   ├── semantic.py     (Vektor-Suche via sqlite-vec/lancedb)
│   │   └── hybrid.py       (Rekombination + Reranking)
│   ├── embed/
│   │   └── engine.py       (mlx-embeddings ODER sentence-transformers, Chunking)
│   ├── watch/
│   │   └── watcher.py      (watchdog → inkrementelle Re-Indexierung)
│   ├── mcp_server/
│   │   ├── server.py       (FastMCP: 6+ Tools)
│   │   └── tools.py        (search, get_file, list_projects, graph_query, find_related, reindex)
│   └── web/
│       ├── app.py          (FastAPI: /search, /graph, /file/<id>)
│       └── static/         (minimal D3-Graph-Viewer)
├── tests/
│   ├── test_crawler.py
│   ├── test_extract.py     (Dummy-Dateien je Typ)
│   ├── test_graph.py
│   ├── test_search.py
│   └── test_mcp.py
└── scripts/
    └── benchmark.py        (Indizier-Geschw. über Sample-Verzeichnis)
```

**Datenfluss:**
```
Crawler (Roots + Ignores) → Extractor pro Dateityp → (Text + Metadaten)
    → Graph-Builder (File/Project/Folder/Topic-Knoten + Kanten)
    → Embedder (Chunking → Vektoren) → SQLite (FTS5 + sqlite-vec)
    → Watcher (Datei-Events → inkrementell: Extract → Update Graph + Vektor)
    → Such-Interface: Hybrid(BM25 + Vektor) → Reranking → Ergebnis
    → MCP-Server / CLI / Web-UI konsumieren
```

---

## 5. Implementierungs-Phasen (je eigener Commit-Bereich)

### Phase 0 — Projekt-Gerüst (Commit: `chore: scaffold project + deps`)
- `pyproject.toml`: typer, rich, pathspec, watchdog, pypdf, pdfplumber, python-docx, openpyxl, pillow, mutagen, pygments, sentence-transformers, sqlite-vec (oder lancedb), mcp (FastMCP), fastapi, uvicorn, pytest, ruff.
- `src/omnigraph/__init__.py`, `__main__.py`, `cli.py` (Stub: `omnigraph --version`).
- `config.py`: Default-Roots (`~/Documents`, `~/Projects`), Ignore-Patterns, DB-Pfad `~/.omnigraph/omnigraph.db`.
- `.gitignore`, `README.md` (Skeleton), `AGENTS.md`.
- **Verifikation:** `python -m omnigraph --version` läuft.

### Phase 1 — Crawler + Ignores (Commit: `feat: ignore-aware filesystem crawler`)
- `crawler/ignores.py`: `IgnoreStack` — kombiniert `.omniignore` (projekt-spezifisch) + `.gitignore`-Hierarchie via `pathspec.PathSpec`. Hardcoded Patterns: `.git`, `node_modules`, `.venv`, `__pycache__`, `.DS_Store`.
- `crawler/walker.py`: `walk(root)` → Generator von `FileEntry(path, size, mtime, ext)`. Respektiert Ignores, folgt keinen Symlinks (Default), konfigurierbare Max-Tiefe.
- `tests/test_crawler.py`: Temp-Verzeichnis mit gemischten Dateien + `.gitignore` → prüft gefilterte Menge.
- **Verifikation:** `pytest tests/test_crawler.py` grün; `omnigraph crawl --root ~/Documents --dry-run` listet gefilterte Dateien.

### Phase 2 — Extractors (Commit: `feat: content extractors for text pdf docx xlsx code image media`)
- `extract/base.py`: `Extractor.extract(path) -> ExtractedContent(text, metadata, chunks)`.
- `extract/text.py`, `pdf.py`, `docx.py`, `xlsx.py`, `code.py` (pygments-Sprache + Chunking nach Zeilen/Funktion-Heuristik), `image.py` (EXIF), `media.py` (mutagen).
- `extract/registry.py`: Map `ext → Extractor`, Fallback `text.py` für Unbekanntes (mit Encoding-Detect `chardet`/`charset-normalizer`).
- `tests/test_extract.py`: Für jeden Typ eine kleine Dummy-Datei im `tests/fixtures/` → prüft nicht-leerer Text + Metadaten.
- **Verifikation:** `pytest tests/test_extract.py` grün; `omnigraph extract <file>` gibt Text+Metadaten aus.

### Phase 3 — Graph-Store + Builder (Commit: `feat: graph store + node/edge builder`)
- `graph/schema.sql`: Tabellen `nodes` (id, label, properties JSON), `edges` (src, dst, type, properties JSON), `files` (node_id, path, mtime, size, ext, sha256), `projects` (id, root, name).
- `graph/models.py`: `@dataclass Node, Edge, FileRecord, Project`.
- `graph/store.py`: `GraphStore` — `upsert_file`, `add_edge`, `get_node`, `query_neighbors`, `delete_subtree`.
- `graph/builder.py`: Aus `FileEntry` + `ExtractedContent` → `File`-Knoten, ordnet `Project`/`Folder`-Knoten zu (Root-basiert), extrahiert `Tag`/`Topic` (Frontmatter bei MD, hashtag-Heuristik), baut `CONTAINS`/`PART_OF_PROJECT`/`TAGGED`-Kanten.
- `tests/test_graph.py`: Dummy-Crawl → prüft Knoten-/Kantenanzahl + eine `CONTAINS`-Kante.
- **Verifikation:** `pytest tests/test_graph.py` grün; `omnigraph crawl --root tests/fixtures` → `omnigraph graph stats`.

### Phase 4 — Embeddings + Hybride Suche (Commit: `feat: hybrid keyword + semantic search`)
- `embed/engine.py`: `Embedder` — lädt `all-MiniLM-L6-v2` (oder MLX-Äquivalent), chunked Text (≈512 Token,Overlap 64), schreibt Vektoren in `sqlite-vec` (oder LanceDB-Tabelle).
- `search/keyword.py`: BM25 via FTS5 (`files_fts`-Virtual-Table über `(path, title, text)`).
- `search/semantic.py`: Vektor-KNN-Suche (Top-K), gibt `file_id + score`.
- `search/hybrid.py`: `hybrid_search(query, k)` → kombiniert BM25-Score (normalisiert) + Vektor-Cosine → gewichtetes Reranking (Default 0.5/0.5, konfigurierbar).
- `tests/test_search.py`: Indizierte Fixtures → gezielte Query trifft erwartete Datei.
- **Verifikation:** `pytest tests/test_search.py` grün; `omnigraph search "quarterly report"` → ranked Ergebnisse.

### Phase 5 — File-Watcher (Commit: `feat: incremental auto-update via watchdog`)
- `watch/watcher.py`: `watchdog.Observer` auf konfigurierten Roots. Events: `created`/`modified` → Re-Extract + Graph-/Vektor-Upsert; `deleted` → Graph-/Vektor-Delete; `moved` → Pfad-Update.
- Debouncing (≈1s) um Batches zu vermeiden.
- CLI: `omnigraph watch` (langlaufend), `omnigraph reindex --root X` (manueller Full-Refresh).
- `tests/test_watcher.py`: Temp-Verzeichnis, erstelle/ändere/lösche Datei → prüfe Graph-Änderung (mit kurzer Wait).
- **Verifikation:** `pytest tests/test_watcher.py` grün; manuell `omnigraph watch` + Datei anlegen → `omnigraph search` findet sie.

### Phase 6 — MCP-Server (Commit: `feat: mcp server with 6 tools`)
- `mcp_server/tools.py`: Tools:
  1. `search(query, k=10)` — hybride Suche, returns `[{file_id, path, snippet, score, topics}]`.
  2. `get_file(file_id)` — Volltext + Metadaten.
  3. `list_projects()` — alle indizierten Roots + Knotenzahlen.
  4. `graph_query(node_id, depth=2)` — Nachbarn + Kanten (JSON-Graph).
  5. `find_related(file_id, k=5)` — über `SIMILAR_TO` + gemeinsame Tags/Themen.
  6. `reindex(root=None)` — Full- oder Partial-Refresh.
- `mcp_server/server.py`: FastMCP stdio-Server, registriert Tools.
- MCP-Config-Snippet für `~/.config/opencode/opencode.json` + Claude `.mcp.json` im README dokumentieren.
- `tests/test_mcp.py`: Rufe Tools direkt via `server.call_tool` auf → prüfe Shape.
- **Verifikation:** `pytest tests/test_mcp.py` grün; `omnigraph serve` + in OpenCode `/mcp` zeigt `omnigraph` mit 6 Tools.

### Phase 7 — CLI + Web-UI (Commit: `feat: cli commands + web ui`)
- `cli.py` komplett:
  - `omnigraph crawl [--root X] [--watch]` — Indizieren (+ optional Watch-Loop).
  - `omnigraph search <q> [--limit 20] [--mode hybrid|keyword|semantic]` — rich-Tabelle.
  - `omnigraph show <file-id>` — Details.
  - `omnigraph graph [--node N] [--depth 2]` — Text-Darstellung der Nachbarschaft.
  - `omnigraph serve [--port 8765]` — startet MCP-Server ODER `--web` für Web-UI.
  - `omnigraph stats` — DB-Statistiken.
- `web/app.py`: FastAPI — `/api/search`, `/api/file/<id>`, `/api/graph/<id>`, `/` (statischer Viewer).
- `web/static/`: minimales HTML + D3-Force-Graph-Visualisierung.
- **Verifikation:** `omnigraph serve --web` → Browser `localhost:8765` zeigt Graph + Such-Box.

### Phase 8 — cbm-mcp-Integration (optional) (Commit: `feat: delegate code subgraph to codebase-memory-mcp`)
- Wenn `codebase-memory-mcp` installiert: `omnigraph` ruft dessen `search_graph`/`trace_path` für Code-Pfade auf und mergt Ergebnisse in die hybride Suche (Code-Treiber = cbm-mcp, Rest = omnigraph).
- Config-Flag `code_provider: cbm` in `config.py`.
- **Verifikation:** Code-Query geht via cbm-mcp, Dokumenten-Query via omnigraph, beide in einem `search`-Ergebnis.

### Phase 9 — Polish & Github-Readiness (Commit: `docs: readme + license + benchmarks`)
- `README.md`: Features, Architektur-Diagramm, Install, Config (`.omniignore`), MCP-Setup für OpenCode/Claude, Benchmark-Ergebnisse.
- `LICENSE` (MIT), `CONTRIBUTING.md`, `ROADMAP.md`.
- `scripts/benchmark.py`: misst Indizier-Geschwindigkeit über ein Sample-Verzeichnis (z.B. `~/Projects`).
- GitHub Actions CI: `pytest + ruff`.
- Release v0.1.0 tag.
- **Verifikation:** `pip install -e .` → `omnigraph --help`; Repo push-ready.

---

## 6. Verifikations-Strategie

- **Unit-Tests:** `pytest tests/ -q` nach jeder Phase.
- **Lint:** `ruff check src/` + `ruff format --check src/`.
- **Integration-Smoke (nach Phase 5):** `omnigraph crawl --root tests/fixtures && omnigraph search "invoice" && omnigraph stats` — end-to-end ohne externes Setup.
- **MCP-Check (nach Phase 6):** `omnigraph serve` in MCP-Config → `/mcp` zeigt Server + 6 Tools.
- **Benchmark (Phase 9):** Indizierzeit + Suchlatenz über `~/Projects` dokumentieren.

---

## 7. Commit-Konvention

Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`). Eine Phase = ein logischer Commit-Bereich. Keine DBs/Embeddings/indizierten Dateien committen (siehe `.gitignore`).

---

## 8. Bekannte Fallstricke

- ** grosse Verzeichnisse** (z.B. `~/Documents` mit 100k+ Dateien): Crawler braucht Streaming + Batch-Commits an SQLite, nicht alles im RAM. Progress-Bar via `rich`.
- **Embedding-Modell-Download** beim ersten Run (~90MB MiniLM) — im README klar kommunizieren, offline-cached danach.
- **sqlite-vec** braucht Load-Extension — Alternative `lancedb` falls Probleme. In `pyproject.toml` beides optional.
- **Watchdog** auf macOS nutzt FSEvents — effizient, aber Netzlaufwerke (SMB/NFS) werden nicht zuverlässig überwacht. Im README warnen; für externe Drives `reindex` manuell.
- **Privatsphäre:** Alles lokal, aber der Graph enthält ggf. sensible Dokumentinhalte. DB unter `~/.omnigraph/` — README empfiehlt FileVault + `.omniignore` für sensible Ordner.
- **PDF-Extraktion** scheitert oft an gescannten PDFs → v1 gibt leeren Text + Metadaten, v1.1 OCR.

---

## 9. Github-Publishing-Checkliste

- [ ] README mit Architektur-Diagramm + Screenshot der Web-Graph-Ansicht
- [ ] LICENSE (MIT), CONTRIBUTING, ROADMAP
- [ ] .gitignore sauber (keine DB/Embeddings/Fixtures-Binärdateien)
- [ ] CI: GitHub Actions `pytest + ruff`
- [ ] Benchmark-Tabelle im README (Indizierzeit, Suchlatenz, DB-Grösse)
- [ ] Release v0.1.0 tag
- [ ] Topics: `knowledge-graph`, `local-search`, `mcp`, `semantic-search`, `desktop-search`, `sqlite`, `embeddings`, `privacy`
- [ ] Description: "Local knowledge graph across all your drives — auto-indexing, hybrid search, MCP-integrated. Everything findable, nothing leaves your machine."

---

## 10. Roadmap (v1 hinaus)

- **v1.1** OCR für gescannte PDFs/Bilder (`tesseract` oder Apple Vision Framework).
- **v1.2** cbm-mcp-Integration (Code-Subgraph delegiert).
- **v1.3**native macOS-Menubar-App + Spotlight-Plugin.
- **v1.4** Multi-Device-Sync via verschlüsselter Sync-Engine (z.B. Syncthing-Integration).
- **v1.5** Graph-Visualisierung auf Steroiden (3D à la cbm-mcp-UI).
- **v2.0** "Chat with your computer" — RAG über den gesamten Graphen via lokales LLM (Ollama).
