"""Deferral module (AUDIT-N+39 hardened).

Parses ``$defer`` / ``$DEFER`` / ``$defer:`` directives from agent
output and forwards them into a ``PromptQueue`` so the next cycle
can pick them up.

Supports two calling conventions:

* ``inject_deferred_tasks(queue, tasks)`` -- in-memory PromptQueue,
  returns the queue. Used by the AUDIT-N+39 spec.
* ``inject_deferred_tasks(tasks, queue_path, project=, agent=)`` --
  file-backed PromptQueue, returns the count of tasks injected.
  Used by the dormant ``test_defer_injection`` corridor.

``process_output_for_deferrals`` mirrors the same shape distinction.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

__all__ = [
    "DEFER_PATTERN",
    "extract_deferred_tasks",
    "inject_deferred_tasks",
    "process_output_for_deferrals",
]


DEFER_PATTERN = re.compile(
    r"(?im)^\s*\$defer:?\s+(.+?)\s*$",
)


def extract_deferred_tasks(output: str) -> list[str]:
    """Parse ``$defer`` lines from agent output.

    @trace FR-RES-002
    """
    if not output:
        return []
    return [match.group(1).strip() for match in DEFER_PATTERN.finditer(output)]


def _looks_like_queue_object(obj: Any) -> bool:
    """Heuristic: an in-memory queue object exposes ``enqueue``."""
    return hasattr(obj, "enqueue") and hasattr(obj, "size")


def inject_deferred_tasks(
    queue_or_tasks: Any,
    tasks_or_path: Any = None,
    *,
    project: str | None = None,
    agent: str | None = None,
) -> Any:
    """Inject deferred tasks into a queue.

    Two shapes:

    * ``inject_deferred_tasks(queue: PromptQueue, tasks: list[str])``
      -- append each task as ``{prompt, source: "deferral"}`` and
      return the queue.
    * ``inject_deferred_tasks(tasks: list[str], queue_path: Path,
      project=, agent=)`` -- create / reuse the on-disk
      ``PromptQueue(<dir of queue_path>)`` and append each task with
      the supplied ``project`` / ``agent`` tags. Returns the count
      of injected tasks.
    """
    # Shape 1: in-memory PromptQueue
    if _looks_like_queue_object(queue_or_tasks) and isinstance(tasks_or_path, list):
        queue = queue_or_tasks
        for task in tasks_or_path:
            queue.enqueue({"prompt": task, "source": "deferral"})
        return queue

    # Shape 2: file-backed PromptQueue (dormant test corridor)
    tasks = queue_or_tasks
    queue_path = tasks_or_path
    if not tasks:
        return 0
    storage_dir = Path(queue_path).parent
    storage_dir.mkdir(parents=True, exist_ok=True)
    # Lazy import keeps the lightweight legacy path import-free.
    from thegent.queue.storage import PromptQueue  # noqa: PLC0415

    pq = PromptQueue(storage_dir)
    for task in tasks:
        pq.append(task, project=project, agent=agent, source="deferral")
    return len(tasks)


def process_output_for_deferrals(
    output_or_queue_path: Any,
    queue_path_or_output: Any = None,
    *,
    project: str | None = None,
) -> Any:
    """End-to-end wrapper: parse ``$defer`` lines and inject them.

    Two shapes (mirror of ``inject_deferred_tasks``):

    * ``process_output_for_deferrals(output: str)`` -- returns
      ``{deferred, processed, output}`` (AUDIT-N+39 spec).
    * ``process_output_for_deferrals(output: str, queue_path: Path,
      project=)`` -- extracts tasks, injects into the file-backed
      PromptQueue, returns ``list[str]`` of injected task descriptions.
    """
    # Shape 2: file-backed
    if isinstance(output_or_queue_path, str) and queue_path_or_output is not None:
        output = output_or_queue_path
        queue_path = queue_path_or_output
        tasks = extract_deferred_tasks(output)
        inject_deferred_tasks(tasks, queue_path, project=project)
        return tasks

    # Shape 1: AUDIT-N+39 spec dict shape
    output = output_or_queue_path
    return {
        "deferred": extract_deferred_tasks(output),
        "processed": True,
        "output": output,
    }
