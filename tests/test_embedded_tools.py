from app.services.tool_detection_service import ToolDetectionService


def test_bundled_windows_tools_take_priority_over_path(tmp_path, monkeypatch):
    from unittest.mock import patch

    tools = tmp_path / "tools" / "windows"
    tools.mkdir(parents=True)
    ffprobe = tools / "ffprobe.exe"
    ffprobe.write_bytes(b"portable")
    monkeypatch.setenv("FLET_ASSETS_DIR", str(tmp_path))
    with patch.object(ToolDetectionService, "_binary_name", side_effect=lambda name: name + ".exe"), \
         patch("app.services.tool_detection_service.shutil.which", return_value="system-ffprobe"):
        assert ToolDetectionService.resolve_executable("ffprobe") == str(ffprobe)
        assert ToolDetectionService.resolve_executable("ffmpeg") == "system-ffprobe"
