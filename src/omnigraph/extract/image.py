from __future__ import annotations

from pathlib import Path

from omnigraph.extract.base import ExtractedContent, Extractor

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic"}


class ImageExtractor(Extractor):
    def extract(self, path: Path) -> ExtractedContent:
        metadata = {
            "type": "image",
            "extension": path.suffix.lower(),
            "size": path.stat().st_size,
        }

        try:
            from PIL import Image
            from PIL.ExifTags import TAGS

            with Image.open(str(path)) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
                metadata["mode"] = img.mode

                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, str(tag_id))
                        try:
                            metadata[f"exif_{tag}"] = str(value)
                        except Exception:
                            pass

        except Exception:
            pass

        text = f"Image: {path.name}"
        if "width" in metadata and "height" in metadata:
            text += f" ({metadata['width']}x{metadata['height']})"

        return ExtractedContent(text=text, metadata=metadata, chunks=[text])
