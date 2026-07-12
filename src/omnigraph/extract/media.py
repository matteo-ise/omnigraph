from __future__ import annotations

from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor

MEDIA_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".flac", ".ogg", ".wav", ".aac", ".wma", ".mov", ".avi"}


class MediaExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent:
        metadata = {
            "type": "media",
            "extension": path.suffix.lower(),
            "size": path.stat().st_size,
        }

        try:
            from mutagen import File

            audio = File(str(path))
            if audio is not None:
                if audio.info:
                    metadata["length"] = getattr(audio.info, "length", None)
                    metadata["bitrate"] = getattr(audio.info, "bitrate", None)
                    metadata["sample_rate"] = getattr(audio.info, "sample_rate", None)

                if audio.tags:
                    for key in audio.tags:
                        try:
                            value = audio.tags[key]
                            if isinstance(value, list):
                                value = value[0] if value else ""
                            metadata[f"tag_{key}"] = str(value)[:200]
                        except Exception:
                            pass

        except Exception:
            pass

        text_parts = [f"Media: {path.name}"]
        if "length" in metadata and metadata["length"]:
            minutes = int(metadata["length"] // 60)
            seconds = int(metadata["length"] % 60)
            text_parts.append(f"Duration: {minutes}:{seconds:02d}")

        text = " | ".join(text_parts)
        return ExtractedContent(text=text, metadata=metadata, chunks=[text])
