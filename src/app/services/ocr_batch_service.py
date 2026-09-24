import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.services.extraction_service import ExtractionJob, ExtractionService
from app.services.ocr_service import OcrService
from app.services.logging_service import LoggingService


@dataclass(frozen=True)
class OcrBatchResult:
    job: ExtractionJob
    output: Path | None = None
    count: int = 0
    uncertain: int = 0
    error: str | None = None


class OcrBatchService:
    _logger = LoggingService.get_logger("ocr_batch")

    @staticmethod
    def save_srt(destination: Path, stem: str, text: str) -> Path:
        if not destination.is_dir():
            raise ValueError("Dossier de destination introuvable ou inaccessible")
        for number in range(1, 10000):
            name = f"{stem}.srt" if number == 1 else f"{stem}_{number}.srt"
            output = destination / name
            try:
                with output.open("x", encoding="utf-8", newline="\n") as handle:
                    handle.write(text)
                return output
            except FileExistsError:
                continue
            except BaseException:
                output.unlink(missing_ok=True)
                raise
        raise OSError("Trop de fichiers portent le même nom")

    @classmethod
    async def run(cls, jobs: list[ExtractionJob], destination: Path,
                  cancelled: Callable[[], bool],
                  on_progress: Callable[[int, int, int, OcrBatchResult | None], None]) -> list[OcrBatchResult]:
        results = []
        for job in jobs:
            if cancelled():
                break
            try:
                with tempfile.TemporaryDirectory(prefix="subforge-batch-") as folder:
                    sup = await ExtractionService.extract(job, Path(folder))
                    cues = await OcrService.convert(
                        sup, lambda count: on_progress(len(results), len(jobs), count, None),
                    )
                    uncertain = sum(cue.confidence is None or cue.confidence < 65 or not cue.text.strip()
                                    for cue in cues)
                    output = cls.save_srt(destination, sup.stem, OcrService.to_srt(cues))
                    result = OcrBatchResult(job, output=output, count=len(cues), uncertain=uncertain)
                    cls._logger.info("OCR réussi : %s piste %d → %s (%d à vérifier)",
                                     job.source, job.track.index, output, uncertain)
            except Exception as exc:
                cls._logger.exception("OCR échoué : %s piste %d", job.source, job.track.index)
                result = OcrBatchResult(job, error=str(exc))
            results.append(result)
            on_progress(len(results), len(jobs), 0, result)
        return results
