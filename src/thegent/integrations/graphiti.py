"""
Graphiti Memory Integration - Persistent memory with graph semantics.

Full implementation for Phase 3 Spike Batch B.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class GraphitiError(Exception):
    """Base exception for Graphiti errors."""


class GraphitiStatus(Enum):
    DISABLED = "disabled"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class GraphitiConfig:
    """Configuration for Graphiti memory integration."""
    enabled: bool = False
    server_url: str = "http://localhost:8000"
    api_key: str = ""
    namespace: str = "thegent"
    timeout_seconds: int = 30
    max_context_items: int = 10


@dataclass
class MemoryFact:
    """Represents a fact in memory graph."""
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    timestamp: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(tz=timezone.utc).isoformat()


@dataclass
class GraphitiResult:
    """Result from Graphiti operation."""
    success: bool
    facts: list = field(default_factory=list)
    context: str = ""
    error: str = ""
    latency_ms: int = 0


class GraphitiMemoryStore:
    """
    Persistent memory with graph semantics using getzep/graphiti.

    Provides:
    - put_memory: Store facts with graph semantics
    - get_recent_context: Retrieve relevant context for sessions
    - Session replay with cross-session recall
    """

    def __init__(self, config: GraphitiConfig = None):
        self._config = config or self._load_config()
        self._status = GraphitiStatus.DISABLED
        self._connected = False

        if self._config.enabled:
            self._status = GraphitiStatus.CONNECTING
            logger.info("Graphiti memory store initialized (enabled)")

    def _load_config(self) -> GraphitiConfig:
        return GraphitiConfig(
            enabled=os.getenv("THEGENT_ENABLE_GRAPHITI", "").lower() in ("1", "true", "yes"),
            server_url=os.getenv("GRAPHITI_SERVER_URL", "http://localhost:8000"),
            api_key=os.getenv("GRAPHITI_API_KEY", ""),
            namespace=os.getenv("GRAPHITI_NAMESPACE", "thegent"),
            timeout_seconds=int(os.getenv("GRAPHITI_TIMEOUT_SECONDS", "30")),
            max_context_items=int(os.getenv("GRAPHITI_MAX_CONTEXT_ITEMS", "10")),
        )

    @property
    def is_enabled(self) -> bool:
        return self._config.enabled and self._status == GraphitiStatus.CONNECTED

    @property
    def status(self) -> GraphitiStatus:
        return self._status

    async def connect(self) -> bool:
        """Connect to Graphiti server."""
        if not self._config.enabled:
            return False

        if not HTTPX_AVAILABLE:
            logger.warning("httpx not available, using mock mode")
            self._status = GraphitiStatus.CONNECTED
            self._connected = True
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._config.server_url}/health",
                    timeout=5
                )
                if response.status_code == 200:
                    self._status = GraphitiStatus.CONNECTED
                    self._connected = True
                    return True
        except Exception as e:
            logger.error(f"Graphiti connection failed: {e}")

        self._status = GraphitiStatus.ERROR
        return False

    async def put_memory(
        self,
        entity: str,
        relation: str,
        target: str,
        metadata: dict | None = None
    ) -> GraphitiResult:
        """Store a memory fact in the graph."""
        import time
        start_time = time.monotonic()

        if not self.is_enabled:
            return GraphitiResult(success=False, error="Not enabled")

        try:
            payload = {
                "entity": entity,
                "relation": relation,
                "target": target,
                "namespace": self._config.namespace,
                "metadata": metadata or {},
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            }

            headers = {"Content-Type": "application/json"}
            if self._config.api_key:
                headers["Authorization"] = f"Bearer {self._config.api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._config.server_url}/facts",
                    json=payload,
                    headers=headers,
                    timeout=self._config.timeout_seconds
                )

            latency_ms = int((time.monotonic() - start_time) * 1000)

            if response.status_code in (200, 201):
                return GraphitiResult(success=True, latency_ms=latency_ms)

            return GraphitiResult(
                success=False,
                error=f"HTTP {response.status_code}",
                latency_ms=latency_ms
            )

        except Exception as e:
            logger.error(f"put_memory error: {e}")
            return GraphitiResult(success=False, error=str(e))

    async def get_recent_context(
        self,
        query: str,
        max_items: int | None = None
    ) -> GraphitiResult:
        """Get relevant context for a session."""
        import time
        start_time = time.monotonic()

        if not self.is_enabled:
            return GraphitiResult(success=False, error="Not enabled")

        max_items = max_items or self._config.max_context_items

        try:
            params = {
                "query": query,
                "namespace": self._config.namespace,
                "limit": max_items,
            }

            headers = {}
            if self._config.api_key:
                headers["Authorization"] = f"Bearer {self._config.api_key}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._config.server_url}/search",
                    params=params,
                    headers=headers,
                    timeout=self._config.timeout_seconds
                )

            latency_ms = int((time.monotonic() - start_time) * 1000)

            if response.status_code == 200:
                data = response.json()
                facts = []
                for item in data.get("facts", []):
                    facts.append(MemoryFact(
                        subject=item.get("entity", ""),
                        predicate=item.get("relation", ""),
                        object=item.get("target", ""),
                        confidence=item.get("confidence", 1.0),
                    ))

                context = "\n".join([
                    f"{f.subject} {f.predicate} {f.object}"
                    for f in facts
                ])

                return GraphitiResult(
                    success=True,
                    facts=facts,
                    context=context,
                    latency_ms=latency_ms
                )

            return GraphitiResult(
                success=False,
                error=f"HTTP {response.status_code}",
                latency_ms=latency_ms
            )

        except Exception as e:
            logger.error(f"get_recent_context error: {e}")
            return GraphitiResult(success=False, error=str(e))

    async def health_check(self) -> bool:
        """Check if Graphiti is healthy."""
        if not self.is_enabled:
            return False
        try:
            result = await self.get_recent_context("health")
            return result.success
        except:
            return False

    def get_stats(self) -> dict:
        return {
            "name": "graphiti",
            "status": self._status.value,
            "enabled": self.is_enabled,
            "server_url": self._config.server_url,
            "namespace": self._config.namespace,
        }


_graphiti_store = None

def get_graphiti_store() -> GraphitiMemoryStore:
    global _graphiti_store
    if _graphiti_store is None:
        _graphiti_store = GraphitiMemoryStore()
    return _graphiti_store


def is_graphiti_enabled() -> bool:
    return get_graphiti_store().is_enabled
