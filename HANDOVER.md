# Handover-Prompt für antigravity — omnigraph v0.1.0 → v0.1.1

## Rolle
Du bist der Lead Engineer für **omnigraph** — ein lokaler Desktop-Knowledge-Graph auf Python 3.11+. Das Projekt ist auf v0.1.0 fertiggestellt (alle 10 Phasen aus BLUEPRINT.md committed, 31 Tests grün, ruff clean). Deine Aufgabe ist es, **bekannte Lücken und Bugs zu schliessen** und das Projekt in Richtung v0.1.1 zu bringen. Arbeite voll autonom, frage nicht nach, verifiziere nach jeder Änderung mit `pytest tests/ -q && ruff check src/ && ruff format --check src/` und committe bei Grün mit Conventional Commits.

## Projekt-Kontext (kalt startbar)
- **Repo-Pfad:** `/Users/matteoise/Documents/Development/Projects/personal/omnigraph`
- **Was es ist:** Lokaler Knowledge-Graph über alle Drives. Crawlt Dateien (Text/PDF/DOCX/XLSX/Code/Bilder/Medien), extrahiert Content, baut SQLite-Graph, hybride Suche (BM25 via FTS5 + Vektoren via sqlite-vec), File-Watcher-Auto-Update, MCP-Server mit 6 Tools, FastAPI Web-UI mit D3-Graph.
- **Lizenz:** MIT. Keine Cloud, keine API-Keys, keine Telemetrie.
- **Lies ZUERST:** `BLUEPRINT.md` (Phasen-Plan, Architektur, Fallstricke), `AGENTS.md` (Konventionen, Befehle), `README.md` (Overview), `PROGRESS.md` (Status pro Phase).
- **Stack:** Python · SQLite (FTS5 + sqlite-vec) · pathspec · watchdog · pypdf/pdfplumber · python-docx · openpyxl · Pillow · sentence-transformers (all-MiniLM-L6-v2) · FastMCP · FastAPI · typer/rich.

## Befehle
- Tests: `pytest tests/ -q`
- Lint: `ruff check src/`
- Format prüfen: `ruff format --check src/`
- CLI: `python -m omnigraph --help`
- Smoke: `python -m omnigraph crawl --root tests/fixtures && python -m omnigraph search "sample" --mode keyword && python -m omnigraph stats`
- Web UI: `python -m omnigraph serve --web --port 8765` → `http://localhost:8765`
- MCP: `python -m omnigraph serve` (stdio)
- Benchmark: `python scripts/benchmark.py tests/fixtures`

## Aktueller Stand (commit `3f41c2b`)
```
3f41c2b docs: readme + license + benchmarks
c856991 feat: delegate code subgraph to codebase-memory-mcp
1a58780 feat: cli commands + web ui
696daa1 feat: mcp server with 6 tools
ced26ad feat: incremental auto-update via watchdog
7695b88 feat: hybrid keyword + semantic search
af7ff78 feat: graph store + node/edge builder
80de8e9 feat: content extractors for text pdf docx xlsx code image media
0ee5c2c feat: ignore-aware filesystem crawler
28303cc chore: scaffold project + deps
```

Architektur überblick — alle Module existieren und sind getestet:
```
src/omnigraph/
├── cli.py              # typer CLI: crawl, search, show, graph, stats, reindex, serve
├── config.py           # Config dataclass (roots, ignores, blocked_paths, MiniLM)
├── crawler/            # ignores.py (pathspec), walker.py (os.scandir, blocklist)
├── extract/            # base, text, pdf, docx, xlsx, code, image, media, registry
├── graph/              # schema.sql, models, store (SQLite WAL), builder (tags/topics)
├── embed/              # engine.py (sentence-transformers, chunking)
├── search/             # keyword (FTS5), semantic (sqlite-vec), hybrid (reranker)
├── watch/              # watcher.py (watchdog observer + debounce)
├── mcp_server/         # server.py (FastMCP), tools.py (6 tools)
├── web/                # app.py (FastAPI), static/index.html (D3 force graph)
└── integration/        # cbm-mcp graceful degradation
tests/                  # 31 tests (crawler, extract, graph, search, mcp, watcher, integration)
```

## Bekannte Lücken — Deine Arbeitsliste (priorisiert)

### 🔴 KRITISCH (Bugs — zwingend fixen)

1. **Embeddings werden beim Crawl/Reindex/Watch NICHT in sqlite-vec geschrieben.**
   - In `cli.py` (crawl, reindex) und `mcp_server/tools.py` (reindex) und `watch/watcher.py` wird `KeywordSearch.index()` aufgerufen, aber `SemanticSearch.index()` nie.
   - Folge: `omnigraph search "x" --mode semantic` liefert immer leer. `--mode hybrid` fällt effektiv auf reine Keyword-Suche zurück.
   - Fix: Beim Indexieren jeder Datei: chunks via `Embedder.chunk_text(content.text)` → `embedder.encode(chunks)` → pro Chunk `SemanticSearch.index(file_id + f":chunk{i}", embedding)`. Beim Reindex alte Vektoren der Datei zuerst löschen (`SemanticSearch.delete`).
   - Verifikation: Test in `tests/test_search.py` der `--mode semantic` wirklich Treffer liefert (Achtung: zuerst `all-MiniLM-L6-v2` lokal cachen — kann ~90MB Download beim ersten Run brauchen; im CI ggf. skippen mit `pytest.mark.skipif`).
   - Commit: `fix: wire embeddings into crawl/reindex/watch pipeline`

