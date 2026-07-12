from __future__ import annotations

from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".kt",
    ".swift",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".sh",
    ".bash",
    ".zsh",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".vue",
    ".svelte",
    ".lua",
    ".r",
    ".m",
    ".mm",
}


class CodeExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""

        language = self._detect_language(path)

        metadata = {
            "type": "code",
            "extension": path.suffix.lower(),
            "language": language,
            "size": path.stat().st_size,
            "lines": len(text.splitlines()),
        }

        chunks = []
        if language == "python":
            chunks = self._ast_chunk_python(text)
        
        if not chunks:
            chunks = self.chunk_text(text)
            
        return ExtractedContent(text=text, metadata=metadata, chunks=chunks)

    def _ast_chunk_python(self, text: str) -> list[str]:
        import ast
        try:
            tree = ast.parse(text)
            chunks = []
            lines = text.splitlines()
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    start = node.lineno - 1
                    end = getattr(node, "end_lineno", len(lines))
                    chunks.append("\n".join(lines[start:end]))
            return chunks
        except Exception:
            return []

    def _detect_language(self, path: Path) -> str:
        try:
            from pygments.lexers import get_lexer_for_filename

            lexer = get_lexer_for_filename(path.name)
            return lexer.name.lower()
        except Exception:
            return path.suffix.lstrip(".").lower()
