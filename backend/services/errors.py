class ServiceError(Exception):
    """A rule was broken. `message` is plain language, safe to show to the
    operator and to return from the MCP server as-is."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


class NotFound(ServiceError):
    def __init__(self, message: str):
        super().__init__(message, 404)


class Conflict(ServiceError):
    def __init__(self, message: str):
        super().__init__(message, 409)
