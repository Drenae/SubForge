import asyncio
import json
import subprocess
from pathlib import Path

from app.models.subtitle_track import SubtitleTrack
from app.services.tool_detection_service import ToolDetectionService


class FFprobeError(Exception):
    pass


class FFprobeService:
    @staticmethod
    def parse_tracks(payload: str) -> list[SubtitleTrack]:
        try:
            document = json.loads(payload)
            streams = document["streams"]
            if not isinstance(streams, list):
                raise ValueError("Liste des pistes invalide")
            tracks = []
            for stream in streams:
                if not isinstance(stream, dict) or stream.get("codec_type") != "subtitle":
                    continue
                tags = stream.get("tags") or {}
                disposition = stream.get("disposition") or {}
                if not isinstance(tags, dict) or not isinstance(disposition, dict):
                    raise ValueError("Métadonnées de piste invalides")
                tracks.append(SubtitleTrack(
                    index=int(stream["index"]),
                    codec=str(stream.get("codec_name") or "inconnu"),
                    language=str(tags.get("language")) if tags.get("language") else None,
                    title=str(tags.get("title")) if tags.get("title") else None,
                    forced=str(disposition.get("forced", 0)).lower() in {"1", "true"},
                    default=str(disposition.get("default", 0)).lower() in {"1", "true"},
                    tags={str(k): str(v) for k, v in tags.items()},
                ))
            return tracks
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            raise FFprobeError("Réponse FFprobe invalide") from exc

    @staticmethod
    async def analyze(path: Path) -> list[SubtitleTrack]:
        executable = ToolDetectionService.resolve_executable("ffprobe")
        if not executable:
            raise FFprobeError("FFprobe est introuvable. Vérifiez les Paramètres.")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            process = await asyncio.create_subprocess_exec(
                executable, "-v", "error", "-show_entries", "stream", "-of", "json", str(path),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                creationflags=flags,
            )
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            except asyncio.TimeoutError as exc:
                process.kill()
                await process.communicate()
                raise FFprobeError("Délai d'analyse FFprobe dépassé") from exc
        except OSError as exc:
            raise FFprobeError(f"Impossible de lancer FFprobe : {exc}") from exc
        if process.returncode != 0:
            raise FFprobeError(stderr.decode("utf-8", errors="replace").strip() or "Analyse FFprobe échouée")
        return FFprobeService.parse_tracks(stdout.decode("utf-8", errors="replace"))
