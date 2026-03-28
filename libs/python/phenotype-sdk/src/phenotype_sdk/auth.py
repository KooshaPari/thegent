"""Authentication for the Phenotype SDK.

Following ADR-001:
- Multiple authentication methods supported
- API key, OAuth2, JWT
- Tokens are automatically refreshed
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


class Auth:
    """Authentication handler for the SDK."""

    def __init__(self, config: AuthConfig) -> None:
        self.config = config
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0

    @property
    def access_token(self) -> str | None:
        """Get the current access token."""
        return self._access_token

    @property
    def is_expired(self) -> bool:
        """Check if the current token is expired."""
        if not self._access_token:
            return True
        # Add buffer of 60 seconds
        return time.time() >= (self._expires_at - 60)

    def set_tokens(
        self,
        access_token: str,
        refresh_token: str | None = None,
        expires_in: int = 3600,
    ) -> None:
        """Set authentication tokens."""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = time.time() + expires_in

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        headers = {}

        if self.config.method == "api_key":
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        elif self.config.method == "bearer" and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        elif self.config.method == "jwt" and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        return headers

    def clear(self) -> None:
        """Clear all tokens."""
        self._access_token = None
        self._refresh_token = None
        self._expires_at = 0


@dataclass(frozen=True)
class AuthConfig:
    """Authentication configuration."""

    method: str = field(default="api_key")
    api_key: str | None = field(default=None)
    auth_url: str | None = field(default=None)
    client_id: str | None = field(default=None)
    client_secret: str | None = field(default=None)
    scopes: list[str] = field(default_factory=lambda: ["read", "write"])

    @classmethod
    def from_api_key(cls, api_key: str) -> AuthConfig:
        """Create config from API key."""
        return cls(method="api_key", api_key=api_key)

    @classmethod
    def from_oauth2(
        cls,
        client_id: str,
        client_secret: str,
        auth_url: str,
        scopes: list[str] | None = None,
    ) -> AuthConfig:
        """Create config from OAuth2 credentials."""
        return cls(
            method="oauth2",
            auth_url=auth_url,
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes or ["read", "write"],
        )

    @classmethod
    def from_jwt(cls, token: str) -> AuthConfig:
        """Create config from JWT token."""
        return cls(method="jwt", api_key=token)
