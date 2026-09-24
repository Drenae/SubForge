import os
import shutil
import subprocess
from pathlib import Path

from app.models.tool_info import ToolInfo
from app.services.logging_service import LoggingService


class ToolDetectionService:
    _logger = LoggingService.get_logger("tools")

    @staticmethod
    def _binary_name(executable: str) -> str:
        return executable + (".exe" if os.name == "nt" else "")

    @staticmethod
    def resolve_executable(executable: str) -> str | None:
        filename = ToolDetectionService._binary_name(executable)
        assets = Path(os.environ.get("FLET_ASSETS_DIR") or
                      Path(__file__).resolve().parents[2] / "assets")
        bundled = assets / "tools" / "windows" / filename
        if bundled.is_file():
            return str(bundled)
        return shutil.which(executable)

    @staticmethod
    def detect(executable: str) -> ToolInfo:
        path = ToolDetectionService.resolve_executable(executable)
        if not path:
            ToolDetectionService._logger.warning("%s introuvable dans le PATH système", executable)
            return ToolInfo(
                name=executable,
                available=False,
                error="Exécutable introuvable dans le PATH système.",
            )

        try:
            result = subprocess.run(
                [path, "-version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            output = (result.stdout or result.stderr).strip()
            first_line = output.splitlines()[0] if output else ""
            version = ToolDetectionService._extract_version(first_line)
            available = result.returncode == 0
            ToolDetectionService._logger.info(
                "%s: available=%s version=%s path=%s", executable, available, version, path
            )
            return ToolInfo(
                name=executable,
                available=available,
                path=path,
                version=version,
                error=None if available else first_line or "Impossible d'interroger l'exécutable.",
            )
        except (OSError, subprocess.SubprocessError) as exc:
            ToolDetectionService._logger.exception("Erreur pendant la détection de %s", executable)
            return ToolInfo(name=executable, available=False, path=path, error=str(exc))

    @staticmethod
    def detect_all() -> dict[str, ToolInfo]:
        return {
            "ffmpeg": ToolDetectionService.detect("ffmpeg"),
            "ffprobe": ToolDetectionService.detect("ffprobe"),
        }

    @staticmethod
    def _extract_version(first_line: str) -> str | None:
        parts = first_line.split()
        if len(parts) >= 3 and parts[0].lower() in {"ffmpeg", "ffprobe"} and parts[1].lower() == "version":
            return parts[2]
        return first_line or None
