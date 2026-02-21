"""Unified Prompt Queue (FR-HAX-001).

This module provides the canonical queue implementation for storing and managing
project-aware deferred tasks.

Stores tasks in `.thegent/prompt_queue.jsonl` relative to the project root,
falling back to `~/.thegent/prompt_queue.jsonl` when outside a project.

Fields: timestamp, prompt, project_path, status (pending/claimed/done), id (ulid).

Usage:
    from thegent.queue.prompt_queue import PromptQueueManager, QueueItem

    mgr = PromptQueueManager()
    item = mgr.enqueue("Refactor auth module", project_path="/projects/myapp")
    claimed = mgr.claim()
    if claimed:
        # ... do work ...
        mgr.complete(claimed.id)

# @trace FR-HAX-001
"""

from thegent.core.prompt_queue import PromptQueueManager, QueueItem, _find_project_queue_path, _generate_ulid

__all__ = [
    "PromptQueueManager",
    "QueueItem",
    "_find_project_queue_path",
    "_generate_ulid",
]
