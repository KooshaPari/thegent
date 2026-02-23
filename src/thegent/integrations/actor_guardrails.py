"""Actor and Impersonation Guardrails for identity and access control.

WL-223: Actor/Impersonation Guardrails
Enforces policies for actor identities, target access, and impersonation permissions.

# @trace WL-223
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ActorPolicy:
    """Policy governing an actor's permissions and target access."""

    actor_id: str
    allowed_targets: list[str] = field(default_factory=list)
    can_impersonate: bool = False


class ActorImpersonationGuardrails:
    """Manages actor policies and impersonation permissions."""

    def __init__(self) -> None:
        """Initialize the guardrails with no registered policies."""
        self._policies: dict[str, ActorPolicy] = {}

    def register(
        self, actor_id: str, allowed_targets: list[str], can_impersonate: bool = False
    ) -> ActorPolicy:
        """Register an actor with its permissions.

        Args:
            actor_id: Unique identifier for the actor.
            allowed_targets: List of target IDs this actor can act as.
            can_impersonate: Whether this actor is allowed to impersonate others.

        Returns:
            The created ActorPolicy.

        Raises:
            ValueError: If actor_id is already registered.
        """
        if actor_id in self._policies:
            raise ValueError(f"Actor '{actor_id}' already registered")
        policy = ActorPolicy(actor_id=actor_id, allowed_targets=allowed_targets, can_impersonate=can_impersonate)
        self._policies[actor_id] = policy
        return policy

    def can_act_as(self, actor_id: str, target_id: str) -> bool:
        """Check if an actor is allowed to act as a specific target.

        Args:
            actor_id: ID of the actor.
            target_id: ID of the target to act as.

        Returns:
            True if the actor is allowed to act as the target, False otherwise.
        """
        if actor_id not in self._policies:
            return False
        policy = self._policies[actor_id]
        return target_id in policy.allowed_targets

    def is_allowed_impersonation(self, actor_id: str) -> bool:
        """Check if an actor is allowed to impersonate others.

        Args:
            actor_id: ID of the actor.

        Returns:
            True if the actor can impersonate, False otherwise or if actor not found.
        """
        if actor_id not in self._policies:
            return False
        return self._policies[actor_id].can_impersonate

    def get(self, actor_id: str) -> ActorPolicy:
        """Retrieve an actor's policy.

        Args:
            actor_id: ID of the actor.

        Returns:
            The ActorPolicy for the actor.

        Raises:
            KeyError: If actor_id not found.
        """
        if actor_id not in self._policies:
            raise KeyError(f"Actor '{actor_id}' not found")
        return self._policies[actor_id]
