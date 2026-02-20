"""Syncthing workspace synchronization for thegent compute offloading."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class SyncthingError(Exception):
    """Raised when a Syncthing API operation fails."""


@dataclass
class SyncthingDevice:
    """Represents a Syncthing peer device."""

    device_id: str
    name: str
    is_connected: bool


@dataclass
class SyncthingFolder:
    """Represents a Syncthing shared folder."""

    folder_id: str
    path: str
    label: str
    devices: list[str] = field(default_factory=list)


class SyncthingConfig(BaseSettings):
    """Configuration for the Syncthing API client.

    Reads from environment variables:
      THGENT_SYNCTHING_API_KEY — Syncthing GUI/API key
      THGENT_SYNCTHING_URL     — Base URL of the Syncthing REST API
    """

    api_key: str | None = Field(None, alias="THGENT_SYNCTHING_API_KEY")
    base_url: str = Field("http://localhost:8384", alias="THGENT_SYNCTHING_URL")

    model_config = {"populate_by_name": True}


class SyncthingManager:
    """Manages Syncthing workspace synchronisation via its REST API.

    All network calls use ``httpx.AsyncClient``.  The client is created
    lazily and reused across calls.  Call :meth:`close` (or use the
    async context manager) to release the underlying connection pool.

    Args:
        config: Optional :class:`SyncthingConfig` instance.  If *None*,
            a default instance is created (reads from environment).
    """

    def __init__(self, config: SyncthingConfig | None = None) -> None:
        self._config = config or SyncthingConfig()
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        """Return (creating if necessary) the shared ``httpx.AsyncClient``."""
        if self._client is None or self._client.is_closed:
            headers: dict[str, str] = {}
            if self._config.api_key:
                headers["X-API-Key"] = self._config.api_key
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
                headers=headers,
                timeout=10.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> SyncthingManager:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, **params: Any) -> Any:
        """Perform a GET request and return parsed JSON.

        Args:
            path: API path (e.g. ``/rest/config/devices``).
            **params: Query-string parameters.

        Raises:
            SyncthingError: On HTTP error or connection failure.
        """
        client = self._get_client()
        try:
            resp = await client.get(path, params=params or None)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise SyncthingError(
                f"Syncthing API error {exc.response.status_code} for {path}: "
                f"{exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise SyncthingError(
                f"Syncthing connection error for {path}: {exc}"
            ) from exc

    async def _post(self, path: str, json: Any = None) -> Any:
        """Perform a POST request and return parsed JSON (if any).

        Args:
            path: API path.
            json: Request body, serialised to JSON.

        Raises:
            SyncthingError: On HTTP error or connection failure.
        """
        client = self._get_client()
        try:
            resp = await client.post(path, json=json)
            resp.raise_for_status()
            # Some Syncthing endpoints return empty bodies on success
            if resp.content:
                return resp.json()
            return None
        except httpx.HTTPStatusError as exc:
            raise SyncthingError(
                f"Syncthing API error {exc.response.status_code} for {path}: "
                f"{exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise SyncthingError(
                f"Syncthing connection error for {path}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def is_available(self) -> bool:
        """Return *True* if the Syncthing daemon is reachable and healthy.

        Uses the unauthenticated ``/rest/noauth/health`` endpoint so that
        availability can be checked even without an API key.

        Returns:
            ``True`` if health check succeeds, ``False`` otherwise.
        """
        client = self._get_client()
        try:
            resp = await client.get("/rest/noauth/health")
            resp.raise_for_status()
            data = resp.json()
            return str(data.get("status", "")).lower() == "ok"
        except (httpx.HTTPStatusError, httpx.RequestError, ValueError):
            return False

    async def get_devices(self) -> list[SyncthingDevice]:
        """List all configured Syncthing devices.

        Returns:
            List of :class:`SyncthingDevice` instances.

        Raises:
            SyncthingError: On API or connection error.
        """
        raw: list[dict[str, Any]] = await self._get("/rest/config/devices")
        devices: list[SyncthingDevice] = []
        for item in raw:
            device_id = item.get("deviceID", "")
            name = item.get("name", "") or device_id
            # ``paused`` is the inverse of connected in config; runtime
            # connection state is not available from the config endpoint.
            is_connected = not item.get("paused", False)
            devices.append(
                SyncthingDevice(
                    device_id=device_id,
                    name=name,
                    is_connected=is_connected,
                )
            )
        logger.debug("Retrieved %d Syncthing devices", len(devices))
        return devices

    async def get_folders(self) -> list[SyncthingFolder]:
        """List all configured Syncthing folders.

        Returns:
            List of :class:`SyncthingFolder` instances.

        Raises:
            SyncthingError: On API or connection error.
        """
        raw: list[dict[str, Any]] = await self._get("/rest/config/folders")
        folders: list[SyncthingFolder] = []
        for item in raw:
            folder_id = item.get("id", "")
            path = item.get("path", "")
            label = item.get("label", "") or folder_id
            device_ids = [
                d.get("deviceID", "")
                for d in item.get("devices", [])
                if d.get("deviceID")
            ]
            folders.append(
                SyncthingFolder(
                    folder_id=folder_id,
                    path=path,
                    label=label,
                    devices=device_ids,
                )
            )
        logger.debug("Retrieved %d Syncthing folders", len(folders))
        return folders

    async def add_folder(
        self,
        folder_id: str,
        path: str,
        label: str,
        device_ids: list[str],
    ) -> bool:
        """Add a new folder to the Syncthing configuration.

        Args:
            folder_id: Unique folder identifier (Syncthing folder ID).
            path: Absolute filesystem path for the folder.
            label: Human-readable label for the folder.
            device_ids: List of device IDs to share the folder with.

        Returns:
            ``True`` if the folder was added successfully.

        Raises:
            SyncthingError: On API or connection error.
        """
        payload: dict[str, Any] = {
            "id": folder_id,
            "path": path,
            "label": label,
            "devices": [{"deviceID": did} for did in device_ids],
        }
        await self._post("/rest/config/folders", json=payload)
        logger.info(
            "Added Syncthing folder %r at %r shared with %d device(s)",
            folder_id,
            path,
            len(device_ids),
        )
        return True

    async def sync_status(self, folder_id: str) -> dict[str, Any]:
        """Return the current sync status for a folder.

        Args:
            folder_id: The Syncthing folder ID to query.

        Returns:
            Raw status dict from ``/rest/db/status``.  Keys include
            ``"state"``, ``"needBytes"``, ``"inSyncFiles"``, etc.

        Raises:
            SyncthingError: On API or connection error.
        """
        data: dict[str, Any] = await self._get(
            "/rest/db/status", folder=folder_id
        )
        logger.debug(
            "Sync status for folder %r: state=%r", folder_id, data.get("state")
        )
        return data