2. **`hash(file_id)` ist prozess-instabil — FTS5-Rowids matchen nicht über Prozesse hinweg.**
   - `KeywordSearch.index()` nutzt `hash(file_id) & 0x7FFFFFFF` als FTS5-rowid. Pythons `hash()` ist für Strings pro Prozess randomisiert (`PYTHONHASHSEED`).
   - Folge: Wenn du in Prozess A crawlst und in Prozess B reindext/deletest, greifen die Delete-Statements ins Leere. FTS5 füllt sich mit Duplikaten.
   - Fix: Stabilen Hash verwenden, z.B. `int(hashlib.md5(file_id.encode()).hexdigest()[:8], 16)`.
   - Verifikation: Test: in Prozess A index, in separatem subprocess delete → FTS5 leer.
   - Commit: `fix: use deterministic hash for FTS5 rowids`

3. **`walk()` gibt eine `list` zurück statt Generator — OOM-Risiko bei 100k+ Dateien.**
   - BLUEPRINT.md Fallstricke §8 explizit: "Crawler braucht Streaming + Batch-Commits an SQLite, nicht alles im RAM."
   - Fix: `walk()` in `crawler/walker.py` als Generator umschreiben (`yield FileEntry`), `_walk_recursive` entsprechend. CLI crawlt dann in Batches (z.B. alle 1000 Einträge Commit).
   - Commit: `fix: walker returns generator for streaming large directories`

4. **`PROGRESS.md` zeigt Phase 9 noch als `in_progress`.**
   - Fix: Markiere als `completed` mit Commit `3f41c2b`.
   - Commit: `docs: mark phase 9 complete in PROGRESS.md`

### 🟡 HOCH (Qualität — Blueprint-Erwartungen noch nicht erfüllt)

5. **`find_related` nutzt keine `SIMILAR_TO`-Kanten.**
   - BLUEPRINT Phase 6 Tool 5: "über `SIMILAR_TO` + gemeinsame Tags/Themen". Aktuell nur gemeinsame Tag/Topic/Folder-Nachbarn.
   - Fix: Nach jeder Indexierung Top-N ähnlichste Dateien via Cosine-Similarity der Embeddings berechnen und `SIMILAR_TO`-Kanten in den Graphen schreiben. `find_related` nutzt diese dann zusätzlich.
   - Commit: `feat: add SIMILAR_TO edges via embedding cosine similarity`

6. **Keine Progress-Bar beim Crawl.**
   - BLUEPRINT Fallstricke §8 fordert `rich`-Progress-Bar.
   - Fix: In `cli.py crawl` `rich.progress.Progress` um die Walk-Schleife legen.
   - Commit: `feat: rich progress bar for crawl command`

7. **File-Watcher beobachtet nur `roots[0]`.**
   - In `cli.py crawl --watch` steht `watcher = FileWatcher(store, roots[0])`. Sollte alle Roots beobachten.
   - Fix: Pro Root einen `FileWatcher` starten (oder einen Observer mit多个 `schedule`-Aufrufen).
   - Commit: `fix: file watcher observes all configured roots`

8. **Config kann nicht aus `~/.omnigraph/config` laden.**
   - README.md behauptet "Edit `~/.omnigraph/config`" — Config-Klasse ist aber hardcoded.
   - Fix: TOML-Loading via `tomllib` (stdlib in 3.11+) mit Defaults überschrieben; optional ENV-Vars (`OMNIGRAPH_ROOTS`, `OMNIGRAPH_DB_PATH`).
   - Commit: `feat: load config from ~/.omnigraph/config.toml and env`

### 🟢 MITTEL (Features — für v0.1.1)

9. **Pydantic-Modelle für MCP-Tool-Rückgabewerte.**
   - Aktuell `list[dict]` — FastMCP kann kein Schema generieren. Pydantic-Modelle geben Clients bessere Introspection.
   - Commit: `refactor: pydantic models for mcp tool return types`

10. **Web UI: `/api/projects` Endpoint + Anzeige.**
    - fehlt komplett. FastAPI + kleines HTML-Stück.
    - Commit: `feat: web ui projects endpoint`

11. **Weitere Extractors: PPTX (.pptx), EPUB (.epub), Jupyter (.ipynb), HTML (.html).**
    - Alle via stabile OSS-Libs (`python-pptx`, `ebooklib`, `nbformat`), nur wenn >1000 Downloads/Monat.
    - Commit: `feat: extractors for pptx epub ipynb html`

12. **Funktions-Level Code-Chunking (statt nur Wort-Chunking).**
    - BLUEPRINT Phase 2 erwähnt "Funktion-Heuristik". Aktuell `chunk_text` splittet nur nach Wörtern.
    - Fix: Für Python/JS/TS mind. an Funktions-/Klassengrenzen splitten (AST via `ast`-Modul für Python, `esprima`-ähnlich für JS — oder simpler Regex-Heuristik).
    - Commit: `feat: function-level code chunking`

