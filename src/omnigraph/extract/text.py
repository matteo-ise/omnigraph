from __future__ import annotations

from pathlib import Path

from charset_normalizer import from_path

from omnigraph.extract.base import ExtractedContent, Extractor

TEXT_EXTENSIONS = {".txt", ".md", ".mdx", ".rst", ".org", ".csv", ".json", ".yaml", ".yml", ".toml"}


class TextExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            result = from_path(path)
            best = result.best()
            text = str(best) if best else ""

        metadata = {
            "type": "text",
            "extension": path.suffix.lower(),
            "size": path.stat().st_size,
        }

        if path.suffix.lower() in {".md", ".mdx"}:
            metadata.update(self._parse_frontmatter(text))

        chunks = self.chunk_text(text)
        return ExtractedContent(text=text, metadata=metadata, chunks=chunks)

    def _parse_frontmatter(self, text: str) -> dict:
        if not text.startswith("---"):
            return {}
        end = text.find("---", 3)
        if end == -1:
            return {}
        fm = text[3:end].strip()
        result = {}
        for line in fm.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip()
        return result
