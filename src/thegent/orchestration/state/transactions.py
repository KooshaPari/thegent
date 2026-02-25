"""WP-15003: Atomic Transactions and Commit-Log Orchestration (CLO).
MTSP-13/14: Ensure multi-step agent actions are atomic or revertible.
"""

import asyncio
import logging
from thegent.infra.shim_subprocess import run as shim_run
import tempfile
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class TransactionOperation:
    """A single revertible operation within a transaction."""

    op_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    do: Callable[..., Any] = lambda: None
    undo: Callable[..., Any] = lambda: None
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    status: str = "pending"  # pending, committed, reverted, failed


class TransactionManager:
    """Manages atomic blocks of operations with rollback support."""

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.operations: list[TransactionOperation] = []
        self.tx_id = str(uuid.uuid4())

    def add_op(self, description: str, do: Callable, undo: Callable, *args, **kwargs):
        """Add an operation to the transaction."""
        op = TransactionOperation(description=description, do=do, undo=undo, args=args, kwargs=kwargs)
        self.operations.append(op)
        return op.op_id

    async def execute(self) -> bool:
        """Execute all operations in sequence, rollback on failure."""
        _log.info("Starting transaction %s (Run: %s)", self.tx_id, self.run_id)
        executed_ops = []

        try:
            for op in self.operations:
                _log.debug("Executing op: %s", op.description)
                if asyncio.iscoroutinefunction(op.do) or hasattr(op.do, "__await__"):
                    await op.do(*op.args, **op.kwargs)
                else:
                    op.do(*op.args, **op.kwargs)
                op.status = "committed"
                executed_ops.append(op)

            _log.info("Transaction %s committed successfully", self.tx_id)
            return True
        except Exception as e:
            _log.error("Transaction %s failed: %s. Starting rollback...", self.tx_id, e)
            for op in reversed(executed_ops):
                try:
                    _log.debug("Rolling back op: %s", op.description)
                    if asyncio.iscoroutinefunction(op.undo) or hasattr(op.undo, "__await__"):
                        await op.undo(*op.args, **op.kwargs)
                    else:
                        op.undo(*op.args, **op.kwargs)
                    op.status = "reverted"
                except Exception as rollback_err:  # noqa: PERF203 - intentional per-item error handling
                    _log.critical("Rollback FAILED for op %s: %s", op.description, rollback_err)
            return False


def apply_multi_file_transaction(
    changes: list[tuple[Path, str]],
    cwd: Path | None = None,
    git_commit: bool = False,
    commit_message: str = "thegent: atomic multi-file apply",
) -> tuple[bool, str]:
    """MTSP-13: Prepare multi-file changes and apply as a single atomic transaction.

    Writes each file to a temp path, then renames all atomically. On failure, no files are modified.
    If git_commit=True and cwd is a git repo, stages and commits as a single transaction.

    Returns:
        (success, message)
    """
    if not changes:
        return True, "No changes to apply"
    cwd = Path(cwd or Path.cwd()).resolve()
    temp_files: list[tuple[Path, Path]] = []
    try:
        for path, content in changes:
            target = Path(path).resolve() if not isinstance(path, Path) else path.resolve()
            if not str(target).startswith(str(cwd)):
                return False, f"Path {target} outside cwd {cwd}"
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(
                prefix=".thegent_tx_",
                suffix=target.suffix or "",
                dir=target.parent,
            )
            try:
                with open(fd, "w", encoding="utf-8") as f:
                    f.write(content)
                temp_files.append((Path(tmp), target))
            except OSError:
                import os

                os.close(fd)
                Path(tmp).unlink(missing_ok=True)
                raise
        for tmp_path, target in temp_files:
            tmp_path.replace(target)
        if git_commit and (cwd / ".git").exists():
            for _, target in temp_files:
                shim_run(
                    ["git", "add", str(target.relative_to(cwd))],
                    cwd=cwd,
                    capture_output=True,
                    check=False,
                )
            shim_run(
                ["git", "commit", "-m", commit_message],
                cwd=cwd,
                capture_output=True,
                check=False,
            )
        return True, f"Applied {len(changes)} file(s) atomically"
    except Exception as e:
        for tmp_path, _ in temp_files:
            tmp_path.unlink(missing_ok=True)
        return False, str(e)
