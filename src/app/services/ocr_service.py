import asyncio
import csv
import io
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from PIL import Image, ImageOps

from app.models.ocr_cue import OcrCue
from app.services.pgs_service import PgsService
from app.services.tool_detection_service import ToolDetectionService


class OcrError(RuntimeError):
    pass


class OcrService:
    @staticmethod
    async def languages() -> list[str]:
        executable = ToolDetectionService.resolve_executable("tesseract")
        if not executable:
            return []
        process = await asyncio.create_subprocess_exec(
            executable, "--list-langs", stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output, _ = await process.communicate()
        return [line.strip() for line in output.decode("utf-8", errors="replace").splitlines()
                if line.strip() and not line.startswith("List of available languages")]

    @staticmethod
    def parse_tsv(payload: str) -> tuple[str, float | None]:
        lines: dict[tuple[str, str, str], list[str]] = {}
        confidence = []
        for row in csv.DictReader(io.StringIO(payload), delimiter="\t"):
            word = (row.get("text") or "").strip()
            if not word:
                continue
            key = (row.get("block_num", ""), row.get("par_num", ""), row.get("line_num", ""))
            lines.setdefault(key, []).append(word)
            try:
                value = float(row.get("conf", "-1"))
                if value >= 0:
                    confidence.append(value)
            except ValueError:
                pass
        return "\n".join(" ".join(words) for words in lines.values()), (
            sum(confidence) / len(confidence) if confidence else None)

    @staticmethod
    def _prepare(image: Image.Image, path: Path) -> None:
        base = Image.new("RGBA", image.size, "white")
        base.alpha_composite(image)
        gray = ImageOps.autocontrast(ImageOps.grayscale(base.convert("RGB")))
        gray.resize((gray.width * 2, gray.height * 2), Image.Resampling.LANCZOS).save(path)

    @classmethod
    async def recognize(cls, image: Image.Image, language: str) -> tuple[str, float | None]:
        executable = ToolDetectionService.resolve_executable("tesseract")
        if not executable:
            raise OcrError("Tesseract est introuvable. Installez-le avec la langue souhaitée, puis redémarrez SubForge.")
        with tempfile.TemporaryDirectory(prefix="subforge-ocr-") as folder:
            path = Path(folder) / "cue.png"
            await asyncio.to_thread(cls._prepare, image, path)
            process = await asyncio.create_subprocess_exec(
                executable, str(path), "stdout", "-l", language, "--psm", "6", "tsv",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            except asyncio.TimeoutError as exc:
                process.kill()
                await process.communicate()
                raise OcrError("Délai OCR dépassé") from exc
            if process.returncode != 0:
                raise OcrError(stderr.decode("utf-8", errors="replace").strip() or "Tesseract a échoué")
            return cls.parse_tsv(stdout.decode("utf-8", errors="replace"))

    @classmethod
    async def convert(cls, source: Path, language: str,
                      progress: Callable[[int], None] | None = None) -> list[OcrCue]:
        if source.suffix.casefold() != ".sup" or not source.is_file():
            raise OcrError("Choisissez un fichier PGS .sup accessible.")
        executable = ToolDetectionService.resolve_executable("tesseract")
        if not executable:
            raise OcrError("Tesseract est introuvable. Installez-le avec la langue souhaitée, puis redémarrez SubForge.")
        available = await cls.languages()
        if language not in available:
            raise OcrError(f"Langue OCR {language} absente. Installez {language}.traineddata dans "
                           f"le dossier tessdata de Tesseract (langues trouvées : {', '.join(available) or 'aucune'}).")
        cues = []
        frames = PgsService.read(source)
        while frame := await asyncio.to_thread(lambda: next(frames, None)):
            text, confidence = await cls.recognize(frame.image, language)
            cues.append(OcrCue(frame.start_ms, frame.end_ms, text, confidence))
            if progress:
                progress(len(cues))
        if not cues:
            raise OcrError("Aucun sous-titre PGS complet n'a été trouvé.")
        return cues

    @staticmethod
    def _timestamp(ms: int) -> str:
        hours, rest = divmod(max(0, ms), 3600000)
        minutes, rest = divmod(rest, 60000)
        seconds, milliseconds = divmod(rest, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    @classmethod
    def to_srt(cls, cues: list[OcrCue]) -> str:
        return "".join(f"{index}\n{cls._timestamp(cue.start_ms)} --> {cls._timestamp(cue.end_ms)}\n"
                       f"{cue.text.strip()}\n\n" for index, cue in enumerate(cues, 1))
