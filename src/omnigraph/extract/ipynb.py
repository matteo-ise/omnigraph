from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor


class IpynbExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent | None:
        try:
            import nbformat

            nb = nbformat.read(path, as_version=4)
            text = []
            for cell in nb.cells:
                if cell.cell_type in ("markdown", "code"):
                    text.append(cell.source)
            return ExtractedContent(
                text="\n\n".join(text),
                metadata={"type": "jupyter_notebook", "title": path.name},
                chunks=[],
            )
        except Exception:
            return None
