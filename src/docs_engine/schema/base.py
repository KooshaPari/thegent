"""Schema base - STUB."""
from dataclasses import dataclass
from typing import Any


@dataclass
class Schema:
    name: str
    version: str
    fields: dict[str, Any]
    def validate(self, data, *args, **kwargs) -> bool: return True
__all__ = ["Schema"]
