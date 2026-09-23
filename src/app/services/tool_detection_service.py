import shutil
import subprocess

from app.models.tool_info import ToolInfo


class ToolDetectionService:
    @staticmethod
    def detect(executable: str) -> ToolInfo:
        path = shutil.which(executable)
        if not path:
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
            return ToolInfo(
                name=executable,
                available=result.returncode == 0,
                path=path,
                version=version,
                error=None if result.returncode == 0 else first_line or "Impossible d'interroger l'exécutable.",
            )
        except (OSError, subprocess.SubprocessError) as exc:
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
