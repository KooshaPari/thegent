"""Unified persona registry across projects."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CrossProjectRegistry:
    """Unified persona registry."""

    def __init__(self, registry_path: Path | None = None) -> None:
        """Initialize cross-project registry.

        Args:
            registry_path: Registry file path
        """
        self.registry_path = registry_path or Path("~/.thegent/persona_registry.json").expanduser()
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry: dict[str, Any] = self._load_registry()

    def _load_registry(self) -> dict[str, Any]:
        """Load registry from file.

        Returns:
            Registry dictionary
        """
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text())
            except Exception:
                return {}
        return {}

    def register_persona(self, project: str, persona: dict[str, Any]) -> None:
        """Register a persona.

        Args:
            project: Project name
            persona: Persona dictionary
        """
        if project not in self.registry:
            self.registry[project] = []

        self.registry[project].append(persona)
        self._save_registry()
        logger.info(f"Registered persona for project {project}")

    def get_personas(self, project: str | None = None) -> list[dict[str, Any]]:
        """Get personas.

        Args:
            project: Optional project filter

        Returns:
            List of personas
        """
        if project:
            return self.registry.get(project, [])

        all_personas = []
        for personas in self.registry.values():
            all_personas.extend(personas)
        return all_personas

    def _save_registry(self) -> None:
        """Save registry to file."""
        self.registry_path.write_text(json.dumps(self.registry, indent=2))
