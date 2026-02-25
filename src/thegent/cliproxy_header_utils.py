# MIGRATION NOTE: Migrate to cliproxyapi-plusplus Go SDK
from __future__ import annotations

from typing import Any


def sanitize_outbound_request_headers(request_headers: dict[str, Any]) -> dict[str, str]:
    """Return outbound request headers with hop-by-hop fields removed."""
    headers = dict(request_headers)
    headers.pop("host", None)
    headers.pop("content-length", None)
    return headers


def filter_inbound_response_headers(response_headers: dict[str, Any]) -> dict[str, str]:
    """Drop hop-by-hop response headers before returning to clients."""
    return {k: str(v) for k, v in response_headers.items() if k.lower() not in ("transfer-encoding", "connection")}


def extract_websocket_forward_headers(websocket_headers: dict[str, str]) -> dict[str, str]:
    """Build headers for WS->HTTP forwarding while preserving authorization."""
    forward_headers = {"authorization"}
    headers = {
        k: v
        for k, v in websocket_headers.items()
        if k.lower()
        not in (
            "host",
            "content-length",
            "upgrade",
            "connection",
            "sec-websocket-key",
            "sec-websocket-version",
            "sec-websocket-extensions",
        )
        or k.lower() in forward_headers
    }
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "text/event-stream"
    return headers
