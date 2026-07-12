from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractedContent:
    text: str
    metadata: dict = field(default_factory=dict)
    chunks: list[str] = field(default_factory=list)


class Extractor(ABC):
    @abstractmethod
    def extract(self, path: Path) -> ExtractedContent:
        pass

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        if not text:
            return []
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            if chunk:
                chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
        return chunks
