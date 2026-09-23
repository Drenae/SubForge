from app.services.logging_service import LoggingService


class ErrorService:
    _logger = LoggingService.get_logger("errors")

    @classmethod
    def capture(cls, error: Exception, context: str = "") -> str:
        message = str(error) or error.__class__.__name__
        cls._logger.exception("%s%s", f"{context}: " if context else "", message)
        return message
