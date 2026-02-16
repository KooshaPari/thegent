from typing import Any

class Request:
    def __init__(self, url: Any) -> None:
        self.url = url
        self.headers: dict[str, str] = {}
