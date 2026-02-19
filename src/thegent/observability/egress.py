"""WP-15001: External SOC/SIEM event egress for enterprise observability."""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

import httpx
import tenacity


@dataclass
class EgressEvent:
    id: str
    severity: str  # "low", "medium", "high", "critical"
    event_type: str
    source: str
    payload: dict[str, Any]
    timestamp: str = datetime.now(UTC).isoformat()


class SIEMEgress:
    """Pushes normalized events to external enterprise security systems (WP-15001)."""

    def __init__(self, endpoint_url: str | None = None) -> None:
        self.endpoint_url = endpoint_url
        self._sent_count = 0

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_random_exponential(multiplier=1, min=2, max=10),
        retry=tenacity.retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    )
    def push_event(self, event: EgressEvent) -> bool:
        """Push an event to the external SIEM endpoint via HTTP POST."""
        if not self.endpoint_url:
            # If no endpoint, just log or skip (enterprise feature not configured)
            return False

        payload = asdict(event)
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                self.endpoint_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()

        self._sent_count += 1
        return True

    def format_for_syslog(self, event: EgressEvent) -> str:
        """Format the event for traditional RFC 5424 syslog."""
        return f"<{event.severity}> {event.timestamp} {event.source} {event.event_type}: {json.dumps(event.payload)}"
