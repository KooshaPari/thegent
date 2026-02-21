"""Ante session scraper.

Extracts session metadata from Ante agent harness at ~/.ante/sessions/.
Sessions are stored as JSON files with usage stats, timestamps, and model info.
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


def scrape_ante_models() -> list[str]:
    """Scrape available Ante models from settings.json."""
    settings_path = Path.home() / ".ante" / "settings.json"

    if not settings_path.exists():
        return ["claude-haiku-4-5"]  # fallback default

    try:
        with open(settings_path) as f:
            settings = json.load(f)
            model_name = settings.get("model", {})
            if isinstance(model_name, dict):
                name = model_name.get("name")
            else:
                name = model_name

            if name and isinstance(name, str):
                return [name]
    except Exception as e:
        _log.debug(f"Failed to scrape Ante models from settings.json: {e}")

    return ["claude-haiku-4-5"]


def parse_ante_session(session_file: Path) -> dict[str, Any] | None:
    """Parse a single Ante session JSON file.

    Returns dict with:
        - id: session ID
        - started_at: ISO datetime string
        - ended_at: ISO datetime string (None if ongoing)
        - duration_secs: total duration in seconds
        - model: model name
        - provider: provider name
        - input_tokens: prompt token count
        - output_tokens: completion token count
        - project_dir: working directory
    """
    try:
        with open(session_file) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return None

        session_id = data.get("id")
        if not session_id:
            return None

        # Extract usage stats
        usage = data.get("usage", {})
        input_tokens = int(usage.get("input_tokens", 0)) if isinstance(usage, dict) else 0
        output_tokens = int(usage.get("output_tokens", 0)) if isinstance(usage, dict) else 0

        # Extract duration
        duration = data.get("duration", {})
        duration_secs = 0
        if isinstance(duration, dict):
            secs = int(duration.get("secs", 0))
            nanos = int(duration.get("nanos", 0))
            duration_secs = secs + (nanos / 1_000_000_000)

        # Extract timestamps
        started_time = data.get("started_time")
        if not started_time:
            return None

        # Parse ISO timestamp
        try:
            started_at = datetime.fromisoformat(started_time.replace("Z", "+00:00"))
        except Exception:
            started_at = datetime.now(UTC)

        # Ante doesn't store explicit end time; we infer it from start + duration
        ended_at = None
        if duration_secs > 0:
            ended_at = datetime.fromtimestamp(started_at.timestamp() + duration_secs, tz=UTC)

        # Extract model info
        model_info = data.get("model", {})
        if isinstance(model_info, dict):
            model = model_info.get("name", "unknown")
        else:
            model = str(model_info) if model_info else "unknown"

        # Extract provider
        provider_info = data.get("provider", {})
        if isinstance(provider_info, dict):
            provider = provider_info.get("name", "unknown")
        else:
            provider = str(provider_info) if provider_info else "unknown"

        # Project directory
        project_dir = data.get("dir")

        return {
            "id": session_id,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat() if ended_at else None,
            "duration_secs": duration_secs,
            "model": model,
            "provider": provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "project_dir": project_dir,
        }
    except Exception as e:
        _log.debug(f"Failed to parse Ante session {session_file}: {e}")
        return None


def list_ante_sessions() -> list[dict[str, Any]]:
    """List all Ante sessions from ~/.ante/sessions/."""
    sessions = []
    sessions_dir = Path.home() / ".ante" / "sessions"

    if not sessions_dir.exists():
        return sessions

    try:
        for session_file in sorted(sessions_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            parsed = parse_ante_session(session_file)
            if parsed:
                sessions.append(parsed)
    except Exception as e:
        _log.debug(f"Error listing Ante sessions: {e}")

    return sessions
