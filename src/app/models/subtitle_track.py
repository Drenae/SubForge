from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubtitleTrack:
    index: int
    codec: str
    language: str | None = None
    title: str | None = None
    forced: bool = False
    default: bool = False
    tags: dict[str, str] = field(default_factory=dict)
