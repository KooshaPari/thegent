"""Authentication helpers for the MCP server."""

from __future__ import annotations

import functools

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from phenotype_thegent_core.config import ThegentSettings


@functools.lru_cache(maxsize=1)
def get_settings() -> ThegentSettings:
    """Return the process-wide ThegentSettings singleton."""
    return ThegentSettings()


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """G-FM-01: Bearer token authentication for MCP HTTP endpoints."""

    _settings: ThegentSettings | None = None

    @classmethod
    def reload_settings(cls) -> None:
        """Reset the cached settings so the next request rebuilds them."""
        cls._settings = None

    async def dispatch(self, request: Request, call_next):
        if BearerAuthMiddleware._settings is None:
            BearerAuthMiddleware._settings = get_settings()
        settings = BearerAuthMiddleware._settings
        if settings.mcp_auth_mode == "bearer":
            if request.url.path == "/health":
                return await call_next(request)

            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return JSONResponse({"error": "Missing or invalid Authorization"}, status_code=401)
            token = auth[7:]
            valid_tokens = [t.strip() for t in settings.mcp_bearer_tokens.split(",") if t.strip()]
            if token not in valid_tokens:
                return JSONResponse({"error": "Invalid token"}, status_code=401)
        return await call_next(request)
