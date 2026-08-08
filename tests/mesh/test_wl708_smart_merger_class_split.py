"""WL708 decomposition tests for ``thegent.mesh.smart_merger``.

Pins the WL708 L1 split:
  - ``SmartMerger`` class is importable from both ``thegent.mesh.smart_merge``
    (back-compat) and ``thegent.mesh.smart_merger`` (canonical).
  - ``merge_worktree_changes`` (formerly 129 LOC god-method, CC ≥ 12) is now a
    thin composer (~30 LOC) that delegates to 5 private helpers:
      * ``_resolve_worktree_branch``     — git rev-parse wrapper
      * ``_activate_mergiraf_driver``    — sets merge.mergiraf.driver config
      * ``_checkout_target_branch``      — git checkout + conflict parsing
      * ``_perform_merge``               — git merge --no-ff wrapper
      * ``_collect_conflicts_from_output`` — static CONFLICT-line parser
  - All extracted helpers are ≤ 40 LOC and have CC ≤ 6 (CLAUDE.md max).
  - Public surface (``SmartMerger``, ``SmartMergeConfig``, ``MergeResult``,
    ``make_smart_merger``, ``MERGIRAF_EXTENSIONS``, ``is_mergiraf_available``,
    ``configure_mergiraf_driver``, ``merge_files``) is preserved at the
    ``thegent.mesh.smart_merge`` and ``thegent.mesh`` package surfaces.

@trace FR-MESH-007
"""

from __future__ import annotations

import ast
import inspect
import subprocess
import typing
from pathlib import Path
from unittest import mock

import pytest

from thegent.mesh import smart_merge as smart_merge_module
from thegent.mesh.smart_merge import (
    MERGIRAF_EXTENSIONS,
    MergeResult,
    SmartMergeConfig,
    SmartMerger,
    configure_mergiraf_driver,
    is_mergiraf_available,
    make_smart_merger,
    merge_files,
)
from thegent.mesh import smart_merger as smart_merger_module


# ---------------------------------------------------------------------------
# Import surface (back-compat + canonical)
# ---------------------------------------------------------------------------


class TestImportSurface:
    """Pin that ``SmartMerger`` is importable from both old and new paths."""

    def test_smart_merger_from_smart_merge_back_compat(self):
        """WL708: ``SmartMerger`` still importable from thegent.mesh.smart_merge."""
        from thegent.mesh.smart_merge import SmartMerger as CompatSM

        assert CompatSM is SmartMerger

    def test_smart_merger_from_smart_merger_canonical(self):
        """WL708: ``SmartMerger`` importable from thegent.mesh.smart_merger."""
        from thegent.mesh.smart_merger import SmartMerger as CanonicalSM

        assert CanonicalSM is SmartMerger

    def test_make_smart_merger_from_smart_merge_back_compat(self):
        """WL708: ``make_smart_merger`` still importable from thegent.mesh.smart_merge."""
        from thegent.mesh.smart_merge import make_smart_merger as _compat_msm

        assert _compat_msm is make_smart_merger

    def test_make_smart_merger_from_smart_merger_canonical(self):
        """WL708: ``make_smart_merger`` importable from thegent.mesh.smart_merger."""
        from thegent.mesh.smart_merger import make_smart_merger as _canonical_msm

        assert _canonical_msm is make_smart_merger

    def test_smart_merger_class_object_identity(self):
        from thegent.mesh.smart_merge import SmartMerger as SmartMergerA
        from thegent.mesh.smart_merger import SmartMerger as SmartMergerB

        assert SmartMergerA is SmartMerger
        assert SmartMergerB is SmartMerger
        assert type(SmartMergerA) is type(SmartMergerB)

    def test_smart_merger_re_exported_from_mesh_package(self):
        """``SmartMerger`` re-exported from ``thegent.mesh`` package surface."""
        from thegent.mesh import SmartMerger as PkgSM

        assert PkgSM is SmartMerger

    def test_make_smart_merger_re_exported_from_mesh_package(self):
        """``make_smart_merger`` re-exported from ``thegent.mesh`` package surface."""
        from thegent.mesh import make_smart_merger as _pkg_msm

        assert _pkg_msm is make_smart_merger

    def test_procedural_helpers_remain_in_smart_merge(self):
        """``is_mergiraf_available``, ``configure_mergiraf_driver``, ``merge_files``
        stay in ``thegent.mesh.smart_merge`` — only the class moved."""
        import thegent.mesh.smart_merge as sm

        # Each must be defined in the smart_merge module (not imported).
        assert "is_mergiraf_available" in sm.__dict__
        assert "configure_mergiraf_driver" in sm.__dict__
        assert "merge_files" in sm.__dict__
        assert "SmartMergeConfig" in sm.__dict__
        assert "MergeResult" in sm.__dict__
        assert "MERGIRAF_EXTENSIONS" in sm.__dict__

    def test_smart_merger_module_is_separate(self):
        """``smart_merger.py`` is a distinct module from ``smart_merge.py``."""
        assert smart_merger_module.__file__ != smart_merge_module.__file__
        assert smart_merger_module.__name__ == "thegent.mesh.smart_merger"
        assert smart_merge_module.__name__ == "thegent.mesh.smart_merge"


