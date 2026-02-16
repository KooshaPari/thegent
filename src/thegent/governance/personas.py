"""WP-12007: Persona profiles and access constraints.

Defines role-based access limits and defaults for different operator personas.
"""

from typing import Any


class PersonaManager:
    """Manages role-based constraints for operator personas."""

    def __init__(self) -> None:
        self._personas = {
            "operator": {"max_lane": "standard", "can_override": False},
            "incident_commander": {"max_lane": "critical", "can_override": True},
            "compliance_officer": {"max_lane": "recovery", "can_override": False, "read_only": True},
        }

    def check_access(self, persona: str, operation: str, lane: str) -> dict[str, Any]:
        """Verify if a persona can perform a specific operation in a specific lane."""
        config = self._personas.get(persona)
        if not config:
            return {"allowed": False, "reason": "Unknown persona."}

        if lane == "critical" and config["max_lane"] != "critical":
            return {"allowed": False, "reason": f"Persona {persona} restricted from critical lane."}

        return {"allowed": True, "config": config}
