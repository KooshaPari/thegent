class ResponseLimitingMiddleware:
    def __init__(self, max_size: int = 1024 * 1024) -> None:
        self.max_size = max_size
