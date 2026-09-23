import asyncio
import shutil
import subprocess

import pytest

from app.models.subtitle_track import SubtitleTrack
from app.services.extraction_service import ExtractionJob, ExtractionService


def test_output_name_and_unsupported_codec():
    from pathlib import Path
    job = ExtractionJob(Path("Loki.S01E01.mkv"), SubtitleTrack(4, "hdmv_pgs_subtitle", "fra", forced=True))
    assert ExtractionService.output_name(job) == "Loki.S01E01_fra_FORCED_HDMV_PGS_SUBTITLE_s4.sup"
    with pytest.raises(ValueError):
        ExtractionService.output_name(ExtractionJob(job.source, SubtitleTrack(5, "unknown")))


def test_ffmpeg_copies_subtitle_and_never_overwrites(tmp_path):
    if not shutil.which("ffmpeg"):
        pytest.skip("FFmpeg absent")
    srt = tmp_path / "episode.srt"
    srt.write_text("1\n00:00:01,000 --> 00:00:02,000\nBonjour !\n", encoding="utf-8")
    source = tmp_path / "episode.mkv"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(srt), "-c:s", "copy", str(source)], check=True)
    output_dir = tmp_path / "sortie"
    output_dir.mkdir()
    job = ExtractionJob(source, SubtitleTrack(0, "subrip", "fra"))

    async def run():
        first = await ExtractionService.extract(job, output_dir)
        second = await ExtractionService.extract(job, output_dir)
        assert first != second
        assert first.read_bytes() == second.read_bytes()

    asyncio.run(run())
