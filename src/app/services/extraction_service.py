import asyncio
import re
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.models.subtitle_track import SubtitleTrack
from app.services.logging_service import LoggingService
from app.services.tool_detection_service import ToolDetectionService


# Matroska subtitle-only container keeps VobSub/SSA packets without conversion.
CODEC_OUTPUT = {
    "hdmv_pgs_subtitle": ("sup", "sup"),
    "subrip": ("srt", "srt"),
    "ass": ("ass", "ass"),
    "ssa": ("matroska", "mks"),
    "dvd_subtitle": ("matroska", "mks"),
    "webvtt": ("webvtt", "vtt"),
}


@dataclass(frozen=True)
class ExtractionJob:
    source: Path
    track: SubtitleTrack


@dataclass(frozen=True)
class ExtractionResult:
    job: ExtractionJob
    output: Path | None = None
    error: str | None = None


class ExtractionService:
    _logger = LoggingService.get_logger("extraction")

    @staticmethod
    def output_name(job: ExtractionJob) -> str:
        codec = job.track.codec.casefold()
        if codec not in CODEC_OUTPUT:
            raise ValueError(f"Codec non pris en charge en copie directe : {job.track.codec}")
        extension = CODEC_OUTPUT[codec][1]
        language = job.track.language or "und"
        safe_language = re.sub(r"[^a-zA-Z0-9_-]", "_", language)[:20] or "und"
        safe_stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", job.source.stem).rstrip(" .") or "video"
        kind = "FORCED" if job.track.forced else "FULL"
        return f"{safe_stem}_{safe_language}_{kind}_{codec.upper()}_s{job.track.index}.{extension}"

    @staticmethod
    def _reserve(destination: Path, filename: str) -> Path:
        candidate = destination / filename
        for index in range(1, 10000):
            path = candidate if index == 1 else candidate.with_name(f"{candidate.stem}_{index}{candidate.suffix}")
            try:
                path.touch(exist_ok=False)
                return path
            except FileExistsError:
                continue
        raise OSError("Trop de fichiers portent le même nom")

    @staticmethod
    async def _duration(source: Path) -> float | None:
        executable = ToolDetectionService.resolve_executable("ffprobe")
        if not executable:
            return None
        try:
            process = await asyncio.create_subprocess_exec(
                executable, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(source),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            output, _ = await asyncio.wait_for(process.communicate(), timeout=20)
            duration = float(output.strip())
            return duration if duration > 0 and process.returncode == 0 else None
        except (OSError, ValueError, asyncio.TimeoutError):
            if "process" in locals() and process.returncode is None:
                process.kill()
                await process.communicate()
            return None

    @staticmethod
    def _progress_seconds(value: str) -> float | None:
        try:
            hours, minutes, seconds = value.split(":")
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        except ValueError:
            return None

    @classmethod
    async def extract(cls, job: ExtractionJob, destination: Path,
                      on_partial: Callable[[float | None], None] | None = None) -> Path:
        executable = ToolDetectionService.resolve_executable("ffmpeg")
        if not executable:
            raise RuntimeError("FFmpeg est introuvable. Vérifiez les Paramètres.")
        fmt = CODEC_OUTPUT.get(job.track.codec.casefold())
        if fmt is None:
            raise ValueError(f"Codec non pris en charge en copie directe : {job.track.codec}")
        if not destination.is_dir():
            raise ValueError("Dossier de destination introuvable ou inaccessible")
        output = cls._reserve(destination, cls.output_name(job))
        temporary = destination / f".subforge-{uuid.uuid4().hex}.part"
        process = None
        try:
            duration = await cls._duration(job.source) if on_partial else None
            if on_partial:
                on_partial(0.0 if duration else None)
            process = await asyncio.create_subprocess_exec(
                executable, "-nostdin", "-hide_banner", "-loglevel", "error", "-n",
                "-progress", "pipe:1", "-stats_period", "0.5",
                "-i", str(job.source), "-map", f"0:{job.track.index}", "-c:s", "copy",
                "-f", fmt[0], str(temporary),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            stderr_task = asyncio.create_task(process.stderr.read())
            try:
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    if on_partial and duration and line.startswith(b"out_time="):
                        seconds = cls._progress_seconds(line.partition(b"=")[2].decode("ascii", errors="replace").strip())
                        if seconds is not None:
                            on_partial(min(0.99, max(0.0, seconds / duration)))
                await process.wait()
                stderr = await stderr_task
            finally:
                if not stderr_task.done():
                    stderr_task.cancel()
            if process.returncode != 0:
                raise RuntimeError(stderr.decode("utf-8", errors="replace").strip() or "FFmpeg a échoué")
            if not temporary.is_file() or temporary.stat().st_size == 0:
                raise RuntimeError("FFmpeg n'a produit aucun sous-titre")
            temporary.replace(output)
            cls._logger.info("Extraction réussie : %s → %s", job.source, output)
            return output
        except BaseException:
            if process is not None and process.returncode is None:
                process.kill()
                await process.communicate()
            output.unlink(missing_ok=True)
            cls._logger.exception("Extraction échouée : %s piste %s", job.source, job.track.index)
            raise
        finally:
            temporary.unlink(missing_ok=True)

    @classmethod
    async def run_batch(cls, jobs: list[ExtractionJob], destination: Path,
                        cancelled: Callable[[], bool],
                        on_progress: Callable[[int, int, ExtractionResult], None],
                        on_partial: Callable[[int, int, float | None], None] | None = None) -> list[ExtractionResult]:
        results = []
        for job in jobs:
            if cancelled():
                break
            try:
                partial = (lambda fraction: on_partial(len(results), len(jobs), fraction)) if on_partial else None
                result = ExtractionResult(job, output=await cls.extract(job, destination, partial))
            except Exception as exc:
                result = ExtractionResult(job, error=str(exc))
            results.append(result)
            on_progress(len(results), len(jobs), result)
        return results