13. **Graceful Shutdown für Watcher (SIGINT/SIGTERM sauber fangen).**
    - Commit: `fix: graceful watcher shutdown on signal`

### 🔵 NIEDRIG (Polish — optional)

14. **MCP-Tool-Errors als `{"error": ...}` statt `raise ValueError`.**
15. **README: GitHub-URL `YOUR/omnigraph` durch echtes Repo ersetzen.**
16. **Release v0.1.0 Tag setzen + GitHub-Topics: `knowledge-graph`, `local-search`, `mcp`, `semantic-search`, `desktop-search`, `sqlite`, `embeddings`, `privacy`.**
17. **Web UI: Zoom/Pan für D3-Graph, Node-Count-Limit (sonst Browser-Crash bei >1000 Knoten).**
18. **HuggingFace-Offline-Modus nach erstem Modell-Download** (`HF_HUB_OFFLINE=1` setzen sobald Modell gecacht — true offline Assurance).
19. **Edges in `/api/graph` auf Top-N begrenzen** (sonst SQL wird riesig bei depth>=2).
20. **Screenshots der Web-UI im README** (liegen aktuell nicht im Repo).

## Autonomie-Regeln
- Triff Entscheidungen selbständig. Frage nicht nach.
- Wenn du festestellt hast, dass eine Entscheidung im Blueprint einer Wahl lassen (z.B. sqlite-vec vs lancedb): wirf keinen grossen Loop, sondern dokumentiere Entscheidung im Commit-Body.
- Nach jeder Änderung: `pytest tests/ -q && ruff check src/ && ruff format --check src/`. Erst bei Grün committen. Bei Rot: erst offensichtlichster Fix, dann Alternative, dann skill-Konsultation.

## Self-Healing bei Fehlern
1. Fix 1 — offensichtlichste Lösung.
2. Fix 2 — alternative Herangehensweise aus dem BLUEPRINT (z.B. lancedb statt sqlite-vec wenn vec-Extension Probleme macht).
3. Fix 3 — relevante Skills konsultieren. Verfügbare Skill-Names je nach Plattform: `python-patterns`, `python-testing`, `coding-standards`, `mcp-server-patterns`, `security-review`, `tdd-workflow`, `verification-loop`.
4. Alle 3 scheitern → PROGRESS.md-Eintrag "blocked: <Fehler> + <Versuche> + <nötiger Next-Step>" und weiter mit nächstem Punkt.

## Data Security — STRENG
- `pip install` NUR Pakete die in `pyproject.toml` stehen oder etablierte OSS-Libs mit >1000 Downloads/Monat sind. Neue Pakete: Commit-Body begründen WARUM.
- Keine `curl|bash` von externen Skripten.
- Modelle NUR: `all-MiniLM-L6-v2` via sentence-transformers (HuggingFace offiziell), `mlx-community-*` Embeddings (HuggingFace offiziell). Keine anderen Downloads.
- Keine API-Keys, keine Cloud-Aufrufe, keine externen HTTP-Requests ausser HuggingFace-Modell-Download + PyPI.
- Keine Telemetrie/Analytics. Kein `os.system`/`subprocess` mit unsanitised Input.
- Crawler darf NUR die in `config.py` definierten Roots indizieren. Niemals `/`, `/etc`, `/System`, `~/.ssh`, `~/.config` crawlen. Hartcodierter Blocklist-Check im Walker (bereits vorhanden, nicht aushebeln).
- Unsicherer Quick-Fix nötig? TU ES NICHT. Nutze Fix 2/3.

## Skills-Nutzung (proaktiv)
Lade bei Bedarf via Skill-Tool: `python-patterns`, `python-testing`, `coding-standards`, `mcp-server-patterns`, `security-review`, `tdd-workflow`, `verification-loop`.

## Erwartung bei Rückkehr
- PROGRESS.md aktuell mit v0.1.1-Status und Commits.
- `git log` sauber (Conventional Commits, pro Bug/Feature ein Commit).
- `pytest tests/ -q` grün (auch mit neuen Tests für Embeddings-Pipeline).
- `ruff check src/` clean.
- `python -m omnigraph --help` läuft.
- Smoke `crawl tests/fixtures && search "sample" --mode hybrid && stats` klappt.
- Erste `--mode semantic` Suche gegen Fixtures liefert Treffer (Embedding-Modell lokal gecacht).
- Kein Crawlen ausserhalb der konfigurierten Roots. Keine Secrets, keine externen Downloads ausser HuggingFace.

## Los
Beginne mit dem Lesen von `BLUEPRINT.md` und `AGENTS.md`, dann arbeite die Arbeitsliste KRITISCH → HOCH → MITTEL → NIEDRIG ab. Committe jeden Fix separat. Aktualisiere `PROGRESS.md` nach jedem Commit. Verifiziere nach jedem Commit. Wenn alles KRITISCH + HOCH durch ist, setze einen `v0.1.1` Git-Tag.

Viel Erfolg.