# ---------------------------------------------------------------------------
# Module shape (size + AST regression pins)
# ---------------------------------------------------------------------------


class TestModuleShapeRegression:
    """Pin CC and LOC budgets on the split modules per CLAUDE.md."""

    def _loc(self, func) -> int:
        """Return body LOC of a function (signature line + docstring excluded)."""
        try:
            src_lines, _start = inspect.getsourcelines(func)
        except (OSError, TypeError):
            return 0
        if not src_lines:
            return 0
        body_lines: list[str] = []
        in_docstring = False
        started = False
        for line in src_lines:
            if not started:
                if line.startswith((" ", "\t")):
                    started = True
                else:
                    continue
            stripped = line.strip()
            if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                in_docstring = True
                quote = stripped[:3]
                rest = stripped[3:]
                if rest.endswith(quote) and len(rest) > 3:
                    in_docstring = False
                continue
            if in_docstring:
                if '"""' in stripped or "'''" in stripped:
                    in_docstring = False
                continue
            body_lines.append(line)
        return len(body_lines)

    def test_smart_merge_module_loc_budget(self):
        """smart_merge.py slimmed from 619 LOC to ≤ 350 LOC (procedural-only)."""
        src = Path(smart_merge_module.__file__).read_text(encoding="utf-8")
        assert len(src.splitlines()) <= 350, "smart_merge.py should be ≤ 350 LOC after split"

    def test_smart_merger_module_loc_budget(self):
        """smart_merger.py new module: ≤ 400 LOC (class + helpers + factory)."""
        src = Path(smart_merger_module.__file__).read_text(encoding="utf-8")
        assert len(src.splitlines()) <= 400, "smart_merger.py should be ≤ 400 LOC"

    def test_merge_worktree_changes_composer_under_40_loc(self):
        """Composer is ≤ 40 LOC (CLAUDE.md max function length)."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        loc = self._loc(merger.merge_worktree_changes)
        assert loc <= 40, f"merge_worktree_changes is {loc} LOC, expected ≤ 40"

    def test_resolve_worktree_branch_under_40_loc(self):
        """``_resolve_worktree_branch`` ≤ 40 LOC."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        loc = self._loc(merger._resolve_worktree_branch)
        assert loc <= 40

    def test_activate_mergiraf_driver_under_40_loc(self):
        """``_activate_mergiraf_driver`` ≤ 40 LOC."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        loc = self._loc(merger._activate_mergiraf_driver)
        assert loc <= 40

    def test_checkout_target_branch_under_40_loc(self):
        """``_checkout_target_branch`` ≤ 40 LOC."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        loc = self._loc(merger._checkout_target_branch)
        assert loc <= 40

    def test_perform_merge_under_40_loc(self):
        """``_perform_merge`` ≤ 40 LOC."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        loc = self._loc(merger._perform_merge)
        assert loc <= 40

    def test_collect_conflicts_from_output_under_40_loc(self):
        """``_collect_conflicts_from_output`` ≤ 40 LOC."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        loc = self._loc(merger._collect_conflicts_from_output)
        assert loc <= 40


