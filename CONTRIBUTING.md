# Contributing to omnigraph

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/YOUR/omnigraph.git
cd omnigraph
pip install -e ".[dev]"
```

## Workflow

1. Create a branch: `feat/your-feature` or `fix/your-bug`.
2. Write code following existing style (enforced by `ruff`).
3. Add tests for new functionality.
4. Run verification:
   ```bash
   pytest tests/ -q
   ruff check src/
   ruff format --check src/
   ```
5. Use Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`.
6. Open a PR with a clear description.

## Conventions

- Python 3.11+
- One BLUEPRINT phase per logical commit area.
- Never commit DBs, embedding models, or indexed binaries (see `.gitignore`).
- Everything stays local — no cloud calls, no API keys, no telemetry.
- Security: never crawl system paths (`/`, `/etc`, `~/.ssh`, etc.).

## Adding a New Extractor

1. Create `src/omnigraph/extract/yourtype.py` extending `Extractor`.
2. Register it in `extract/registry.py`.
3. Add a test in `tests/test_extract.py` with a fixture file.