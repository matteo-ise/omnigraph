from __future__ import annotations

import struct

from omnigraph.config import get_config


class Embedder:
    def __init__(self, model_name: str | None = None):
        config = get_config()
        self.model_name = model_name or config.embedding_model
        self.chunk_size = config.chunk_size
        self.chunk_overlap = config.chunk_overlap
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str]) -> list[bytes]:
        self._load_model()
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return [self._to_bytes(emb) for emb in embeddings]

    def encode_query(self, query: str) -> bytes:
        self._load_model()
        embedding = self._model.encode([query], convert_to_numpy=True)[0]
        return self._to_bytes(embedding)

    def chunk_text(self, text: str) -> list[str]:
        if not text:
            return []
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i : i + self.chunk_size])
            if chunk:
                chunks.append(chunk)
            if i + self.chunk_size >= len(words):
                break
        return chunks

    @staticmethod
    def _to_bytes(vec) -> bytes:
        return struct.pack(f"{len(vec)}f", *vec)

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._model.get_sentence_embedding_dimension()
