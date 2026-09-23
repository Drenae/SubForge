from app.models.media_file import MediaFile
from app.models.subtitle_track import SubtitleTrack
from app.services.media_import_service import MediaImportService


class MediaState:
    def __init__(self):
        self.files: dict[str, MediaFile] = {}
        self.tracks: dict[str, list[SubtitleTrack]] = {}
        self.analysis_errors: dict[str, str] = {}

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
        key = path.casefold()
        self.files.pop(key, None)
        self.tracks.pop(key, None)
        self.analysis_errors.pop(key, None)

    def clear(self) -> None:
        self.files.clear()
        self.tracks.clear()
        self.analysis_errors.clear()
