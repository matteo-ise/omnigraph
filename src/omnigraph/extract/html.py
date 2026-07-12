from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor


class HtmlExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent | None:
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(path.read_text(errors="ignore"), "html.parser")
            title = soup.title.string if soup.title else path.name
            return ExtractedContent(
                text=soup.get_text(separator="\n", strip=True),
                metadata={"type": "html", "title": title},
                chunks=[],
            )
        except Exception:
            return None
