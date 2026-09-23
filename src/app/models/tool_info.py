from dataclasses import dataclass


@dataclass(frozen=True)
class ToolInfo:
    name: str
    available: bool
    path: str | None = None
    version: str | None = None
    error: str | None = None
