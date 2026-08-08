"""WL709 decomposition tests for ``thegent.mesh.git_parallelism``.

Pins the WL709 L1 split:

* The 397-LOC god-module ``thegent.mesh.git_parallelism`` is now a
  4-submodule package: ``helpers``, ``pool_state``, ``worktree_context``
  and ``pool``.  Imports from the legacy flat path continue to work
  because the package ``__init__.py`` re-exports every public name.
* Each submodule is constrained to a strict LOC budget (CLAUDE.md).
* Each public class lives in its own canonical module and is importable
  from both the package root (back-compat) and the canonical module.
* ``isinstance`` / ``__module__`` checks confirm that the package
  re-exports are the *same* objects, not proxies.
* The split is purely structural — no behaviour change.

@trace FR-MESH-006, FR-MESH-007
"""

from __future__ import annotations

import inspect
import subprocess
import typing
from pathlib import Path
from unittest import mock

import pytest

from thegent.mesh import git_parallelism as git_parallelism_pkg
from thegent.mesh.git_parallelism import (
    _STATE_FILENAME,
    _WORKTREE_BASE,
    _PoolStateLock,
    _atomic_write,
    _git_available,
    _project_hash,
    _run,
    _worktrees_supported,
    tempfile_mkstemp,
)
from thegent.mesh.git_parallelism import pool as pool_module
from thegent.mesh.git_parallelism import pool_state as pool_state_module
from thegent.mesh.git_parallelism import worktree_context as worktree_context_module
from thegent.mesh.git_parallelism import helpers as helpers_module
from thegent.mesh.git_parallelism.helpers import _atomic_write as _atomic_write_canonical
from thegent.mesh.git_parallelism.pool import WorktreePool
from thegent.mesh.git_parallelism.worktree_context import WorktreeContext


# ---------------------------------------------------------------------------
# Package + submodule import surface
# ---------------------------------------------------------------------------


class TestPackageSurface:
    """Verify the package structure and re-exports."""

    def test_git_parallelism_is_package_not_module(self):
        """``thegent.mesh.git_parallelism`` is a package (has __path__)."""
        assert hasattr(git_parallelism_pkg, "__path__"), "git_parallelism should be a package after the WL709 split"
        assert git_parallelism_pkg.__file__ is not None

    def test_submodules_exist(self):
        """All four WL709 submodules are importable."""
        assert helpers_module.__file__ is not None
        assert pool_state_module.__file__ is not None
        assert worktree_context_module.__file__ is not None
        assert pool_module.__file__ is not None

    def test_submodule_names_are_correct(self):
        """Submodule ``__name__`` attributes match the canonical paths."""
        assert helpers_module.__name__ == "thegent.mesh.git_parallelism.helpers"
        assert pool_state_module.__name__ == "thegent.mesh.git_parallelism.pool_state"
        assert worktree_context_module.__name__ == "thegent.mesh.git_parallelism.worktree_context"
        assert pool_module.__name__ == "thegent.mesh.git_parallelism.pool"

    def test_submodule_files_are_distinct(self):
        """Each submodule has a distinct ``__file__`` path."""
        files = {
            helpers_module.__file__,
            pool_state_module.__file__,
            worktree_context_module.__file__,
            pool_module.__file__,
        }
        assert len(files) == 4, "submodule files must be distinct"


# ---------------------------------------------------------------------------
# Re-export identity (package is the canonical home)
# ---------------------------------------------------------------------------


class TestReexportIdentity:
    """``git_parallelism`` re-exports must be the *same* objects as the canonical modules."""

    def test_worktree_pool_identity(self):
        """``WorktreePool`` from the package is the same class as ``pool.WorktreePool``."""
        assert git_parallelism_pkg.WorktreePool is pool_module.WorktreePool
        assert WorktreePool is pool_module.WorktreePool

    def test_worktree_context_identity(self):
        """``WorktreeContext`` from the package is the same as the canonical module."""
        assert git_parallelism_pkg.WorktreeContext is worktree_context_module.WorktreeContext
        assert WorktreeContext is worktree_context_module.WorktreeContext

    def test_pool_state_lock_identity(self):
        """``_PoolStateLock`` from the package is the same class as the canonical module."""
        assert _PoolStateLock is pool_state_module._PoolStateLock

    def test_helpers_identity(self):
        """All helpers re-exported from the package are the same callable as canonical."""
        assert _project_hash is helpers_module._project_hash
        assert _atomic_write is helpers_module._atomic_write
        assert _atomic_write is _atomic_write_canonical
        assert tempfile_mkstemp is helpers_module.tempfile_mkstemp
        assert _run is helpers_module._run
        assert _git_available is helpers_module._git_available
        assert _worktrees_supported is helpers_module._worktrees_supported

    def test_constants_identity(self):
        """Path constants are re-exported identically."""
        assert _WORKTREE_BASE is helpers_module._WORKTREE_BASE
        assert _STATE_FILENAME is helpers_module._STATE_FILENAME

    def test_class_module_strings(self):
        """Each class's ``__module__`` points to its canonical submodule."""
        assert WorktreePool.__module__ == "thegent.mesh.git_parallelism.pool"
        assert WorktreeContext.__module__ == "thegent.mesh.git_parallelism.worktree_context"
        assert _PoolStateLock.__module__ == "thegent.mesh.git_parallelism.pool_state"


