import asyncio
from pathlib import Path
from unittest.mock import patch

from app.models.ocr_cue import OcrCue
from app.models.subtitle_track import SubtitleTrack
from app.services.extraction_service import ExtractionJob
from app.services.ocr_batch_service import OcrBatchService


def test_batch_continues_after_failure_and_never_overwrites(tmp_path):
    source = tmp_path / "episode.mkv"
    jobs = [ExtractionJob(source, SubtitleTrack(index, "hdmv_pgs_subtitle", "fra"))
            for index in (2, 3)]
    existing = tmp_path / "episode_fra_FULL_HDMV_PGS_SUBTITLE_s2.srt"
    existing.write_text("original", encoding="utf-8")
    progress = []

    async def fake_extract(job, folder):
        if job.track.index == 3:
            raise RuntimeError("échec simulé")
        sup = folder / "episode_fra_FULL_HDMV_PGS_SUBTITLE_s2.sup"
        sup.write_bytes(b"PGS")
        return sup

    async def fake_convert(source, language, callback):
        callback(1)
        return [OcrCue(1000, 2000, "Bonjour", 50)]

    with patch("app.services.ocr_batch_service.ExtractionService.extract", side_effect=fake_extract), \
         patch("app.services.ocr_batch_service.OcrService.convert", side_effect=fake_convert):
        results = asyncio.run(OcrBatchService.run(
            jobs, tmp_path, "fra", lambda: False, lambda *args: progress.append(args)))

    assert results[0].output.name.endswith("_2.srt")
    assert "Bonjour" in results[0].output.read_text(encoding="utf-8")
    assert results[0].uncertain == 1
    assert existing.read_text(encoding="utf-8") == "original"
    assert results[1].error == "échec simulé"
    assert progress[-1][:2] == (2, 2)
