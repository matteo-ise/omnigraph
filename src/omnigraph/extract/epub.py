from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor


class EpubExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent | None:
        try:
            import ebooklib
            from bs4 import BeautifulSoup
            from ebooklib import epub

            book = epub.read_epub(path)
            text = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text.append(soup.get_text(separator="\n", strip=True))

            title = book.get_metadata("DC", "title")
            title_str = title[0][0] if title else path.name

            return ExtractedContent(
                text="\n".join(text), metadata={"type": "ebook", "title": title_str}, chunks=[]
            )
        except Exception:
            return None