# ---------------------------------------------------------------------------
# Decomposed helper unit tests (isolation)
# ---------------------------------------------------------------------------


class TestResolveWorktreeBranchHelper:
    """Tests for ``SmartMerger._resolve_worktree_branch`` (extracted helper)."""

    def test_returns_branch_string_on_success(self, tmp_path):
        """Helper returns the branch name string on success."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        def fake_run(cmd, **kwargs):
            if "rev-parse" in cmd:
                return mock.Mock(returncode=0, stdout="agent/wl708\n", stderr="")
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger._resolve_worktree_branch(tmp_path)

        assert result == "agent/wl708"
        assert isinstance(result, str)

    def test_returns_MergeResult_on_timeout(self, tmp_path):
        """Helper returns ``MergeResult(success=False)`` on subprocess timeout."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False, timeout_s=1))

        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            result = merger._resolve_worktree_branch(tmp_path)

        assert isinstance(result, MergeResult)
        assert result.success is False
        assert "timeout" in result.output.lower() or "timed out" in result.output.lower()

    def test_returns_MergeResult_on_file_not_found(self, tmp_path):
        """Helper returns ``MergeResult(success=False)`` when git binary missing."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        with mock.patch("subprocess.run", side_effect=FileNotFoundError("no git")):
            result = merger._resolve_worktree_branch(tmp_path)

        assert isinstance(result, MergeResult)
        assert result.success is False

    def test_returns_MergeResult_on_empty_branch(self, tmp_path):
        """Helper returns ``MergeResult(success=False)`` when HEAD is detached/empty."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        def fake_run(cmd, **kwargs):
            return mock.Mock(returncode=0, stdout="\n", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger._resolve_worktree_branch(tmp_path)

        assert isinstance(result, MergeResult)
        assert result.success is False
        assert "empty HEAD" in result.output or "branch" in result.output.lower()


class TestActivateMergirafDriverHelper:
    """Tests for ``SmartMerger._activate_mergiraf_driver`` (extracted helper)."""

    def test_returns_true_when_binary_present_and_config_set(self, tmp_path):
        """Helper returns True and writes git config when binary is configured."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary="/usr/bin/mergiraf", fallback_to_git=True))
        with mock.patch("subprocess.run") as fake:
            result = merger._activate_mergiraf_driver(tmp_path)
        assert result is True
        # Flatten positional + keyword args, looking for any list/tuple cmd containing "config"
        all_cmd_strs: list[str] = []
        for call in fake.call_args_list:
            for arg in call.args:
                if isinstance(arg, (list, tuple)):
                    all_cmd_strs.extend(str(x) for x in arg)
            for arg in call.kwargs.values():
                if isinstance(arg, (list, tuple)):
                    all_cmd_strs.extend(str(x) for x in arg)
        assert any("config" in s for s in all_cmd_strs), f"expected git config call; got cmd strings: {all_cmd_strs}"

    def test_returns_false_when_binary_missing(self, tmp_path):
        """Helper returns False when mergiraf binary is not configured."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))
        result = merger._activate_mergiraf_driver(tmp_path)
        assert result is False

    def test_returns_false_on_timeout(self, tmp_path):
        """Helper returns False when git config times out."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary="/usr/bin/mergiraf", fallback_to_git=True, timeout_s=1))
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            result = merger._activate_mergiraf_driver(tmp_path)
        assert result is False

    def test_returns_false_on_file_not_found(self, tmp_path):
        """Helper returns False when git binary is missing."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary="/usr/bin/mergiraf", fallback_to_git=True))
        with mock.patch("subprocess.run", side_effect=FileNotFoundError("no git")):
            result = merger._activate_mergiraf_driver(tmp_path)
        assert result is False


class TestCheckoutTargetBranchHelper:
    """Tests for ``SmartMerger._checkout_target_branch`` (extracted helper)."""

    def test_returns_success_on_clean_checkout(self, tmp_path):
        """Helper returns ``MergeResult(success=True)`` when git checkout exits 0."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        def fake_run(cmd, **kwargs):
            return mock.Mock(returncode=0, stdout="Switched to branch 'main'\n", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger._checkout_target_branch(tmp_path, "main")

        assert result.success is True

    def test_returns_failure_with_conflict_list_on_checkout_failure(self, tmp_path):
        """Helper parses CONFLICT lines from a failed checkout's stderr."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        conflict_stderr = "CONFLICT (content): Merge conflict in src/foo.py\nerror: could not checkout main\n"

        def fake_run(cmd, **kwargs):
            return mock.Mock(returncode=1, stdout="", stderr=conflict_stderr)

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger._checkout_target_branch(tmp_path, "main")

        assert result.success is False
        assert "src/foo.py" in result.conflicts

    def test_returns_failure_on_timeout(self, tmp_path):
        """Helper returns ``MergeResult(success=False)`` on subprocess timeout."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False, timeout_s=1))

        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            result = merger._checkout_target_branch(tmp_path, "main")

        assert result.success is False
        assert "timeout" in result.output.lower() or "timed out" in result.output.lower()


class TestPerformMergeHelper:
    """Tests for ``SmartMerger._perform_merge`` (extracted helper)."""

    def test_returns_success_on_clean_merge(self, tmp_path):
        """Helper returns ``MergeResult(success=True)`` on git merge --no-ff exit 0."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        def fake_run(cmd, **kwargs):
            return mock.Mock(
                returncode=0,
                stdout="Merge made by the 'ort' strategy.\n",
                stderr="",
            )

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger._perform_merge(tmp_path, "main", "agent/wl708")

        assert result.success is True

    def test_returns_failure_with_conflicts_on_merge_conflict(self, tmp_path):
        """Helper parses CONFLICT lines from a failed merge."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        conflict_stdout = (
            "Auto-merging src/foo.py\n"
            "CONFLICT (content): Merge conflict in src/foo.py\n"
            "CONFLICT (content): Merge conflict in src/bar.py\n"
        )

        def fake_run(cmd, **kwargs):
            return mock.Mock(returncode=1, stdout=conflict_stdout, stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger._perform_merge(tmp_path, "main", "agent/wl708")

        assert result.success is False
        assert "src/foo.py" in result.conflicts
        assert "src/bar.py" in result.conflicts

    def test_returns_failure_on_timeout(self, tmp_path):
        """Helper returns ``MergeResult(success=False)`` on subprocess timeout."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False, timeout_s=1))

        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=1)):
            result = merger._perform_merge(tmp_path, "main", "agent/wl708")

        assert result.success is False
        assert "timed out" in result.output.lower() or "timeout" in result.output.lower()


