from dataclasses import dataclass


@dataclass(frozen=True)
class OcrCue:
    start_ms: int
    end_ms: int
    text: str
    confidence: float | None = None
