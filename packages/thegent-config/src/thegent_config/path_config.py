"""Path and directory configuration settings for thegent.

Settings related to filesystem paths and directory locations.
"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from thegent_config.defaults import expanded_path_factory


class PathConfig(BaseSettings):
    """Filesystem path and directory configuration."""

    model_config = SettingsConfigDict(
        env_prefix="THGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Factory directories
    factory_skills_dir: Path = Field(
        default_factory=expanded_path_factory("~/.factory/skills"),
        description="Factory skills directory",
    )
    factory_droids_dir: Path = Field(
        default_factory=expanded_path_factory("~/.factory/droids"),
        description="Factory droids directory",
    )

    # Cache and session directories
    cache_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cache/thegent"),
        description="Global cache directory for thegent",
    )
    session_dir: Path = Field(
        default_factory=expanded_path_factory("~/.cache/thegent/sessions"),
        description="Session metadata/log directory for background runs",
    )

    # Working directory
    cwd: Path | None = Field(
        default=None,
        description="Working directory (inferred or explicit)",
    )

    # Session management paths
    session_meta_path: Path | None = Field(
        default=None,
        description="Session metadata path override",
    )
    session_rc_path: Path | None = Field(
        default=None,
        description="Session rc path override",
    )
    health_snapshot_path: Path | None = Field(
        default=None,
        description="Health snapshot path",
    )
    fifo_path: Path | None = Field(
        default=None,
        description="Override path for stdin FIFO",
    )
    holdpty_socket_dir: Path | None = Field(
        default=None,
        description="Directory for holdpty sockets",
    )

    # MCP storage
    mcp_storage_dir: Path | None = Field(
        default=None,
        description="MCP storage directory override",
    )

    # Connector mapping cache
    connector_mapping_cache_path: Path | None = Field(
        default=None,
        description="Path override for connector mapping cache",
    )
