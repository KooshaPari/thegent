"""Configuration for the Phenotype SDK.

Following ADR-001:
- Configuration is immutable after creation
- Environment variables are the primary source
- Validation happens at construction time
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Config:
    """SDK configuration.

    Configuration is immutable (frozen=True) to prevent
    accidental modification after creation.
    """

    # API Configuration
    base_url: str = field(default="https://api.phenotype.dev")
    api_version: str = field(default="v1")
    timeout_seconds: float = field(default=30.0)
    max_retries: int = field(default=3)

    # Authentication
    api_key: str | None = field(default=None)
    auth_url: str | None = field(default=None)

    # Connection
    max_connections: int = field(default=100)
    max_keepalive_connections: int = field(default=20)
    keepalive_expiry_seconds: float = field(default=5.0)

    # Logging
    log_level: str = field(default="INFO")
    log_format: Literal["json", "console"] = field(default="console")

    # Feature Flags
    enable_telemetry: bool = field(default=True)
    enable_metrics: bool = field(default=True)

    @classmethod
    def from_env(cls) -> Config:
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv("PHENOTYPE_BASE_URL", "https://api.phenotype.dev"),
            api_version=os.getenv("PHENOTYPE_API_VERSION", "v1"),
            timeout_seconds=float(os.getenv("PHENOTYPE_TIMEOUT", "30")),
            max_retries=int(os.getenv("PHENOTYPE_MAX_RETRIES", "3")),
            api_key=os.getenv("PHENOTYPE_API_KEY"),
            auth_url=os.getenv("PHENOTYPE_AUTH_URL"),
            max_connections=int(os.getenv("PHENOTYPE_MAX_CONNECTIONS", "100")),
            max_keepalive_connections=int(
                os.getenv("PHENOTYPE_MAX_KEEPALIVE_CONNECTIONS", "20")
            ),
            keepalive_expiry_seconds=float(
                os.getenv("PHENOTYPE_KEEPALIVE_EXPIRY", "5.0")
            ),
            log_level=os.getenv("PHENOTYPE_LOG_LEVEL", "INFO"),
            log_format=Literal[os.getenv("PHENOTYPE_LOG_FORMAT", "console")],
            enable_telemetry=os.getenv(
                "PHENOTYPE_ENABLE_TELEMETRY", "true"
            ).lower() == "true",
            enable_metrics=os.getenv(
                "PHENOTYPE_ENABLE_METRICS", "true"
            ).lower() == "true",
        )

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        """Create configuration from a dictionary."""
        # Filter to only known fields
        known_fields = {
            "base_url",
            "api_version",
            "timeout_seconds",
            "max_retries",
            "api_key",
            "auth_url",
            "max_connections",
            "max_keepalive_connections",
            "keepalive_expiry_seconds",
            "log_level",
            "log_format",
            "enable_telemetry",
            "enable_metrics",
        }
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def with_api_key(self, api_key: str) -> Config:
        """Create a new config with the given API key."""
        return Config(
            base_url=self.base_url,
            api_version=self.api_version,
            timeout_seconds=self.timeout_seconds,
            max_retries=self.max_retries,
            api_key=api_key,
            auth_url=self.auth_url,
            max_connections=self.max_connections,
            max_keepalive_connections=self.max_keepalive_connections,
            keepalive_expiry_seconds=self.keepalive_expiry_seconds,
            log_level=self.log_level,
            log_format=self.log_format,
            enable_telemetry=self.enable_telemetry,
            enable_metrics=self.enable_metrics,
        )

    @property
    def api_base_url(self) -> str:
        """Get the full API base URL."""
        return f"{self.base_url}/{self.api_version}"

    def validate(self) -> list[str]:
        """Validate the configuration.

        Returns a list of validation errors (empty if valid).
        """
        errors = []

        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")

        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")

        if self.max_connections <= 0:
            errors.append("max_connections must be positive")

        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            errors.append(f"Invalid log_level: {self.log_level}")

        if self.log_format not in {"json", "console"}:
            errors.append(f"Invalid log_format: {self.log_format}")

        return errors
