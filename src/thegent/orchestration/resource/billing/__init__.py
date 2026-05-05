"""Stub module."""
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class TeamBillingManager:
    """Team billing manager stub."""
    
    def __init__(self) -> None:
        self.budgets: dict[str, Any] = {}
    
    def get_usage(self, team_id: str) -> dict[str, Any]:
        return {"team_id": team_id, "usage": 0}


__all__ = ["TeamBillingManager"]
