"""CLIProxy model checking utilities.

Traces to: FR-AGT-004, FR-AGT-006
"""

from __future__ import annotations

from typing import Any


def extract_model_ids(payload: dict[str, Any]) -> list[str]:
    """Extract model IDs from API response payload.

    Supports both 'data' and legacy 'models' keys.
    Prefers 'data' over 'models' when both are present.
    """
    if "data" in payload:
        return [m["id"] for m in payload["data"] if "id" in m]
    if "models" in payload:
        return [m["id"] for m in payload["models"] if "id" in m]
    return []


def models_url(base_url: str) -> str:
    """Construct the models endpoint URL from a base URL.

    If the URL ends with /v1 or /v1/, append /models.
    Otherwise, append /v1/models.
    """
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/models"
    return f"{base}/v1/models"


def run_check(base_url: str | None = None, timeout: float = 5.0) -> dict[str, Any]:
    """Run a model check against the Phenotype CLIProxy.

    Args:
        base_url: The base URL of the CLIProxy. If None, uses default.
        timeout: Request timeout in seconds.

    Returns:
        Dict with 'ok' boolean and 'models' list or 'error' message.
    """
    import urllib.request

    url = models_url(base_url or "http://127.0.0.1:8317")

    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            import json

            data = json.loads(response.read().decode("utf-8"))
            models = extract_model_ids(data)
            return {"ok": True, "models": models, "count": len(models)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


__all__ = [
    "extract_model_ids",
    "models_url",
    "run_check",
]
