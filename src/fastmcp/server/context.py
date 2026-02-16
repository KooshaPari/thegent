from typing import Any
from dataclasses import dataclass

@dataclass
class Context:
    request_context: Any = None


@dataclass
class AcceptedElicitation:
    data: Any


@dataclass
class DeclinedElicitation:
    reason: str | None = None


@dataclass
class CancelledElicitation:
    reason: str | None = None
