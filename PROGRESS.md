# omnigraph — Progress

## Phase 0: Projekt-Gerüst
- **Status:** completed
- **Commit:** 28303cc
- **Notes:** pyproject.toml, __init__, __main__, cli, config, .gitignore

## Phase 1: Crawler + Ignores
- **Status:** completed
- **Commit:** 0ee5c2c
- **Notes:** IgnoreStack (pathspec), walker with blocklist, 5 tests

## Phase 2: Extractors
- **Status:** completed
- **Commit:** 80de8e9
- **Notes:** 8 extractors (text, pdf, docx, xlsx, code, image, media, registry), 9 tests

## Phase 3: Graph-Store + Builder
- **Status:** completed
- **Commit:** af7ff78
- **Notes:** SQLite schema, models, store (CRUD + WAL), builder (tags/topics), 4 tests

## Phase 4: Embeddings + Hybride Suche
- **Status:** completed
- **Commit:** 7695b88
- **Notes:** Embedder (MiniLM), KeywordSearch (FTS5), SemanticSearch (sqlite-vec), hybrid reranker, 3 tests

## Phase 5: File-Watcher
- **Status:** completed
- **Commit:** ced26ad
- **Notes:** watchdog with debounce, thread-safe SQLite, 3 tests

## Phase 6: MCP-Server
- **Status:** completed
- **Commit:** 696daa1
- **Notes:** FastMCP server with 6 tools, 5 tests

## Phase 7: CLI + Web-UI
- **Status:** completed
- **Commit:** 1a58780
- **Notes:** Full CLI (crawl, search, show, graph, stats, reindex, serve), FastAPI web UI with D3 graph

## Phase 8: cbm-mcp-Integration (optional)
- **Status:** completed
- **Commit:** c856991
- **Notes:** Graceful degradation, merge results, 2 tests

## Phase 9: Polish & Github-Readiness
- **Status:** completed
- **Commit:** 3f41c2b
- **Notes:** README, LICENSE, CONTRIBUTING, ROADMAP, CI, benchmark script