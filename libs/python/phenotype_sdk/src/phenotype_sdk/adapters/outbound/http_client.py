"""HTTP client adapter for remote configuration service."""

import httpx
from typing import Any, AsyncIterator

from phenotype_sdk.domain.entities import ConfigEntry
from phenotype_sdk.domain.ports import ConfigRepository
from phenotype_sdk.domain.value_objects import ConfigValue, ValueType


class HttpConfigClient(ConfigRepository):
    """
    HTTP adapter for configuration repository.

    Implements the ConfigRepository port (Hexagonal: Driven Adapter).
    Handles HTTP communication with the configuration service.
    """

    def __init__(self, base_url: str, api_key: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def get(self, key: str) -> ConfigEntry | None:
        """Retrieve a configuration entry from the remote service."""
        response = await self._client.get(f"{self._base_url}/api/v1/config/{key}")
        if response.status_code == 404:
            return None
        response.raise_for_status()

        data = response.json()
        return self._deserialize_entry(data)

    async def save(self, entry: ConfigEntry) -> ConfigEntry:
        """Save a configuration entry to the remote service."""
        response = await self._client.post(
            f"{self._base_url}/api/v1/config",
            json=self._serialize_entry(entry),
        )
        response.raise_for_status()
        return self._deserialize_entry(response.json())

    async def delete(self, key: str) -> bool:
        """Delete a configuration entry from the remote service."""
        response = await self._client.delete(f"{self._base_url}/api/v1/config/{key}")
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True

    async def list(self, prefix: str | None = None) -> AsyncIterator[ConfigEntry]:
        """List all configuration entries from the remote service."""
        params = {"prefix": prefix} if prefix else {}
        response = await self._client.get(f"{self._base_url}/api/v1/config", params=params)
        response.raise_for_status()

        for item in response.json()["items"]:
            yield self._deserialize_entry(item)

    @staticmethod
    def _serialize_entry(entry: ConfigEntry) -> dict[str, Any]:
        """Serialize domain entity to JSON for API."""
        return {
            "key": entry.key,
            "value": entry.value.raw,
            "value_type": entry.value.value_type.value,
            "version": entry.version,
            "metadata": entry.metadata,
        }

    @staticmethod
    def _deserialize_entry(data: dict[str, Any]) -> ConfigEntry:
        """Deserialize JSON from API to domain entity."""
        from datetime import datetime
        from uuid import UUID

        return ConfigEntry(
            key=data["key"],
            value=ConfigValue(raw=data["value"], value_type=ValueType(data["value_type"])),
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
            id=UUID(data["id"]),
        )
