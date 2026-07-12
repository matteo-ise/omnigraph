from __future__ import annotations

from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor
from omnigraph.extract.code import CODE_EXTENSIONS, CodeExtractor
from omnigraph.extract.docx import DocxExtractor
from omnigraph.extract.image import IMAGE_EXTENSIONS, ImageExtractor
from omnigraph.extract.media import MEDIA_EXTENSIONS, MediaExtractor
from omnigraph.extract.pdf import PdfExtractor
from omnigraph.extract.text import TEXT_EXTENSIONS, TextExtractor
from omnigraph.extract.xlsx import XlsxExtractor

_REGISTRY: dict[str, Extractor] = {}


def _init_registry():
    if _REGISTRY:
        return

    text_ext = TextExtractor()
    for ext in TEXT_EXTENSIONS:
        _REGISTRY[ext] = text_ext

    pdf_ext = PdfExtractor()
    _REGISTRY[".pdf"] = pdf_ext

    docx_ext = DocxExtractor()
    _REGISTRY[".docx"] = docx_ext

    xlsx_ext = XlsxExtractor()
    for ext in [".xlsx", ".xls"]:
        _REGISTRY[ext] = xlsx_ext

    code_ext = CodeExtractor()
    for ext in CODE_EXTENSIONS:
        _REGISTRY[ext] = code_ext

    image_ext = ImageExtractor()
    for ext in IMAGE_EXTENSIONS:
        _REGISTRY[ext] = image_ext

    media_ext = MediaExtractor()
    for ext in MEDIA_EXTENSIONS:
        _REGISTRY[ext] = media_ext

    from omnigraph.extract.pptx import PptxExtractor
    _REGISTRY[".pptx"] = PptxExtractor()
    _REGISTRY[".ppt"] = PptxExtractor()

    from omnigraph.extract.html import HtmlExtractor
    html_ext = HtmlExtractor()
    for ext in [".html", ".htm", ".xhtml"]:
        _REGISTRY[ext] = html_ext

    from omnigraph.extract.epub import EpubExtractor
    _REGISTRY[".epub"] = EpubExtractor()

    from omnigraph.extract.ipynb import IpynbExtractor
    _REGISTRY[".ipynb"] = IpynbExtractor()

def get_extractor(path: Path) -> Extractor | None:
    _init_registry()
    return _REGISTRY.get(path.suffix.lower())


def extract_file(path: Path) -> ExtractedContent | None:
    extractor = get_extractor(path)
    if extractor is None:
        return None
    return extractor.extract(path)
