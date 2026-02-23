"""
NATS Event Bus Integration - Event bus for thegent orchestration.

Full implementation for Phase 3 Spike Batch B.
"""

import orjson as json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from enum import Enum
from typing import Callable
from uuid import uuid4

from thegent.integrations.base import DataclassConfig

logger = logging.getLogger(__name__)

try:
    import nats  # type: ignore[import-not-found]
    from nats.js import JetStreamContext  # type: ignore[import-not-found]
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    nats = None
    JetStreamContext = None  # type: ignore[assignment,misc]


class NATSError(Exception):
    """Base exception for NATS errors."""


class NATSStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class NATSConfig(DataclassConfig):
    """Configuration for NATS event bus."""
    servers: list = field(default_factory=lambda: ["nats://localhost:4222"])
    user: str = ""
    password: str = ""
    use_tls: bool = False
    max_reconnect_attempts: int = 10
    reconnect_time_wait: float = 2.0


class EventType(str, Enum):
    """Event types for thegent orchestration."""
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


@dataclass
class WorkflowEvent:
    """Represents a workflow event."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = EventType.TASK_STARTED
    workflow_id: str = ""
    task_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(tz=UTC).isoformat())
    data: dict = field(default_factory=dict)


@dataclass
class NATSResult:
    """Result from NATS operation."""
    success: bool
    message: str = ""
    error: str = ""


class NATSEventBus:
    """
    Event bus using NATS for thegent orchestration.

    Publishes 4 event types:
    - task.started
    - task.progress
    - task.completed
    - task.failed
    """

    def __init__(self, config: NATSConfig | None = None):
        self._config = config or self._load_config()
        self._status = NATSStatus.DISCONNECTED
        self._nc = None
        self._js = None
        self._subscriptions = {}

        if self._config.enabled:
            self._status = NATSStatus.CONNECTING
            logger.info("NATS event bus initialized (enabled)")

    def _load_config(self) -> NATSConfig:
        config = NATSConfig.from_env("NATS_")
        # Handle servers as comma-separated list
        servers_env = os.environ.get("NATS_SERVERS", "nats://localhost:4222")
        config.servers = [s.strip() for s in servers_env.split(",")]
        # Handle enable flag with THEGENT-specific env var
        config.enabled = os.environ.get("THEGENT_EVENT_BUS", "").lower() in ("1", "true", "yes", "nats")
        return config

    @property
    def is_enabled(self) -> bool:
        return self._config.enabled and self._status == NATSStatus.CONNECTED

    @property
    def status(self) -> NATSStatus:
        return self._status

    async def connect(self) -> bool:
        """Connect to NATS server."""
        if not self._config.enabled:
            return False

        if not NATS_AVAILABLE:
            logger.warning("NATS library not available, using mock mode")
            self._status = NATSStatus.CONNECTED
            return True

        try:
            opts = {
                "servers": self._config.servers,
                "max_reconnect_attempts": self._config.max_reconnect_attempts,
            }

            if self._config.user and self._config.password:
                opts["user"] = self._config.user
                opts["password"] = self._config.password

            self._nc = await nats.connect(**opts)
            self._js = self._nc.jetstream()

            self._status = NATSStatus.CONNECTED
            logger.info(f"Connected to NATS: {self._config.servers}")
            return True

        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            self._status = NATSStatus.ERROR
            return False

    async def disconnect(self):
        """Disconnect from NATS."""
        if self._nc and self._status == NATSStatus.CONNECTED:
            await self._nc.close()
            self._status = NATSStatus.DISCONNECTED

    async def publish(
        self,
        event_type: EventType,
        workflow_id: str = "",
        task_id: str = "",
        data: dict | None = None
    ) -> NATSResult:
        """Publish an event."""
        if not self.is_enabled:
            return NATSResult(success=False, error="Not enabled")

        try:
            event = WorkflowEvent(
                event_type=event_type,
                workflow_id=workflow_id,
                task_id=task_id,
                data=data or {}
            )

            subject = f"workflow.events.{event.workflow_id or 'global'}.{event_type.value}"

            payload = json.dumps({
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "workflow_id": event.workflow_id,
                "task_id": event.task_id,
                "timestamp": event.timestamp,
                "data": event.data,
            }).encode()

            if self._js:
                await self._js.publish(subject=subject, payload=payload)
            elif self._nc:
                await self._nc.publish(subject, payload)

            logger.debug(f"Published {event_type.value} to {subject}")
            return NATSResult(success=True, message=f"Published to {subject}")

        except Exception as e:
            logger.error(f"Publish error: {e}")
            return NATSResult(success=False, error=str(e))

    async def subscribe(
        self,
        subject_pattern: str,
        callback: Callable,
        queue: str | None = None
    ) -> str:
        """Subscribe to events."""
        if not self.is_enabled:
            raise NATSError("Not enabled")

        async def handler(msg):
            try:
                data = json.loads(msg.data.decode())
                event = WorkflowEvent(
                    event_id=data.get("event_id", ""),
                    event_type=EventType(data.get("event_type", "")),
                    workflow_id=data.get("workflow_id", ""),
                    task_id=data.get("task_id", ""),
                    timestamp=data.get("timestamp", ""),
                    data=data.get("data", {})
                )
                await callback(event)
            except Exception as e:
                logger.error(f"Message handler error: {e}")

        sub_id = str(uuid4())

        if queue:
            sub = await self._nc.subscribe(subject_pattern, queue=queue, cb=handler)
        else:
            sub = await self._nc.subscribe(subject_pattern, cb=handler)

        self._subscriptions[sub_id] = sub
        return sub_id

    async def unsubscribe(self, sub_id: str):
        """Unsubscribe from events."""
        if sub_id in self._subscriptions:
            sub = self._subscriptions.pop(sub_id)
            await sub.unsubscribe()

    # Convenience methods
    async def publish_task_started(self, workflow_id: str, task_id: str, data: dict | None = None) -> NATSResult:
        return await self.publish(EventType.TASK_STARTED, workflow_id, task_id, data)

    async def publish_task_progress(self, workflow_id: str, task_id: str, data: dict | None = None) -> NATSResult:
        return await self.publish(EventType.TASK_PROGRESS, workflow_id, task_id, data)

    async def publish_task_completed(self, workflow_id: str, task_id: str, data: dict | None = None) -> NATSResult:
        return await self.publish(EventType.TASK_COMPLETED, workflow_id, task_id, data)

    async def publish_task_failed(self, workflow_id: str, task_id: str, data: dict | None = None) -> NATSResult:
        return await self.publish(EventType.TASK_FAILED, workflow_id, task_id, data)

    async def health_check(self) -> bool:
        if not self.is_enabled:
            return False
        try:
            result = await self.publish_task_started("_health", "_ping")
            return result.success
        except:
            return False

    def get_stats(self) -> dict:
        return {
            "name": "nats",
            "status": self._status.value,
            "enabled": self.is_enabled,
            "servers": self._config.servers,
        }


_nats_bus = None

def get_nats_event_bus() -> NATSEventBus:
    global _nats_bus
    if _nats_bus is None:
        _nats_bus = NATSEventBus()
    return _nats_bus


def is_nats_enabled() -> bool:
    return get_nats_event_bus().is_enabled
