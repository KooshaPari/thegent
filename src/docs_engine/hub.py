"""Hub - STUB."""

from typing import Any, Dict, List, Optional


class DocsHub:
    def __init__(self, *args, **kwargs):
        pass

    def register(self, doc, *args, **kwargs):
        pass

    def get(self, doc_id, *args, **kwargs) -> Optional[dict[str, Any]]:
        return None

    def list_all(self, *args, **kwargs) -> list[dict[str, Any]]:
        return []


__all__ = ["DocsHub"]