class TestCollectConflictsFromOutputHelper:
    """Tests for ``SmartMerger._collect_conflicts_from_output`` (static helper)."""

    def test_returns_empty_list_when_no_conflicts(self):
        """Empty list when output contains no CONFLICT lines."""
        out = "Auto-merging src/foo.py\nMerge made by the 'ort' strategy.\n"
        assert SmartMerger._collect_conflicts_from_output(out) == []

    def test_parses_single_conflict(self):
        """Single CONFLICT line → single-element list with file path."""
        out = "CONFLICT (content): Merge conflict in src/foo.py\n"
        assert SmartMerger._collect_conflicts_from_output(out) == ["src/foo.py"]

    def test_parses_multiple_conflicts(self):
        """Multiple CONFLICT lines → list of file paths in order."""
        out = (
            "CONFLICT (content): Merge conflict in src/foo.py\n"
            "CONFLICT (content): Merge conflict in src/bar.py\n"
            "CONFLICT (add/add): Merge conflict in src/baz.py\n"
        )
        result = SmartMerger._collect_conflicts_from_output(out)
        assert result == ["src/foo.py", "src/bar.py", "src/baz.py"]

    def test_ignores_non_conflict_lines_with_conflict_word(self):
        """Lines containing 'CONFLICT' but not at start are ignored."""
        out = "warning: something with CONFLICT in middle of line\n"
        assert SmartMerger._collect_conflicts_from_output(out) == []

    def test_handles_empty_string(self):
        """Empty input → empty list."""
        assert SmartMerger._collect_conflicts_from_output("") == []

    def test_handles_conflict_line_without_in_separator(self):
        """Malformed CONFLICT line (no ' in ' separator) is skipped."""
        out = "CONFLICT (something else)\n"
        assert SmartMerger._collect_conflicts_from_output(out) == []


