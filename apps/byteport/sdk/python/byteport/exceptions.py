"""BytePort exceptions"""


class BytePortError(Exception):
    """Base exception for BytePort SDK"""

    def __init__(self, message: str, status_code: int = 0, details: str = ""):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.details:
            return f"BytePort API error (status {self.status_code}): {self.message} - {self.details}"
        return f"BytePort API error (status {self.status_code}): {self.message}"


class NotFoundError(BytePortError):
    """Resource not found error"""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message, 404, details)


class BadRequestError(BytePortError):
    """Bad request error"""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message, 400, details)


class ServerError(BytePortError):
    """Server error"""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message, 500, details)
