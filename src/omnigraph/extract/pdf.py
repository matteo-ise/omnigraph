from __future__ import annotations

from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor


class PdfExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent:
        text = self._extract_pypdf(path)
        if not text.strip():
            text = self._extract_pdfplumber(path)

        metadata = {
            "type": "pdf",
            "extension": ".pdf",
            "size": path.stat().st_size,
        }

        chunks = self.chunk_text(text)
        return ExtractedContent(text=text, metadata=metadata, chunks=chunks)

    def _extract_pypdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(path))
            pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
            return "\n\n".join(pages)
        except Exception:
            return ""

    def _extract_pdfplumber(self, path: Path) -> str:
        try:
            import pdfplumber

            with pdfplumber.open(str(path)) as pdf:
                pages = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pages.append(page_text)
                return "\n\n".join(pages)
        except Exception:
            return ""
