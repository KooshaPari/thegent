"""Install-time model and enum definitions."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class InstallMode(StrEnum):
    SMART = "smart"
    EDITABLE = "editable"
    FORCE = "force"
    INTERACTIVE = "interactive"
    UNDO = "undo"


class FileAction(StrEnum):
    COPIED = "copied"
    SYMLINKED = "symlinked"
    SKIPPED = "skipped"
    BACKED_UP = "backed_up"
    REMOVED = "removed"
    CONFLICT = "conflict"
    ERROR = "error"


class FileManifest(BaseModel):
    source: str
    target: str
    mode: str  # "copy" or "symlink"
    mtime: float
    backup: str | None = None
    checksum: str | None = None


class ConfigManifest(BaseModel):
    file_path: str
    key: str
    original_value: Any = None
    new_value: Any = None


class InstallManifest(BaseModel):
    version: int = 1
    installed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    files: dict[str, FileManifest] = {}
    configs: list[ConfigManifest] = []


class BundleItem(BaseModel):
    source: str
    target: str
    mode: str = ""
    pin: str | None = None
    checksum: str | None = None


class BundleManifest(BaseModel):
    """Optional external manifest describing installable third-party bundles."""

    bundles: dict[str, list[BundleItem]] = {}
