"""WP-26002: Agent Micro-Payment Protocol.
Enables agents to pay each other for services (tool execution, data, research).
Supports micro-payments via a virtual agent treasury.
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class Transaction(BaseModel):
    """Metadata for an agent-to-agent micro-payment."""

    tx_id: str = field(default_factory=lambda: f"tx_{uuid.uuid4().hex[:8]}")
    sender_id: str
    receiver_id: str
    amount_usd: float
    purpose: str
    timestamp: str = datetime.now(UTC).isoformat()
    status: str = "pending"  # pending, settled, rejected


class AgentTreasury:
    """Manages the budget and payments for a local agent instance."""

    def __init__(self, agent_id: str, initial_balance: float = 100.0) -> None:
        self.agent_id = agent_id
        self.balance = initial_balance
        self.history: list[Transaction] = []

    def pay_peer(self, receiver_id: str, amount: float, purpose: str) -> str | None:
        """Initiate a payment to a peer agent."""
        if amount > self.balance:
            _log.error("Insufficient funds in treasury: Balance $%.2f < Amount $%.2f", self.balance, amount)
            return None

        _log.info("Agent %s paying %s: $%.4f for '%s'", self.agent_id, receiver_id, amount, purpose)

        tx = Transaction(
            sender_id=self.agent_id, receiver_id=receiver_id, amount_usd=amount, purpose=purpose, status="settled"
        )

        self.balance -= amount
        self.history.append(tx)
        _log.info("Payment settled. New balance: $%.2f", self.balance)
        return tx.tx_id

    def receive_payment(self, sender_id: str, amount: float, purpose: str) -> str:
        """Process an incoming payment from a peer agent."""
        _log.info("Agent %s received $%.4f from %s for '%s'", self.agent_id, amount, sender_id, purpose)

        tx = Transaction(
            sender_id=sender_id, receiver_id=self.agent_id, amount_usd=amount, purpose=purpose, status="settled"
        )

        self.balance += amount
        self.history.append(tx)
        return tx.tx_id

    def get_statement(self) -> dict[str, Any]:
        """Generate a financial statement for the treasury."""
        return {
            "agent_id": self.agent_id,
            "balance_usd": self.balance,
            "total_spent": sum(t.amount_usd for t in self.history if t.sender_id == self.agent_id),
            "total_received": sum(t.amount_usd for t in self.history if t.receiver_id == self.agent_id),
            "transaction_count": len(self.history),
        }
