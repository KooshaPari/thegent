"""Schema base - STUB."""

from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class Schema:
    name: str
    version: str
    fields: dict[str, Any]

    def validate(self, data, *args, **kwargs) -> bool:
        return True


__all__ = ["Schema"]
