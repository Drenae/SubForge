from app.services.logging_service import LoggingService


def test_log_path_uses_subforge_filename():
    assert LoggingService.log_path().name == "subforge.log"
