"""
Swarm Communication

Fast inter-agent communication with <5ms latency.
"""

from dataclasses import dataclass
from typing import Any, Optional, Callable
from collections import defaultdict
import time
import queue
import threading


@dataclass
class Message:
    """Message between agents."""

    sender: str
    receiver: str  # or "broadcast"
    message_type: str
    payload: Any
    timestamp: float
    id: Optional[str] = None


class SwarmChannel:
    """Fast communication channel for agents."""

    def __init__(self, max_queue_size: int = 1000):
        self._queues: dict[str, queue.Queue] = defaultdict(lambda: queue.Queue(maxsize=max_queue_size))
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
        self._message_count = 0
        self._total_latency = 0.0

    def send(self, message: Message) -> bool:
        """Send message to receiver."""
        start = time.time()

        if message.receiver == "broadcast":
            # Deliver to all subscribers
            for agent_id in self._subscribers:
                self._deliver(agent_id, message)
        else:
            self._deliver(message.receiver, message)

        # Track latency
        self._total_latency += (time.time() - start) * 1000  # ms
        self._message_count += 1

        return True

    def _deliver(self, receiver: str, message: Message) -> bool:
        """Deliver message to specific receiver."""
        try:
            self._queues[receiver].put(message, block=False)
            # Notify subscribers
            for callback in self._subscribers.get(receiver, []):
                callback(message)
            return True
        except queue.Full:
            return False

    def receive(self, agent_id: str, timeout: float = 0.001) -> Optional[Message]:
        """Receive message for agent (non-blocking by default)."""
        try:
            return self._queues[agent_id].get(block=True, timeout=timeout)
        except queue.Empty:
            return None

    def subscribe(self, agent_id: str, callback: Callable[[Message], None]) -> None:
        """Subscribe to messages for agent."""
        self._subscribers[agent_id].append(callback)

    def average_latency(self) -> float:
        """Get average message latency in ms."""
        if self._message_count == 0:
            return 0.0
        return self._total_latency / self._message_count

    def stats(self) -> dict:
        """Get channel statistics."""
        return {
            "message_count": self._message_count,
            "average_latency_ms": self.average_latency(),
            "queue_sizes": {k: q.qsize() for k, q in self._queues.items()},
        }
