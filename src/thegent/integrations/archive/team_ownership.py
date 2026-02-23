# @trace WL-281 B90-W2-B1
"""Team ownership registry with escalation contacts.

Maintains ownership assignments for work items across teams with backup
escalation contacts for governance and accountability.
"""

from __future__ import annotations

import orjson as json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, UTC
from pathlib import Path


@dataclass
class TeamOwnership:
    """Ownership record for a work item.

    Attributes:
        wl_id: Work item identifier (e.g., "WL-281")
        team: Team responsible for the item
        owner: Primary owner (username or email)
        backup_owner: Backup/escalation contact
        assigned_at: ISO 8601 timestamp when assignment was made
    """

    wl_id: str
    team: str
    owner: str
    backup_owner: str
    assigned_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class OwnershipRegistry:
    """Registry for team ownership assignments.

    Persists ownership data to JSON format with efficient lookup by
    work item ID or team.
    """

    def __init__(self, registry_path: Path | str = "docs/reference/team_ownership.json"):
        """Initialize the ownership registry.

        Args:
            registry_path: Path to JSON registry file. Created if it does not exist.
        """
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        """Load ownership data from disk."""
        self._data: dict[str, TeamOwnership] = {}
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                raw = json.load(f)
                # raw is a dict of wl_id -> ownership data
                for wl_id, data in raw.items():
                    self._data[wl_id] = TeamOwnership(**data)

    def _save(self) -> None:
        """Persist ownership data to disk."""
        with open(self.registry_path, "w") as f:
            # Convert dataclass instances to dicts
            data_to_save = {wl_id: asdict(ownership) for wl_id, ownership in self._data.items()}
            json.dump(data_to_save, f, indent=2)

    def register(self, ownership: TeamOwnership) -> None:
        """Register or update ownership for a work item.

        Args:
            ownership: TeamOwnership record to register.
        """
        self._data[ownership.wl_id] = ownership
        self._save()

    def get_owner(self, wl_id: str) -> TeamOwnership | None:
        """Get ownership record for a work item.

        Args:
            wl_id: Work item identifier.

        Returns:
            TeamOwnership if found, None otherwise.
        """
        return self._data.get(wl_id)

    def list_by_team(self, team: str) -> list[TeamOwnership]:
        """List all ownership records for a team.

        Args:
            team: Team identifier.

        Returns:
            List of TeamOwnership records for the team.
        """
        return [o for o in self._data.values() if o.team == team]
