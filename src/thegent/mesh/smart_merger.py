"""SmartMerger — class-based API for AST-aware merges (heliosShield-smart-merge).

Extracted from ``smart_merge.py`` as part of the WL708 L1 architecture split.
Provides the :class:`SmartMerger` thin coordinator for integration with
:class:`~thegent_gitops.worktree.WorktreePool` (FR-MESH-007).

The procedural helpers (``is_mergiraf_available``, ``configure_mergiraf_driver``,
``merge_files``) remain in :mod:`thegent.mesh.smart_merge`.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from thegent.infra.shim_subprocess import run as shim_run

from thegent.mesh.smart_merge import (
    MERGIRAF_EXTENSIONS,  # noqa: F401  (re-export for back-compat)
    MergeResult,
    SmartMergeConfig,
    _merge_with_git_merge_file,
)

__all__ = [
    "SmartMerger",
    "MergeResult",  # re-exported for callers that do `from .smart_merger import MergeResult`
    "SmartMergeConfig",  # re-exported for convenience
    "MERGIRAF_EXTENSIONS",  # re-exported for convenience
    "make_smart_merger",
]


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------


def make_smart_merger(config: SmartMergeConfig | None = None) -> SmartMerger:
    """Create a :class:`SmartMerger` instance, reading env var for binary path.

    When *config* is ``None``, a default :class:`SmartMergeConfig` is used.
    The mergiraf binary path is resolved from (in priority order):

    1. ``config.mergiraf_binary`` if provided.
    2. The ``THGENT_MERGIRAF_BINARY`` environment variable.
    3. ``shutil.which("mergiraf")`` (PATH search).

    @trace heliosShield-smart-merge / FR-MESH-007
    """
    return SmartMerger(config)


class SmartMerger:
    """Thin coordinator for AST-aware merges via Mergiraf with git fallback.

    This class wraps subprocess calls to mergiraf (or ``git merge-file``) and
    provides a structured :class:`MergeResult` rather than a bare bool.  It is
    intentionally thin: it does *not* implement merge logic itself.

    Typical usage::

        merger = make_smart_merger()
        result = merger.merge(base, ours, theirs, output)
        if not result.success:
            print("Conflicts:", result.conflicts)

    @trace heliosShield-smart-merge / FR-MESH-007
    """

    def __init__(self, config: SmartMergeConfig | None = None) -> None:
        self._config = config or SmartMergeConfig()
        self._binary: str | None = self._resolve_binary()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if the mergiraf binary can be located.

        @trace FR-MESH-007
        """
        return self._binary is not None

    def merge(
        self,
        base: str,
        ours: str,
        theirs: str,
        output: str,
        *,
        path_hint: str | None = None,
    ) -> MergeResult:
        """Perform a three-way merge of three file paths.

        Calls mergiraf when available; otherwise falls back to
        ``git merge-file`` (if :attr:`SmartMergeConfig.fallback_to_git`
        is True).

        Args:
            base:      Common ancestor file path (string).
            ours:      Our version file path (string).
            theirs:    Their version file path (string).
            output:    Destination file path for the merged result (string).
            path_hint: Logical repository path for language detection.

        Returns:
            :class:`MergeResult` describing whether the merge was clean.

        @trace FR-MESH-007
        """
        base_p = Path(base)
        ours_p = Path(ours)
        theirs_p = Path(theirs)
        output_p = Path(output)

        if self._binary:
            return self._run_mergiraf(base_p, ours_p, theirs_p, output_p, path_hint=path_hint)

        if self._config.fallback_to_git:
            return self._run_git_fallback(base_p, ours_p, theirs_p, output_p)

        return MergeResult(success=False, output="mergiraf unavailable and fallback disabled")

    def merge_worktree_changes(
        self,
        worktree_path: Path,
        target_branch: str,
    ) -> MergeResult:
        """Merge all uncommitted changes in *worktree_path* into *target_branch*.

        Thin composer: resolves worktree branch, activates mergiraf driver,
        checks out the target branch, performs the merge, then collects
        any conflict file paths from the output.

        @trace FR-MESH-007
        """
        # 1. Resolve worktree branch (returns MergeResult on failure)
        branch_or_error = self._resolve_worktree_branch(worktree_path)
        if isinstance(branch_or_error, MergeResult):
            return branch_or_error
        worktree_branch = branch_or_error

        # 2. Activate mergiraf driver in git config (if available)
        used_mergiraf = self._activate_mergiraf_driver(worktree_path)

        # 3. Checkout target branch
        checkout = self._checkout_target_branch(worktree_path, target_branch)
        if not checkout.success:
            return self._with_used_flag(checkout, used_mergiraf)

        # 4. Perform the merge
        merged = self._perform_merge(worktree_path, target_branch, worktree_branch)
        if not merged.success:
            return self._with_used_flag(
                MergeResult(
                    success=False,
                    conflicts=self._collect_conflicts_from_output(merged.output),
                    output=merged.output,
                ),
                used_mergiraf,
            )
        return MergeResult(
            success=True,
            conflicts=[],
            output=merged.output,
            used_mergiraf=used_mergiraf,
        )

    @staticmethod
    def _with_used_flag(result: MergeResult, used_mergiraf: bool) -> MergeResult:
        """Return a copy of *result* with ``used_mergiraf`` overridden."""
        return MergeResult(
            success=result.success,
            conflicts=result.conflicts,
            output=result.output,
            used_mergiraf=used_mergiraf,
        )

    # ------------------------------------------------------------------
    # Private helpers (merge_worktree_changes decomposition)
    # ------------------------------------------------------------------

    def _resolve_worktree_branch(self, worktree_path: Path) -> str | MergeResult:
        """Return the current branch name in *worktree_path*, or a MergeResult on failure."""
        try:
            branch_result = shim_run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(worktree_path),
                capture_output=True,
                text=True,
                check=False,
                timeout=self._config.timeout_s,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return MergeResult(success=False, output=str(exc))

        branch = branch_result.stdout.strip()
        if not branch:
            return MergeResult(
                success=False,
                output="failed to resolve worktree branch (empty HEAD)",
            )
        return branch

    def _activate_mergiraf_driver(self, worktree_path: Path) -> bool:
        """Register mergiraf as the merge driver in git config. Returns True if activated."""
        if not (self._binary and self._config.fallback_to_git):
            return False
        try:
            shim_run(
                [
                    "git",
                    "config",
                    "merge.mergiraf.driver",
                    f"{self._binary} merge --git %O %A %B -p %P",
                ],
                cwd=str(worktree_path),
                capture_output=True,
                check=False,
                timeout=self._config.timeout_s,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        return True

    def _checkout_target_branch(
        self,
        worktree_path: Path,
        target_branch: str,
    ) -> MergeResult:
        """Run ``git checkout <target_branch>``; collect conflict paths on failure."""
        try:
            checkout_result = shim_run(
                ["git", "checkout", target_branch],
                cwd=str(worktree_path),
                capture_output=True,
                text=True,
                check=False,
                timeout=self._config.timeout_s,
            )
        except subprocess.TimeoutExpired as exc:
            return MergeResult(success=False, output=f"checkout timed out: {exc}")
        except FileNotFoundError as exc:
            return MergeResult(success=False, output=str(exc))

        if checkout_result.returncode == 0:
            return MergeResult(success=True)

        combined = checkout_result.stderr or checkout_result.stdout or ""
        return MergeResult(
            success=False,
            conflicts=self._collect_conflicts_from_output(combined),
            output=f"failed to checkout target branch {target_branch}: {combined}",
        )

    def _perform_merge(
        self,
        worktree_path: Path,
        target_branch: str,
        worktree_branch: str,
    ) -> MergeResult:
        """Run ``git merge --no-ff <worktree_branch>`` and capture the result."""
        try:
            result = shim_run(
                [
                    "git",
                    "merge",
                    "--no-ff",
                    "-m",
                    f"Merge {worktree_branch} into {target_branch} (smart-merge)",
                    worktree_branch,
                ],
                cwd=str(worktree_path),
                capture_output=True,
                text=True,
                check=False,
                timeout=self._config.timeout_s,
            )
        except subprocess.TimeoutExpired:
            return MergeResult(
                success=False,
                output=f"git merge timed out after {self._config.timeout_s}s",
            )
        except FileNotFoundError as exc:
            return MergeResult(success=False, output=str(exc))

        combined = (result.stdout or "") + (result.stderr or "")
        return MergeResult(
            success=result.returncode == 0,
            conflicts=self._collect_conflicts_from_output(combined) if result.returncode != 0 else [],
            output=combined,
        )

    @staticmethod
    def _collect_conflicts_from_output(combined_output: str) -> list[str]:
        """Parse ``CONFLICT (content): Merge conflict in <path>`` lines."""
        conflicts: list[str] = []
        for line in combined_output.splitlines():
            if line.startswith("CONFLICT"):
                # e.g. "CONFLICT (content): Merge conflict in src/foo.py"
                parts = line.split(" in ", maxsplit=1)
                if len(parts) == 2:
                    conflicts.append(parts[1].strip())
        return conflicts

    # ------------------------------------------------------------------
    # Private helpers (binary resolution + low-level run)
    # ------------------------------------------------------------------

    def _resolve_binary(self) -> str | None:
        """Determine the path to the mergiraf binary."""
        if self._config.mergiraf_binary:
            return self._config.mergiraf_binary
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        env_bin = settings.mergiraf_binary
        if env_bin:
            return env_bin
        return shutil.which("mergiraf")

    def _run_mergiraf(
        self,
        base: Path,
        ours: Path,
        theirs: Path,
        output: Path,
        *,
        path_hint: str | None,
    ) -> MergeResult:
        """Invoke mergiraf and parse the result into a MergeResult."""
        assert self._binary is not None
        cmd: list[str] = [self._binary, "merge", str(base), str(ours), str(theirs)]
        if output:
            cmd += ["-o", str(output)]
        if path_hint:
            cmd += ["-p", path_hint]

        try:
            result = shim_run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=self._config.timeout_s,
            )
        except subprocess.TimeoutExpired:
            if self._config.fallback_to_git:
                return self._run_git_fallback(base, ours, theirs, output)
            return MergeResult(success=False, output="mergiraf timed out")
        except FileNotFoundError:
            if self._config.fallback_to_git:
                return self._run_git_fallback(base, ours, theirs, output)
            return MergeResult(success=False, output="mergiraf binary not found")

        combined = (result.stdout or "") + (result.stderr or "")

        if result.returncode == 0:
            if not output.exists() and result.stdout:
                output.write_text(result.stdout, encoding="utf-8")
            return MergeResult(success=True, output=combined, used_mergiraf=True)

        if result.returncode == 1:
            # Conflicts present but output written with markers
            if not output.exists() and result.stdout:
                output.write_text(result.stdout, encoding="utf-8")
            return MergeResult(success=False, output=combined, used_mergiraf=True)

        # Hard failure (exit >=2): fall through to diff3 fallback
        if self._config.fallback_to_git:
            return self._run_git_fallback(base, ours, theirs, output)

        return MergeResult(success=False, output=combined, used_mergiraf=True)

    def _run_git_fallback(
        self,
        base: Path,
        ours: Path,
        theirs: Path,
        output: Path,
    ) -> MergeResult:
        """Fall back to ``git merge-file --diff3``."""
        success = _merge_with_git_merge_file(base, ours, theirs, output)
        return MergeResult(success=success, used_mergiraf=False)
