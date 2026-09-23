from app.services.tool_detection_service import ToolDetectionService


def test_extract_ffmpeg_version():
    line = "ffmpeg version 7.1-full_build-www.gyan.dev Copyright"
    assert ToolDetectionService._extract_version(line) == "7.1-full_build-www.gyan.dev"


def test_extract_ffprobe_version():
    line = "ffprobe version 7.1-full_build-www.gyan.dev Copyright"
    assert ToolDetectionService._extract_version(line) == "7.1-full_build-www.gyan.dev"


def test_extract_version_returns_none_for_empty_output():
    assert ToolDetectionService._extract_version("") is None
