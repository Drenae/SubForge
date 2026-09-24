import asyncio
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageOps

from app.models.ocr_cue import OcrCue
from app.services.pgs_service import PgsService


class OcrError(RuntimeError):
    pass


class OcrService:
    _engine = None

    @staticmethod
    def _lines(image: Image.Image) -> list[Image.Image]:
        alpha = np.asarray(image.getchannel("A")) > 12
        active = np.flatnonzero(alpha.any(axis=1))
        if not len(active):
            return []
        spans = []
        start = previous = int(active[0])
        for row in active[1:]:
            row = int(row)
            if row - previous >= 9:
                spans.append((start, previous + 1))
                start = row
            previous = row
        spans.append((start, previous + 1))
        lines = []
        for top, bottom in spans:
            columns = np.flatnonzero(alpha[top:bottom].any(axis=0))
            if len(columns):
                left, right = int(columns[0]), int(columns[-1]) + 1
                lines.append(image.crop((max(0, left - 3), max(0, top - 3),
                                         min(image.width, right + 3), min(image.height, bottom + 3))))
        return lines

    @staticmethod
    def _prepare(image: Image.Image) -> np.ndarray:
        base = Image.new("RGBA", image.size, "white")
        base.alpha_composite(image)
        gray = ImageOps.autocontrast(ImageOps.grayscale(base.convert("RGB")))
        enlarged = gray.resize((gray.width * 2, gray.height * 2), Image.Resampling.LANCZOS)
        return np.asarray(enlarged.convert("RGB"))

    @classmethod
    def _recognize_sync(cls, image: Image.Image) -> tuple[str, float | None]:
        try:
            import rapidocr
            from rapidocr import RapidOCR

            if cls._engine is None:
                model_dir = Path(rapidocr.__file__).resolve().parent / "models"
                models = {
                    "Det.model_path": model_dir / "PP-OCRv6_det_small.onnx",
                    "Cls.model_path": model_dir / "ch_ppocr_mobile_v2.0_cls_mobile.onnx",
                    "Rec.model_path": model_dir / "PP-OCRv6_rec_small.onnx",
                }
                missing = [path.name for path in models.values() if not path.is_file()]
                if missing:
                    raise OcrError(f"Modèles OCR absents du paquet : {', '.join(missing)}")
                cls._engine = RapidOCR(params={
                    "Global.use_det": False,
                    "Global.use_cls": False,
                    **{key: str(path) for key, path in models.items()},
                })
            texts = []
            scores = []
            for line in cls._lines(image):
                result = cls._engine(cls._prepare(line))
                if result.txts:
                    texts.append(" ".join(result.txts))
                if result.scores:
                    scores.extend(result.scores)
        except Exception as exc:
            raise OcrError(f"Moteur OCR intégré indisponible : {exc}") from exc
        return "\n".join(texts), (sum(scores) / len(scores) * 100 if scores else None)

    @classmethod
    async def recognize(cls, image: Image.Image) -> tuple[str, float | None]:
        return await asyncio.to_thread(cls._recognize_sync, image)

    @classmethod
    async def convert(cls, source: Path,
                      progress: Callable[[int], None] | None = None) -> list[OcrCue]:
        if source.suffix.casefold() != ".sup" or not source.is_file():
            raise OcrError("Choisissez un fichier PGS .sup accessible.")
        cues = []
        frames = PgsService.read(source)
        while frame := await asyncio.to_thread(lambda: next(frames, None)):
            text, confidence = await cls.recognize(frame.image)
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
