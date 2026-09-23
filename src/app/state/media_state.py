from app.models.media_file import MediaFile
from app.models.subtitle_track import SubtitleTrack
from app.services.media_import_service import MediaImportService


class MediaState:
    def __init__(self):
        self.files: dict[str, MediaFile] = {}
        self.tracks: dict[str, list[SubtitleTrack]] = {}
        self.analysis_errors: dict[str, str] = {}
        self.selected_tracks: set[tuple[str, int]] = set()

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

    def set_tracks(self, path: str, tracks: list[SubtitleTrack]) -> None:
        key = path.casefold()
        if key not in self.files:
            return
        self.tracks[key] = tracks
        valid_indices = {track.index for track in tracks}
        self.selected_tracks = {item for item in self.selected_tracks
                                if item[0] != key or item[1] in valid_indices}
        self.analysis_errors.pop(key, None)

    def select_track(self, path: str, index: int, selected: bool) -> None:
        key = path.casefold()
        item = (key, index)
        if key not in self.files or index not in {track.index for track in self.tracks.get(key, [])}:
            return
        if selected:
            self.selected_tracks.add(item)
        else:
            self.selected_tracks.discard(item)

    def select_all(self, selected: bool) -> None:
        self.selected_tracks = ({(key, track.index)
                                 for key, tracks in self.tracks.items() if key in self.files
                                 for track in tracks} if selected else set())

    def remove(self, path: str) -> None:
        key = path.casefold()
        self.files.pop(key, None)
        self.tracks.pop(key, None)
        self.analysis_errors.pop(key, None)
        self.selected_tracks = {item for item in self.selected_tracks if item[0] != key}

    def clear(self) -> None:
        self.files.clear()
        self.tracks.clear()
        self.analysis_errors.clear()
        self.selected_tracks.clear()
