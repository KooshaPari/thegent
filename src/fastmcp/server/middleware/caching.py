from dataclasses import dataclass
from collections.abc import Sequence

@dataclass
class CallToolSettings:
    included_tools: Sequence[str] | None = None
    ttl: int = 0

class ResponseCachingMiddleware:
    def __init__(self, call_tool_settings: CallToolSettings | None = None) -> None:
        self.call_tool_settings = call_tool_settings
