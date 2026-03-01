"""
Teammate Registry

Auto-discovers and manages available teammates from agents/ directory.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os


@dataclass
class Teammate:
    """Represents a teammate agent."""
    id: str
    name: str
    description: str
    priority: str = "NORMAL"
    path: Optional[Path] = None

    def __post_init__(self):
        if self.path is None:
            self.path = Path(f"agents/{self.id}")


class TeammateRegistry:
    """Registry for discovering and managing teammates."""

    def __init__(self, agents_dir: str = "agents"):
        self.agents_dir = Path(agents_dir)
        self._teammates: dict[str, Teammate] = {}

    def discover(self) -> list[Teammate]:
        """Auto-discover teammates from agents/ directory."""
        teammates = []

        if not self.agents_dir.exists():
            return teammates

        for path in self.agents_dir.iterdir():
            if path.is_dir() and not path.name.startswith("_"):
                teammate = self._load_teammate(path)
                if teammate:
                    teammates.append(teammate)
                    self._teammates[teammate.id] = teammate

        return teammates

    def _load_teammate(self, path: Path) -> Optional[Teammate]:
        """Load teammate from directory."""
        config_file = path / "teammate.yaml"
        if not config_file.exists():
            config_file = path / "config.yaml"

        if config_file.exists():
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
                return Teammate(
                    id=path.name,
                    name=config.get("name", path.name),
                    description=config.get("description", ""),
                    priority=config.get("priority", "NORMAL"),
                    path=path
                )

        return Teammate(
            id=path.name,
            name=path.name,
            description="",
            path=path
        )

    def get(self, teammate_id: str) -> Optional[Teammate]:
        """Get teammate by ID."""
        return self._teammates.get(teammate_id)

    def list(self) -> list[Teammate]:
        """List all registered teammates."""
        return list(self._teammates.values())
