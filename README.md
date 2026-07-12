# omnigraph

> Lokaler Knowledge Graph über deinen ganzen Computer. Indiziert Dateien über alle Drives hinweg, modelliert Beziehungen, aktualisiert sich selbst und beantwortet Suchanfragen in Millisekunden — hybrid aus Keyword- und Semantik-Suche. MCP-integriert für jeden Coding-Agent.

## Status

🚧 In Planung — siehe [`BLUEPRINT.md`](./BLUEPRINT.md) für den vollständigen Bauplan.

## Was es wird

Ein desktop-weiter Knowledge-Graph: crawlt konfigurierbare Roots (`~/Documents`, `~/Projects`, externe Drives), extrahiert Content aus Text, Markdown, PDF, DOCX, XLSX, Code, Bildern und Medien, baut einen Graphen (Datei → Projekt → Thema → Tag → Link) und bietet hybride Suche (BM25 + lokale Vektoren). Ein File-Watcher hält alles aktuell. Ein MCP-Server exposes 6 Tools, damit Claude Code / OpenCode / Codex deinen Computer befragen können.

**Ergänzt** [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) (das nur Code-Repos indiziert) — `omnigraph` deckt alle Dateitypen ab und kann Code an cbm-mcp delegieren.

## Warum

Spotlight/mdfind ist schnell aber flach — keine Semantik, kein Graph, keine Agent-Schnittstelle. cbm-mcp ist tief, aber nur Code. `omnigraph` schliesst die Lücke: desktop-weit, semantisch, graph-basiert, MCP-ready. Alles lokal, keine Cloud, keine API-Keys.

## Lizenz

MIT
