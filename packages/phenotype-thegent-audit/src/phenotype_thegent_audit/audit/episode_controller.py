"""Episode lifecycle controller.

Manages agent episode lifecycle (start/end/suspend/resume) by integrating
with ProjectRegistry for episode records and ShadowAuditGit for audit
trail entries at episode boundaries.

WBS: wp-71003-episode-ctrl
FR Traceability: FR-VER-004 (episode lifecycle management)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from phenotype_thegent_core.registry.project_registry import (
    EpisodeRecord,
    EpisodeStatus,
    ProjectRegistry,
)

if TYPE_CHECKING:
    from types import TracebackType

    from phenotype_thegent_audit.audit.shadow_audit_git import ShadowAuditGit

log = logging.getLogger(__name__)


class EpisodeController:
    """Manages the lifecycle of an agent episode.

    Can be used as a context manager::

        with EpisodeController(project_id="p1", agent_id="a1", registry=reg, shadow=shadow):
            # agent work happens here
            ...

    On normal exit the episode is marked completed; on exception it is
    marked failed.

    Parameters
    ----------
    project_id:
        The project this episode belongs to.
    agent_id:
        Identifier for the agent running this episode.
    registry:
        ProjectRegistry instance for episode CRUD.
    shadow:
        ShadowAuditGit instance for audit trail.
    metadata:
        Optional metadata to attach to the episode.
    """

    def __init__(
        self,
        project_id: str,
        agent_id: str,
        registry: ProjectRegistry,
        shadow: ShadowAuditGit,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._project_id = project_id
        self._agent_id = agent_id
        self._registry = registry
        self._shadow = shadow
        self._metadata = metadata or {}
        self._episode: EpisodeRecord | None = None
        self._started = False

    @property
    def episode(self) -> EpisodeRecord | None:
        """The current episode record, or None if not started."""
        return self._episode

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> EpisodeRecord:
        """Start a new episode. Raises RuntimeError if already started."""
        if self._started:
            raise RuntimeError("Episode already started")

        self._episode = self._registry.create_episode(
            project_id=self._project_id,
            agent_id=self._agent_id,
            metadata=self._metadata,
        )
        self._started = True

        self._shadow.record_commit(
            project_id=self._project_id,
            sha=f"ep-start-{self._episode.id}",
            message=f"episode_start agent={self._agent_id} episode={self._episode.id}",
            diff="",
        )

        log.info(
            "episode_controller.start episode=%s agent=%s project=%s",
            self._episode.id,
            self._agent_id,
            self._project_id,
        )
        return self._episode

    def end(self, *, failed: bool = False) -> EpisodeRecord:
        """End the current episode. Raises RuntimeError if not started."""
        if not self._started or self._episode is None:
            raise RuntimeError("Episode not started")

        status = EpisodeStatus.FAILED if failed else EpisodeStatus.COMPLETED
        updated = self._registry.update_episode(
            episode_id=self._episode.id,
            status=status,
        )
        if updated is None:
            raise RuntimeError(f"Failed to update episode {self._episode.id}")
        self._episode = updated

        self._shadow.record_commit(
            project_id=self._project_id,
            sha=f"ep-end-{self._episode.id}",
            message=f"episode_end agent={self._agent_id} episode={self._episode.id} status={status.value}",
            diff="",
        )

        log.info(
            "episode_controller.end episode=%s status=%s",
            self._episode.id,
            status.value,
        )
        return self._episode

    def suspend(self) -> EpisodeRecord | None:
        """Suspend the current episode. Raises RuntimeError if not started."""
        if not self._started or self._episode is None:
            raise RuntimeError("Episode not started")

        updated = self._registry.update_episode(
            episode_id=self._episode.id,
            status=EpisodeStatus.SUSPENDED,
        )
        if updated is None:
            raise RuntimeError(f"Failed to suspend episode {self._episode.id}")
        self._episode = updated

        log.info("episode_controller.suspend episode=%s", self._episode.id)
        return self._episode

    def resume(self) -> EpisodeRecord | None:
        """Resume a suspended episode. Raises RuntimeError if not suspended."""
        if not self._started or self._episode is None:
            raise RuntimeError("Episode not started")
        if self._episode.status != EpisodeStatus.SUSPENDED:
            raise RuntimeError("Episode not suspended")

        updated = self._registry.update_episode(
            episode_id=self._episode.id,
            status=EpisodeStatus.RUNNING,
        )
        if updated is None:
            raise RuntimeError(f"Failed to resume episode {self._episode.id}")
        self._episode = updated

        log.info("episode_controller.resume episode=%s", self._episode.id)
        return self._episode

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> EpisodeController:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        failed = exc_type is not None
        self.end(failed=failed)
        return False  # Do not suppress exceptions
