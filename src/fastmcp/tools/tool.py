from typing import Any

class ToolResult(dict):
    def __init__(self, content: Any = None, structured_content: Any | None = None, meta: dict | None = None) -> None:
        super().__init__()
        if content is not None:
            self["content"] = content
        if structured_content is not None:
            self["structured_content"] = structured_content
        if meta is not None:
            self["meta"] = meta
