from unittest.mock import patch

from app.services.tool_detection_service import ToolDetectionService


def test_tesseract_version():
    assert ToolDetectionService._extract_version("tesseract 5.5.0.20241111") == "5.5.0.20241111"


def test_windows_standard_install_detected_even_when_not_in_path(tmp_path, monkeypatch):
    executable = tmp_path / "Tesseract-OCR" / "tesseract.exe"
    executable.parent.mkdir()
    executable.write_bytes(b"exe")
    monkeypatch.setenv("ProgramFiles", str(tmp_path))
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    with patch("app.services.tool_detection_service.sys.platform", "win32"), \
         patch("app.services.tool_detection_service.shutil.which", return_value=None):
        assert ToolDetectionService.resolve_executable("tesseract") == str(executable)
