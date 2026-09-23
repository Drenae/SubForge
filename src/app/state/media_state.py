from app.models.media_file import MediaFile
from app.services.media_import_service import MediaImportService


class MediaState:
    def __init__(self):
        self.files: dict[str, MediaFile] = {}

    def add(self, paths: list[str]) -> tuple[int, list[str]]:
        added = 0
        errors = []
        for path in paths:
            try:
                media = MediaImportService.validate(path)
            except (ValueError, OSError) as exc:
                errors.append(f"{path}: {exc}")
                continue
            key = str(media.path).casefold()
            if key not in self.files:
                self.files[key] = media
                added += 1
        return added, errors

    def remove(self, path: str) -> None:
        self.files.pop(path.casefold(), None)

    def clear(self) -> None:
        self.files.clear()
