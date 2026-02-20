"""MAIFRunner - thin wrapper for recording run lifecycle as MAIF artifacts.

Optional/non-blocking: gated by THGENT_MAIF_ENABLED env var (default disabled).
All errors are caught and logged; this module never raises to the caller.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from pathlib import Path
from typing import Optional

_log = logging.getLogger(__name__)

# Default DB path under the user's home directory thegent directory
_DEFAULT_DB_PATH = Path.home() / ".thegent" / "maif" / "artifacts.db"


class MAIFRunner:
    """Thin wrapper that records agent run lifecycle as signed MAIF artifacts.

    Enabled when ``THGENT_MAIF_ENABLED=1`` is set in the environment.
    The DB path is read from ``THGENT_MAIF_DB_PATH`` (default:
    ``~/.thegent/maif/artifacts.db``).

    All public methods catch every exception internally and log at DEBUG level
    so that MAIF recording never blocks or fails execution.
    """

    def __init__(self) -> None:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        self._enabled: bool = settings.maif_enabled
        self._db_path: Path = settings.maif_db_path or _DEFAULT_DB_PATH
        self._generator: object | None = None  # MAIFArtifactGenerator, lazy-init
        self._session_id: str = uuid.uuid4().hex  # one session per MAIFRunner instance

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_generator(self) -> object | None:
        """Lazily initialise MAIFArtifactGenerator; return None on failure."""
        if self._generator is not None:
            return self._generator
        try:
            from thegent.maif.artifact_generator import MAIFArtifactGenerator
            from thegent.maif.crypto import SigningKey

            signing_key = SigningKey.generate()
            self._generator = MAIFArtifactGenerator(signing_key)
        except Exception as exc:
            _log.debug("MAIFRunner: failed to init generator: %s", exc)
            return None
        return self._generator

    def _store_artifact(self, artifact: object) -> None:
        """Persist a MAIFArtifact to the configured DB path; swallow all errors."""
        try:
            from thegent.maif.store import MAIFArtifactStore

            store = MAIFArtifactStore(self._db_path)
            store.store(artifact)  # type: ignore[arg-type]
        except Exception as exc:
            _log.debug("MAIFRunner: failed to store artifact: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_run_start(
        self,
        run_id: str,
        owner: str,
        prompt: str,
        agent: str,
    ) -> str | None:
        """Record the start of an agent run as a MAIF artifact.

        Args:
            run_id: Unique identifier for the run (e.g. ``run_abc123``).
            owner: The user or system that initiated the run.
            prompt: The prompt sent to the agent (may be truncated in the artifact).
            agent: The agent/provider name (e.g. ``"claude"``, ``"antigravity"``).

        Returns:
            The artifact ``id`` (hex UUID) when MAIF is enabled and recording
            succeeds; ``None`` otherwise.
        """
        if not self._enabled:
            return None
        try:
            from thegent.maif.crypto import hash_data
            from thegent.maif.models import ActionType

            generator = self._get_generator()
            if generator is None:
                return None

            input_payload = f"run_id={run_id} owner={owner} agent={agent} prompt={prompt[:200]}"
            input_bytes = input_payload.encode()
            output_bytes = b""  # no output yet at start

            artifact = generator.create_artifact(  # type: ignore[union-attr]
                action_type=ActionType.OTHER,
                agent_id=agent or "unknown",
                session_id=run_id,
                input_data=input_bytes,
                output_data=output_bytes,
                metadata={
                    "event": "run_start",
                    "run_id": run_id,
                    "owner": owner,
                    "agent": agent,
                    "prompt_preview": prompt[:200],
                    "timestamp": int(time.time()),
                },
            )
            self._store_artifact(artifact)
            _log.debug("MAIFRunner: recorded run_start artifact %s for run %s", artifact.id, run_id)
            return artifact.id
        except Exception as exc:
            _log.debug("MAIFRunner.record_run_start failed: %s", exc)
            return None

    def record_run_end(
        self,
        run_id: str,
        status: str,
        output_summary: str,
    ) -> str | None:
        """Record the completion of an agent run as a MAIF artifact.

        Args:
            run_id: Unique identifier for the run, matching the one passed to
                :meth:`record_run_start`.
            status: Final status string (e.g. ``"completed"``, ``"failed"``,
                ``"timed_out"``).
            output_summary: Truncated stdout/stderr summary for the artifact.

        Returns:
            The artifact ``id`` (hex UUID) when MAIF is enabled and recording
            succeeds; ``None`` otherwise.
        """
        if not self._enabled:
            return None
        try:
            from thegent.maif.models import ActionType

            generator = self._get_generator()
            if generator is None:
                return None

            input_bytes = f"run_id={run_id} status={status}".encode()
            output_bytes = output_summary[:500].encode()

            artifact = generator.create_artifact(  # type: ignore[union-attr]
                action_type=ActionType.OTHER,
                agent_id="thegent-runner",
                session_id=run_id,
                input_data=input_bytes,
                output_data=output_bytes,
                metadata={
                    "event": "run_end",
                    "run_id": run_id,
                    "status": status,
                    "output_preview": output_summary[:200],
                    "timestamp": int(time.time()),
                },
            )
            self._store_artifact(artifact)
            _log.debug("MAIFRunner: recorded run_end artifact %s for run %s (status=%s)", artifact.id, run_id, status)
            return artifact.id
        except Exception as exc:
            _log.debug("MAIFRunner.record_run_end failed: %s", exc)
            return None
