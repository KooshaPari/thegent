"""WP-16001/16002: Thegent Teammates orchestration and delegation protocol."""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .agent_hierarchy import (
    AgentHierarchyManager,
    AgentRole,
    CoordinationMode,
    RelationshipType,
    TeamType,
)


@dataclass
class TeammatePersona:
    """Specialized agent persona for the teammate swarm."""

    id: str
    role: str
    description: str
    capabilities: list[str]
    default_model: str = "gemini-3-flash"
    priority: int = 1  # 1 (high) to 5 (background)


@dataclass
class DelegationRequest:
    """Record of a delegated task to a teammate."""

    id: str
    teammate_id: str
    parent_run_id: str
    prompt: str
    status: str = "pending"  # pending, running, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None
    result_summary: str | None = None
    artifact_path: str | None = None


class TeammateManager:
    """Manages discovery and delegation for the teammate swarm."""

    def __init__(self, storage_path: Path, hierarchy_manager: AgentHierarchyManager | None = None) -> None:
        """
        Initialize teammate manager.

        Args:
            storage_path: Path for storing delegations
            hierarchy_manager: Optional AgentHierarchyManager for hierarchy support
        """
        self.storage_path = storage_path
        self.hierarchy = hierarchy_manager or AgentHierarchyManager(storage_path / "hierarchy")
        self._delegations: dict[str, DelegationRequest] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                for did, ddata in data.items():
                    self._delegations[did] = DelegationRequest(**ddata)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {did: asdict(d) for did, d in self._delegations.items()}
        self.storage_path.write_text(json.dumps(data, indent=2))

    def list_personas(self) -> list[TeammatePersona]:
        """WP-16001: Discover teammates from agent markdown files."""
        personas = []
        agents_dir = Path("agents")
        if not agents_dir.exists():
            return []

        from thegent.infra import yaml_loads

        for md_file in agents_dir.glob("*.md"):
            try:
                content = md_file.read_text()
                # Simple frontmatter extraction
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        meta = yaml_loads(parts[1])
                        personas.append(
                            TeammatePersona(
                                id=meta.get("name", md_file.stem),
                                role=meta.get("role", "general"),
                                description=meta.get("description", ""),
                                capabilities=meta.get("tools", []),
                                default_model=meta.get("model", "gemini-3-flash"),
                            )
                        )
            except Exception:
                continue

        return sorted(personas, key=lambda x: x.id)

    def delegate(
        self,
        teammate_id: str,
        parent_run_id: str,
        prompt: str,
        team_id: str | None = None,
        relationship_type: RelationshipType = RelationshipType.DIRECT_PARENT_CHILD,
    ) -> DelegationRequest:
        """
        WP-16002: Delegate a task to a teammate with hierarchy support.

        Args:
            teammate_id: Teammate agent identifier
            parent_run_id: Parent agent run_id
            prompt: Task prompt
            team_id: Optional team identifier
            relationship_type: Type of relationship

        Returns:
            DelegationRequest
        """
        req_id = f"DEL-{uuid.uuid4().hex[:8]}"

        # Infer role from teammate_id or use SPECIALIST as default
        role = self._infer_role(teammate_id)

        # Register child agent in hierarchy
        child_node = self.hierarchy.register_agent(
            agent_id=teammate_id,
            run_id=req_id,
            role=role,
            parent_id=parent_run_id,
            team_id=team_id,
        )

        # Create relationship
        relationship = self.hierarchy.create_relationship(
            parent_id=parent_run_id,
            child_id=req_id,
            relationship_type=relationship_type,
            delegation_prompt=prompt,
            task_id=req_id,
        )

        # Create delegation request
        request = DelegationRequest(
            id=req_id, teammate_id=teammate_id, parent_run_id=parent_run_id, prompt=prompt, status="pending"
        )
        self._delegations[req_id] = request
        self._save()

        # WP-16003: ShareCLI Integration
        try:
            from thegent.governance.sharecli_bridge import ShareCLIBridge

            bridge = ShareCLIBridge()
            if bridge.is_available():
                bridge.create_shared_task(
                    task_id=req_id, description=f"Delegated from {parent_run_id}: {prompt[:50]}..."
                )
                bridge.broadcast_intent(agent_id=f"thegent:{parent_run_id}", intent_type="delegate", target=teammate_id)
        except ImportError:
            # ShareCLI bridge not available, continue without it
            pass

        # In a real implementation, this would trigger 'thegent bg'
        return request

    def _infer_role(self, teammate_id: str) -> AgentRole:
        """Infer agent role from teammate_id."""
        teammate_id_lower = teammate_id.lower()

        # Check for team lead indicators
        if "lead" in teammate_id_lower or "manager" in teammate_id_lower:
            return AgentRole.TEAM_LEAD

        # Check for executive indicators
        if "executive" in teammate_id_lower or "orchestrator" in teammate_id_lower or "sitback" in teammate_id_lower:
            return AgentRole.EXECUTIVE

        # Default to specialist
        return AgentRole.SPECIALIST

    def create_team(
        self,
        team_id: str,
        name: str,
        description: str,
        team_type: TeamType,
        coordination_mode: CoordinationMode,
        lead_id: str,
    ) -> Any:
        """
        Create a new team.

        Args:
            team_id: Team identifier
            name: Team name
            description: Team description
            team_type: Type of team
            coordination_mode: Coordination mode
            lead_id: Team lead agent run_id

        Returns:
            Created AgentTeam
        """
        return self.hierarchy.create_team(
            team_id=team_id,
            name=name,
            description=description,
            team_type=team_type,
            coordination_mode=coordination_mode,
            lead_id=lead_id,
        )

    def update_status(self, req_id: str, status: str, summary: str | None = None) -> bool:
        """Update the status of a delegation."""
        if req_id not in self._delegations:
            return False

        req = self._delegations[req_id]
        req.status = status
        if status in ("completed", "failed"):
            req.completed_at = datetime.now(UTC).isoformat()
            req.result_summary = summary

        self._save()
        return True

    def get_delegations(self, parent_run_id: str | None = None) -> list[DelegationRequest]:
        """List all delegations, optionally filtered by parent run."""
        if parent_run_id:
            return [d for d in self._delegations.values() if d.parent_run_id == parent_run_id]
        return list(self._delegations.values())