# ---------------------------------------------------------------------------
# Module shape (LOC + CC budgets per CLAUDE.md)
# ---------------------------------------------------------------------------


class TestModuleShapeRegression:
    """Pin the WL709 LOC budgets on each submodule."""

    def test_helpers_module_under_200_loc(self):
        """``helpers.py`` ≤ 200 LOC (utility helpers + constants)."""
        src = Path(helpers_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 200, f"helpers.py is {loc} LOC, expected ≤ 200"

    def test_pool_state_module_under_140_loc(self):
        """``pool_state.py`` ≤ 140 LOC (_PoolStateLock class)."""
        src = Path(pool_state_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 140, f"pool_state.py is {loc} LOC, expected ≤ 140"

    def test_worktree_context_module_under_140_loc(self):
        """``worktree_context.py`` ≤ 140 LOC (WorktreeContext dataclass)."""
        src = Path(worktree_context_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 140, f"worktree_context.py is {loc} LOC, expected ≤ 140"

    def test_pool_module_under_320_loc(self):
        """``pool.py`` ≤ 320 LOC (WorktreePool class + internal helpers)."""
        src = Path(pool_module.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 320, f"pool.py is {loc} LOC, expected ≤ 320"

    def test_init_module_under_60_loc(self):
        """``__init__.py`` ≤ 60 LOC (pure re-exports)."""
        src = Path(git_parallelism_pkg.__file__).read_text(encoding="utf-8")
        loc = len(src.splitlines())
        assert loc <= 60, f"__init__.py is {loc} LOC, expected ≤ 60"

    def test_total_split_is_smaller_per_module_than_original(self):
        """After the split, no single module exceeds the original 397 LOC."""
        # Pulled from the WL709 commit summary: original was 397 LOC.
        for module in (
            helpers_module,
            pool_state_module,
            worktree_context_module,
            pool_module,
        ):
            src = Path(module.__file__).read_text(encoding="utf-8")
            loc = len(src.splitlines())
            assert loc < 397, f"{module.__name__} is {loc} LOC, larger than the original 397"

    def _cognitive_complexity(self, func: object) -> int:
        """Rough CC estimate: count decision points + 1."""
        try:
            src_lines, _start = inspect.getsourcelines(func)
        except (OSError, TypeError):
            return 0
        text = "".join(src_lines)
        # Decision-point keywords (mirrors radon.cc_visit approximation)
        keywords = (
            "if ",
            "elif ",
            "else:",
            "for ",
            "while ",
            "and ",
            "or ",
            "except ",
            "with ",
        )
        cc = 1
        for kw in keywords:
            cc += text.count(kw)
        return cc

    def test_pool_init_under_complexity_budget(self):
        """``WorktreePool.__init__`` has manageable CC."""
        cc = self._cognitive_complexity(WorktreePool.__init__)
        # CLAUDE.md says CC ≤ 15.  Pool __init__ is straightforward but has
        # several boolean expressions, so we allow a generous ceiling.
        assert cc <= 15, f"WorktreePool.__init__ CC is {cc}, expected ≤ 15"

    def test_acquire_worktree_under_complexity_budget(self):
        """``acquire_worktree`` has CC ≤ 15."""
        cc = self._cognitive_complexity(WorktreePool.acquire_worktree)
        assert cc <= 15, f"acquire_worktree CC is {cc}, expected ≤ 15"

    def test_release_worktree_under_complexity_budget(self):
        """``release_worktree`` has CC ≤ 15."""
        cc = self._cognitive_complexity(WorktreePool.release_worktree)
        assert cc <= 15, f"release_worktree CC is {cc}, expected ≤ 15"

    def test_cleanup_stale_under_complexity_budget(self):
        """``cleanup_stale`` has CC ≤ 15."""
        cc = self._cognitive_complexity(WorktreePool.cleanup_stale)
        assert cc <= 15, f"cleanup_stale CC is {cc}, expected ≤ 15"


# ---------------------------------------------------------------------------
# Public surface regression (back-compat pin)
# ---------------------------------------------------------------------------


class TestPublicSurfaceRegression:
    """Pin the complete public surface after the WL709 split."""

    REQUIRED_NAMES: typing.ClassVar[list[str]] = [
        "WorktreeContext",
        "WorktreePool",
        "_PoolStateLock",
        "_project_hash",
        "_atomic_write",
        "tempfile_mkstemp",
        "_run",
        "_git_available",
        "_worktrees_supported",
        "_WORKTREE_BASE",
        "_STATE_FILENAME",
    ]

    def test_all_names_present_at_package_root(self):
        """Every public name is reachable from ``thegent.mesh.git_parallelism``."""
        for name in self.REQUIRED_NAMES:
            assert name in git_parallelism_pkg.__dict__, f"{name} missing from thegent.mesh.git_parallelism"

    def test_worktree_pool_lives_in_pool_submodule(self):
        """``WorktreePool`` is defined in the ``pool`` submodule (not __init__)."""
        assert "WorktreePool" in pool_module.__dict__
        # It must NOT be defined in the package __init__ body itself
        # (only re-exported via ``from .pool import WorktreePool``).
        src = Path(git_parallelism_pkg.__file__).read_text(encoding="utf-8")
        # The init may import WorktreePool but the class definition should
        # NOT live in the init source itself.
        assert "class WorktreePool" not in src

    def test_worktree_context_lives_in_worktree_context_submodule(self):
        """``WorktreeContext`` is defined in the ``worktree_context`` submodule."""
        src = Path(git_parallelism_pkg.__file__).read_text(encoding="utf-8")
        assert "class WorktreeContext" not in src
        assert "class WorktreeContext" in Path(worktree_context_module.__file__).read_text(encoding="utf-8")

    def test_pool_state_lock_lives_in_pool_state_submodule(self):
        """``_PoolStateLock`` is defined in the ``pool_state`` submodule."""
        src = Path(git_parallelism_pkg.__file__).read_text(encoding="utf-8")
        assert "class _PoolStateLock" not in src
        assert "class _PoolStateLock" in Path(pool_state_module.__file__).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Back-compat behavioural verification (no functional change)
# ---------------------------------------------------------------------------


class TestBackCompatBehaviour:
    """Verify the split is purely structural — all helpers still work."""

    def test_project_hash_still_works(self, tmp_path):
        """``_project_hash`` from the package behaves identically."""
        h1 = _project_hash(tmp_path)
        h2 = git_parallelism_pkg._project_hash(tmp_path)
        assert h1 == h2
        assert len(h1) == 12
        assert all(c in "0123456789abcdef" for c in h1)

    def test_atomic_write_still_works(self, tmp_path):
        """``_atomic_write`` from the package behaves identically."""
        target = tmp_path / "out.txt"
        _atomic_write(target, "abc=def\n")
        assert target.read_text() == "abc=def\n"

    def test_pool_state_lock_still_works(self, tmp_path):
        """``_PoolStateLock`` from the package behaves identically."""
        state_path = tmp_path / "x.txt"
        with _PoolStateLock(state_path) as lock:
            lock.write({"a": "1"})
        with _PoolStateLock(state_path) as lock:
            assert lock.read() == {"a": "1"}

    def test_worktree_pool_constructs_via_package_import(self, tmp_path):
        """A ``WorktreePool`` constructed via the package import works."""
        project = tmp_path / "p"
        project.mkdir()
        pool = WorktreePool(project, pool_root=tmp_path / ".pool")
        assert pool.project_root == project.resolve()
        assert pool._pool_dir.name == _project_hash(project.resolve())

    def test_worktree_context_constructs_via_package_import(self, tmp_path):
        """A ``WorktreeContext`` constructed via the package import works."""
        ctx = WorktreeContext(
            agent_id="wl709",
            path=tmp_path,
            branch="agent/wl709",
            project_root=tmp_path,
        )
        assert ctx.agent_id == "wl709"
        assert ctx.release() is False  # no _pool_ref

    def test_git_available_returns_bool(self, tmp_path):
        """``_git_available`` returns a bool (not raises)."""
        result = _git_available(tmp_path)
        assert isinstance(result, bool)

    def test_worktrees_supported_returns_bool(self, tmp_path):
        """``_worktrees_supported`` returns a bool (not raises)."""
        result = _worktrees_supported(tmp_path)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Isolation: pkg import vs canonical submodule import
# ---------------------------------------------------------------------------


class TestImportIsolation:
    """Verify that submodule-level imports work as well as package-level imports."""

    def test_worktree_pool_importable_from_pool_module(self):
        """``from thegent.mesh.git_parallelism.pool import WorktreePool`` works."""
        from thegent.mesh.git_parallelism.pool import WorktreePool as PoolWP

        assert PoolWP is WorktreePool

    def test_worktree_context_importable_from_submodule(self):
        """``from thegent.mesh.git_parallelism.worktree_context import WorktreeContext`` works."""
        from thegent.mesh.git_parallelism.worktree_context import (
            WorktreeContext as WCSub,
        )

        assert WCSub is WorktreeContext

    def test_pool_state_lock_importable_from_submodule(self):
        """``from thegent.mesh.git_parallelism.pool_state import _PoolStateLock`` works."""
        from thegent.mesh.git_parallelism.pool_state import (
            _PoolStateLock as PSLSub,
        )

        assert PSLSub is _PoolStateLock

    def test_helpers_importable_from_helpers_module(self):
        """``from thegent.mesh.git_parallelism.helpers import _run`` works."""
        from thegent.mesh.git_parallelism.helpers import _run as _run_sub

        assert _run_sub is _run


# ---------------------------------------------------------------------------
# Function-level budgets (CLAUDE.md: max function length 40 LOC)
# ---------------------------------------------------------------------------


class TestFunctionLengthRegression:
    """Wire-level pin: every public method on WorktreePool is ≤ 40 LOC."""

    def _body_loc(self, func: object) -> int:
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

    def test_acquire_worktree_under_40_loc(self):
        """``acquire_worktree`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool.acquire_worktree)
        assert loc <= 40, f"acquire_worktree is {loc} LOC, expected ≤ 40"

    def test_release_worktree_under_40_loc(self):
        """``release_worktree`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool.release_worktree)
        assert loc <= 40, f"release_worktree is {loc} LOC, expected ≤ 40"

    def test_worktree_contextmanager_under_40_loc(self):
        """``worktree`` context manager ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool.worktree)
        assert loc <= 40, f"worktree is {loc} LOC, expected ≤ 40"

    def test_active_agents_under_40_loc(self):
        """``active_agents`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool.active_agents)
        assert loc <= 40

    def test_cleanup_stale_under_40_loc(self):
        """``cleanup_stale`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool.cleanup_stale)
        assert loc <= 40, f"cleanup_stale is {loc} LOC, expected ≤ 40"

    def test_create_worktree_under_40_loc(self):
        """``_create_worktree`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool._create_worktree)
        assert loc <= 40, f"_create_worktree is {loc} LOC, expected ≤ 40"

    def test_merge_and_remove_under_40_loc(self):
        """``_merge_and_remove`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreePool._merge_and_remove)
        assert loc <= 40, f"_merge_and_remove is {loc} LOC, expected ≤ 40"

    def test_worktree_context_commit_all_under_40_loc(self):
        """``WorktreeContext.commit_all`` ≤ 40 LOC body."""
        loc = self._body_loc(WorktreeContext.commit_all)
        assert loc <= 40, f"commit_all is {loc} LOC, expected ≤ 40"

    def test_pool_state_lock_read_under_40_loc(self):
        """``_PoolStateLock.read`` ≤ 40 LOC body."""
        loc = self._body_loc(_PoolStateLock.read)
        assert loc <= 40

    def test_pool_state_lock_write_under_40_loc(self):
        """``_PoolStateLock.write`` ≤ 40 LOC body."""
        loc = self._body_loc(_PoolStateLock.write)
        assert loc <= 40


# ---------------------------------------------------------------------------
# Interaction with SmartMerger (cross-class workflow)
# ---------------------------------------------------------------------------


class TestWorktreePoolSmartMergerInteraction:
    """Verify the split preserves the WorktreePool ↔ SmartMerger interop."""

    def test_pool_accepts_merger_initially_none(self, tmp_path):
        """A freshly constructed pool has ``_merger = None`` and acquire still works."""
        project = tmp_path / "p"
        project.mkdir()
        pool = WorktreePool(project, pool_root=tmp_path / ".pool")
        assert pool._merger is None
        # Use fallback mode so we don't need git
        pool._git_ok = False
        pool._worktrees_ok = False
        ctx = pool.acquire_worktree("wl709-agent")
        assert ctx.agent_id == "wl709-agent"

    def test_pool_subclass_inherits_from_package(self, tmp_path):
        """A subclass of ``WorktreePool`` can be defined at the package level."""

        class MyPool(WorktreePool):
            pass

        project = tmp_path / "p"
        project.mkdir()
        pool = MyPool(project, pool_root=tmp_path / ".pool")
        assert isinstance(pool, WorktreePool)
        # The instance's *class* is the test-local MyPool, but it should
        # still be a direct subclass of the canonical WorktreePool whose
        # canonical module is the pool submodule.
        assert pool.__class__.__bases__ == (WorktreePool,)
        assert WorktreePool.__module__ == "thegent.mesh.git_parallelism.pool"
