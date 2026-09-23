from pathlib import Path

from app.models.media_file import MediaFile


SUPPORTED_EXTENSIONS = frozenset({".mkv", ".mp4", ".m4v", ".mov", ".avi", ".webm", ".ts", ".m2ts"})


class MediaImportService:
    @staticmethod
    def validate(path: str) -> MediaFile:
        candidate = Path(path).expanduser().resolve()
        if candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError("Format vidéo non pris en charge")
        if not candidate.is_file():
            raise ValueError("Fichier introuvable ou inaccessible")
        try:
            size = candidate.stat().st_size
        except OSError as exc:
            raise ValueError("Fichier inaccessible") from exc
        if size == 0:
            raise ValueError("Fichier vide")
        return MediaFile(path=candidate, size=size)
