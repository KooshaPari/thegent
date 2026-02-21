"""WP-5004: Non-critical deferral rules.

WL-038: $defer <task> syntax — parse agent output and inject into PromptQueue.
"""

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# WL-038: $defer <task> output parsing
# ---------------------------------------------------------------------------

# Matches lines like:
#   $defer Implement WL-039
#   $defer: Run ruff check on all files
#   $DEFER some task text
_DEFER_PATTERN = re.compile(r"^\s*\$defer:?\s+(.+)$", re.IGNORECASE)


def extract_deferred_tasks(output: str) -> list[str]:
    """Parse ``$defer <task>`` directives from agent stdout/stderr.

    Scans every line of *output* for the ``$defer`` syntax and returns the
    list of deferred task texts in order of appearance.  Lines that do not
    match are silently ignored.

    # @trace WL-038

    Args:
        output: Combined stdout/stderr text from an agent run.

    Returns:
        Ordered list of deferred task description strings (stripped).
    """
    tasks: list[str] = []
    for line in output.splitlines():
        m = _DEFER_PATTERN.match(line)
        if m:
            task_text = m.group(1).strip()
            if task_text:
                tasks.append(task_text)
    return tasks


def inject_deferred_tasks(
    deferred_tasks: list[str],
    queue_path: Path,
    project: str,
    agent: str | None = None,
) -> int:
    """Append deferred tasks to the Unified Prompt Queue as ``pending`` entries.

    Each task text becomes a new entry in *queue_path* with status ``pending``
    so it will be picked up by the next available worker.

    # @trace WL-038

    Args:
        deferred_tasks: Task texts extracted by :func:`extract_deferred_tasks`.
        queue_path:     Path to the ``prompt_queue.jsonl`` file.
        project:        Project identifier to associate with each entry.
        agent:          Optional preferred agent name for the deferred tasks.

    Returns:
        Number of tasks successfully appended.
    """
    if not deferred_tasks:
        return 0

    from thegent.queue.storage import PromptQueue

    pq = PromptQueue(queue_path.parent)
    count = 0
    for task_text in deferred_tasks:
        pq.append(task_text, project=project, agent=agent)
        _log.info("Deferred task injected into queue: %r (project=%s)", task_text, project)
        count += 1
    return count


def process_output_for_deferrals(
    output: str,
    queue_path: Path,
    project: str,
    agent: str | None = None,
) -> list[str]:
    """Extract ``$defer`` directives from *output* and inject into the queue.

    Convenience wrapper that combines :func:`extract_deferred_tasks` and
    :func:`inject_deferred_tasks`.

    # @trace WL-038

    Args:
        output:     Combined agent output (stdout + stderr).
        queue_path: Path to the ``prompt_queue.jsonl`` file.
        project:    Project identifier for queue entries.
        agent:      Optional preferred agent name.

    Returns:
        List of deferred task texts that were injected.
    """
    tasks = extract_deferred_tasks(output)
    if tasks:
        injected = inject_deferred_tasks(tasks, queue_path, project=project, agent=agent)
        _log.info("Injected %d deferred task(s) into %s", injected, queue_path)
    return tasks


class DeferralRule:
    """Rule for deferring non-critical tasks."""

    def __init__(self, id: str, condition: str, action: str) -> None:
        self.id = id
        self.condition = condition
        self.action = action


class DeferralManager:
    """Manages deferral of non-critical tasks under high load."""

    def __init__(self, settings: ThegentSettings) -> None:
        self.settings = settings
        self.deferral_log = settings.session_dir / "deferred_tasks.jsonl"

    def should_defer(self, task_priority: str, load_level: float) -> bool:
        """
        Determine if a task should be deferred.
        Priority: P0 (critical) to P3 (low).
        """
        if task_priority == "P0":
            return False  # Never defer critical tasks

        if load_level > 0.9:
            return True  # Defer all non-P0 at very high load

        if load_level > 0.7 and task_priority in ["P2", "P3"]:
            return True  # Defer low priority at high load

        return False

    def defer_task(self, task_id: str, reason: str):
        """Record a task as deferred."""
        _log.info("Deferring task %s: %s", task_id, reason)
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "task_id": task_id,
            "reason": reason,
            "status": "deferred",
        }
        self.settings.session_dir.mkdir(parents=True, exist_ok=True)
        with self.deferral_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def list_deferred(self) -> list[dict[str, Any]]:
        """List all currently deferred tasks."""
        if not self.deferral_log.exists():
            return []
        deferred = []
        with self.deferral_log.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    deferred.append(json.loads(line))
                except Exception:  # noqa: PERF203 - intentional per-item error handling
                    continue
        return deferred
