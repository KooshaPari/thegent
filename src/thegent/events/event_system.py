"""Event system for thegent."""

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class EventSystem:
    """Event system for pub/sub."""

    def __init__(self) -> None:
        """Initialize event system."""
        self.subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to event type.

        Args:
            event_type: Event type
            handler: Handler function
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def emit(self, event_type: str, data: Any) -> None:
        """Emit an event.

        Args:
            event_type: Event type
            data: Event data
        """
        handlers = self.subscribers.get(event_type, [])

        def _call_handler(handler: Any) -> None:
            """Safely call a single event handler."""
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

        for handler in handlers:
            _call_handler(handler)
