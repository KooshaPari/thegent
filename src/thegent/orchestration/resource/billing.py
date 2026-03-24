"""WP-19004: Quota & Billing for Multi-Tenant Teams.
Enforces resource quotas (runs, tokens, storage) per team/tenant.
"""

import orjson as json
import logging
import threading
from pathlib import Path
from typing import Any

from thegent.team.manager import TeamManager

_log = logging.getLogger(__name__)


def _dump_json(payload: Any) -> str:
    return json.dumps(payload, option=json.OPT_INDENT_2).decode("utf-8")


class TeamBillingManager:
    """Manages resource quotas and billing for multi-tenant teams."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.tm = TeamManager(session_dir)
        self.quotas_path = session_dir / "team_quotas.json"
        self._lock = threading.Lock()

    def _load_quotas(self) -> dict[str, Any]:
        """Load quota definitions for all teams."""
        if not self.quotas_path.exists():
            return {}
        return json.loads(self.quotas_path.read_text(encoding="utf-8"))

    def check_quota(self, team_id: str, resource: str, cost: float = 1.0) -> bool:
        """Check if a team has enough quota for a resource."""
        with self._lock:
            quotas = self._load_quotas()
            team_quota = quotas.get(
                team_id,
                {
                    "max_runs": 100,
                    "used_runs": 0,
                    "max_tokens": 1_000_000,
                    "used_tokens": 0,
                    "budget_usd": 10.0,
                    "used_usd": 0.0,
                },
            )

            if resource == "run":
                if team_quota["used_runs"] + 1 > team_quota["max_runs"]:
                    return False
            elif resource == "tokens":
                if team_quota["used_tokens"] + cost > team_quota["max_tokens"]:
                    return False
            elif resource == "usd":
                if team_quota["used_usd"] + cost > team_quota["budget_usd"]:
                    return False

            return True

    def record_usage(self, team_id: str, resource: str, amount: float = 1.0) -> None:
        """Record resource usage for a team."""
        with self._lock:
            quotas = self._load_quotas()
            if team_id not in quotas:
                quotas[team_id] = {
                    "max_runs": 100,
                    "used_runs": 0,
                    "max_tokens": 1_000_000,
                    "used_tokens": 0,
                    "budget_usd": 10.0,
                    "used_usd": 0.0,
                }

            if resource == "run":
                quotas[team_id]["used_runs"] += int(amount)
            elif resource == "tokens":
                quotas[team_id]["used_tokens"] += int(amount)
            elif resource == "usd":
                quotas[team_id]["used_usd"] += amount

            self.quotas_path.write_text(_dump_json(quotas), encoding="utf-8")
        _log.info("Recorded %s usage for team %s: %s", resource, team_id, amount)

    def get_billing_report(self, team_id: str) -> dict[str, Any]:
        """Generate a billing report for a team."""
        with self._lock:
            quotas = self._load_quotas()
        return quotas.get(team_id, {})