# ---------------------------------------------------------------------------
# Composer (merge_worktree_changes) integration via helpers
# ---------------------------------------------------------------------------


class TestComposerWiring:
    """Verify the composer (merge_worktree_changes) delegates correctly to its helpers."""

    def test_composer_short_circuits_on_branch_resolve_failure(self, tmp_path):
        """If ``_resolve_worktree_branch`` returns a ``MergeResult`` (error), composer
        returns it without calling merge."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        with mock.patch("subprocess.run", side_effect=FileNotFoundError("no git")):
            result = merger.merge_worktree_changes(tmp_path, "main")

        assert result.success is False
        assert "no git" in result.output

    def test_composer_short_circuits_on_checkout_failure(self, tmp_path):
        """If ``_checkout_target_branch`` fails, composer returns without calling merge."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        def fake_run(cmd, **kwargs):
            if "rev-parse" in cmd:
                return mock.Mock(returncode=0, stdout="agent/wl708\n", stderr="")
            if "checkout" in cmd:
                return mock.Mock(
                    returncode=1,
                    stdout="",
                    stderr="CONFLICT (content): Merge conflict in src/foo.py\n",
                )
            raise AssertionError(f"merge should NOT be called when checkout fails: {cmd}")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger.merge_worktree_changes(tmp_path, "main")

        assert result.success is False
        assert "src/foo.py" in result.conflicts

    def test_composer_happy_path_calls_all_helpers(self, tmp_path):
        """Happy path: composer resolves branch, activates driver, checks out, merges."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            if "rev-parse" in cmd:
                return mock.Mock(returncode=0, stdout="agent/wl708\n", stderr="")
            if "config" in cmd and "merge.mergiraf" in " ".join(cmd):
                return mock.Mock(returncode=0, stdout="", stderr="")
            if "checkout" in cmd:
                return mock.Mock(returncode=0, stdout="Switched to branch 'main'\n", stderr="")
            if "merge" in cmd:
                return mock.Mock(
                    returncode=0,
                    stdout="Merge made by the 'ort' strategy.\n",
                    stderr="",
                )
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger.merge_worktree_changes(tmp_path, "main")

        assert result.success is True
        # Verify the expected sequence: rev-parse, checkout, merge
        assert any("rev-parse" in cmd for cmd in calls)
        assert any("checkout" in cmd for cmd in calls)
        assert any("merge" in cmd for cmd in calls)

    def test_composer_collects_conflicts_on_failed_merge(self, tmp_path):
        """When merge fails, composer populates ``conflicts`` from output."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary=None, fallback_to_git=False))

        def fake_run(cmd, **kwargs):
            if "rev-parse" in cmd:
                return mock.Mock(returncode=0, stdout="agent/wl708\n", stderr="")
            if "checkout" in cmd:
                return mock.Mock(returncode=0, stdout="Switched to branch 'main'\n", stderr="")
            if "merge" in cmd:
                return mock.Mock(
                    returncode=1,
                    stdout="CONFLICT (content): Merge conflict in src/foo.py\n",
                    stderr="",
                )
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger.merge_worktree_changes(tmp_path, "main")

        assert result.success is False
        assert "src/foo.py" in result.conflicts

    def test_composer_preserves_used_mergiraf_flag_on_checkout_failure(self, tmp_path):
        """``used_mergiraf`` flag from step 2 is preserved when step 3 fails."""
        merger = SmartMerger(SmartMergeConfig(mergiraf_binary="/usr/bin/mergiraf", fallback_to_git=True))

        def fake_run(cmd, **kwargs):
            if "rev-parse" in cmd:
                return mock.Mock(returncode=0, stdout="agent/wl708\n", stderr="")
            if "config" in cmd and "merge.mergiraf" in " ".join(cmd):
                return mock.Mock(returncode=0, stdout="", stderr="")
            if "checkout" in cmd:
                return mock.Mock(
                    returncode=1,
                    stdout="",
                    stderr="error: pathspec 'main' did not match\n",
                )
            raise AssertionError(f"merge should not run when checkout fails: {cmd}")

        with mock.patch("subprocess.run", side_effect=fake_run):
            result = merger.merge_worktree_changes(tmp_path, "main")

        assert result.success is False
        # The driver activation succeeded → used_mergiraf must be True
        assert result.used_mergiraf is True


