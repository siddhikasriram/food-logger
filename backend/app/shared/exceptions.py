class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message, status_code=409)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service temporarily unavailable") -> None:
        super().__init__(message, status_code=503)
