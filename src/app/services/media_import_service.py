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

    @staticmethod
    def scan_folder(folder: str) -> tuple[list[str], list[str]]:
        root = Path(folder).expanduser().resolve()
        if not root.is_dir():
            return [], [f"{folder}: Dossier introuvable ou inaccessible"]
        paths = []
        errors = []

        def on_error(exc: OSError) -> None:
            errors.append(f"{exc.filename or folder}: {exc.strerror or exc}")

        import os
        for current, _, filenames in os.walk(root, onerror=on_error):
            for filename in filenames:
                if Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS:
                    paths.append(str(Path(current) / filename))
        paths.sort(key=str.casefold)
        return paths, errors
