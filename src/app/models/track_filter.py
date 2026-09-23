from dataclasses import dataclass

from app.models.subtitle_track import SubtitleTrack


FRENCH_CODES = frozenset({"fr", "fra", "fre", "french", "français", "francais"})


@dataclass(frozen=True)
class TrackFilter:
    language: str | None = None
    codec: str | None = None
    mode: str = "all"  # all, forced, full
    default_only: bool = False

    def matches(self, track: SubtitleTrack) -> bool:
        language = (track.language or "").strip().casefold()
        expected = (self.language or "").strip().casefold()
        if expected == "français":
            if language not in FRENCH_CODES:
                return False
        elif expected and language != expected:
            return False
        if self.codec and track.codec.casefold() != self.codec.casefold():
            return False
        if self.mode == "forced" and not track.forced:
            return False
        if self.mode == "full" and track.forced:
            return False
        if self.default_only and not track.default:
            return False
        return True
