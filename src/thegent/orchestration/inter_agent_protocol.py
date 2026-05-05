"""Inter-agent protocol."""
from typing import Any


class InterAgentMessage:
    """Message between agents."""
    
    def __init__(self, sender: str, receiver: str, content: dict[str, Any]) -> None:
        self.sender = sender
        self.receiver = receiver
        self.content = content


class InterAgentProtocol:
    """Protocol for inter-agent communication."""
    
    def send(self, message: InterAgentMessage) -> bool:
        """Send a message."""
        return True
    
    def receive(self) -> InterAgentMessage | None:
        """Receive a message."""
        return None


class MessageBus:
    """Message bus for inter-agent communication."""

    def __init__(self) -> None:
        self.queue: list[InterAgentMessage] = []

    def publish(self, message: InterAgentMessage) -> None:
        """Publish a message to the bus."""
        self.queue.append(message)

    def subscribe(self, agent_id: str) -> list[InterAgentMessage]:
        """Subscribe to messages for an agent."""
        return [m for m in self.queue if m.receiver == agent_id]
