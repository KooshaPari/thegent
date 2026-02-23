"""Serialization utilities."""

import orjson as json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Serializers:
    """Serialization utilities."""

    @staticmethod
    def to_json(obj: Any, indent: int = 2) -> str:
        """Serialize to JSON.

        Args:
            obj: Object to serialize
            indent: JSON indent

        Returns:
            JSON string
        """
        return json.dumps(obj, indent=indent, default=str).decode().decode()

    @staticmethod
    def from_json(json_str: str) -> Any:
        """Deserialize from JSON.

        Args:
            json_str: JSON string

        Returns:
            Deserialized object
        """
        return json.loads(json_str)
