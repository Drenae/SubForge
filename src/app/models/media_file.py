from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MediaFile:
    path: Path
    size: int

    @property
    def name(self) -> str:
        return self.path.name