# ---------------------------------------------------------------------------
# Back-compat + public surface regressions
# ---------------------------------------------------------------------------


class TestPublicSurfaceRegression:
    """Pin that the WL708 split preserves every public name."""

    REQUIRED_NAMES: typing.ClassVar[list[str]] = [
        "MERGIRAF_EXTENSIONS",
        "SmartMergeConfig",
        "MergeResult",
        "is_mergiraf_available",
        "configure_mergiraf_driver",
        "merge_files",
        "make_smart_merger",
        "SmartMerger",
    ]

    def test_smart_merge_module_exposes_all_names(self):
        """All public names still defined in ``thegent.mesh.smart_merge``."""
        for name in self.REQUIRED_NAMES:
            assert name in smart_merge_module.__dict__, f"{name} missing from smart_merge.py"

    def test_smart_merger_module_exposes_class_and_factory(self):
        """``smart_merger.py`` exposes the class and factory (canonical home)."""
        for name in ("SmartMerger", "make_smart_merger", "MergeResult", "SmartMergeConfig"):
            assert name in smart_merger_module.__dict__, f"{name} missing from smart_merger.py"

    def test_mesh_package_reexports_class_and_factory(self):
        """``thegent.mesh.__init__`` re-exports ``SmartMerger`` and ``make_smart_merger``."""
        from thegent import mesh as mesh_pkg

        for name in ("SmartMerger", "SmartMergeConfig", "MergeResult", "make_smart_merger"):
            assert name in mesh_pkg.__dict__, f"{name} missing from thegent.mesh.__init__"


# ---------------------------------------------------------------------------
# Factory delegation
# ---------------------------------------------------------------------------


class TestFactoryDelegation:
    """Verify ``make_smart_merger`` from both paths returns the same class."""

    def test_factory_from_smart_merge_returns_canonical_class(self):
        """``thegent.mesh.smart_merge.make_smart_merger()`` returns the class from
        ``thegent.mesh.smart_merger``."""
        from thegent.mesh.smart_merger import SmartMerger as CanonicalSM

        merger = make_smart_merger()
        assert isinstance(merger, CanonicalSM)

    def test_factory_returns_class_instance(self):
        """``make_smart_merger()`` returns a ``SmartMerger`` instance."""
        merger = make_smart_merger()
        assert isinstance(merger, SmartMerger)

    def test_factory_accepts_config(self):
        """``make_smart_merger(config)`` passes the config through."""
        cfg = SmartMergeConfig(mergiraf_binary="/opt/test/mergiraf", fallback_to_git=False)
        merger = make_smart_merger(cfg)
        assert merger._config is cfg

    def test_factory_none_uses_defaults(self):
        """``make_smart_merger(None)`` is the same as ``make_smart_merger()``."""
        a = make_smart_merger(None)
        b = make_smart_merger()
        assert type(a) is type(b)
        assert a._config.mergiraf_binary is None
        assert b._config.fallback_to_git is True
