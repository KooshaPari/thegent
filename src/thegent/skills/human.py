"""Human-in-the-loop tools for thegent (WP-4009)."""

import logging
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class HumanInputRequest(BaseModel):
    """Request for human intervention or clarification."""

    request_id: str
    prompt: str
    context: dict[str, Any]
    options: list[str] | None = None


def ask_human(prompt: str, options: list[str] | None = None) -> str:
    """WP-4009: Human-as-a-Tool (HaaT).
    Pauses execution and waits for human input via the Cockpit or CLI.
    """
    import json
    import time
    import uuid
    from pathlib import Path

    request_id = f"req_{uuid.uuid4().hex[:8]}"
    _log.info("HITL: ask_human triggered: %s (ID: %s)", prompt, request_id)

    # In a real implementation, this would post to a queue and wait.
    # For this phase, we'll write to a 'human_requests.jsonl' file.
    request = {
        "request_id": request_id,
        "prompt": prompt,
        "options": options,
        "status": "pending",
        "timestamp": time.time(),
    }

    # Placeholder: assuming .thegent/sessions directory
    session_dir = Path(".thegent/sessions")
    session_dir.mkdir(parents=True, exist_ok=True)
    request_file = session_dir / "human_requests.jsonl"

    with request_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(request) + "\n")

    if options:
        pass

    return f"PENDING_HUMAN_RESPONSE:{request_id}"
