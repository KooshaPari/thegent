"""AST-aware smart merge driver for concurrent agent edits (heliosShield Phase 7).

Integrates Mergiraf as a git merge driver for .py, .rs, .ts, .js files.
Falls back to diff3 / git merge-file when Mergiraf is unavailable.

The :class:`SmartMerger` class-based API for integration with WorktreePool
(heliosShield-smart-merge, FR-MESH-007) was extracted into
:mod:`thegent.mesh.smart_merger` as part of the WL708 L1 architecture split.
It is re-exported here for back-compat so ``from thegent.mesh.smart_merge
import SmartMerger`` continues to work.
"""

from __future__ import annotations

import contextlib
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from thegent.infra.shim_subprocess import run as shim_run

# File extensions that Mergiraf understands structurally.
MERGIRAF_EXTENSIONS: frozenset[str] = frozenset(
    {".py", ".rs", ".ts", ".js", ".tsx", ".jsx", ".java", ".go", ".c", ".cpp", ".h"}
)

# ---------------------------------------------------------------------------
# Data types for the SmartMerger API
# ---------------------------------------------------------------------------


@dataclass
class SmartMergeConfig:
    """Configuration for SmartMerger.

    Attributes:
        mergiraf_binary: Path to the mergiraf binary.  When *None*, the value
            of the ``THGENT_MERGIRAF_BINARY`` environment variable is used, or
            ``mergiraf`` is searched on ``PATH``.
        fallback_to_git: When True (default), fall back to ``git merge-file``
            if mergiraf is unavailable or returns a hard error.
        timeout_s: Maximum wall-clock seconds to wait for the merge subprocess.
    """

    mergiraf_binary: str | None = None
    fallback_to_git: bool = True
    timeout_s: int = 30


@dataclass
class MergeResult:
    """Result of a smart merge operation.

    Attributes:
        success: True when the merge produced no unresolved conflicts.
        conflicts: List of conflicting file paths (empty on a clean merge).
        output: Captured stdout/stderr from the merge tool.
        used_mergiraf: True when the merge was performed by mergiraf (as
            opposed to the git merge-file fallback).
    """

    success: bool
    conflicts: list[str] = field(default_factory=list)
    output: str = ""
    used_mergiraf: bool = False


def is_mergiraf_available() -> bool:
    """Return True if the mergiraf binary is discoverable on PATH."""
    return shutil.which("mergiraf") is not None


def configure_mergiraf_driver(
    repo_root: Path | None = None,
    *,
    global_config: bool = False,
) -> bool:
    """Register mergiraf as a git merge driver.

    Writes the ``[merge "mergiraf"]`` stanza to ``.git/config`` (local) or
    ``~/.gitconfig`` (global) and creates / updates ``.gitattributes`` at
    *repo_root* with entries for the supported extensions.

    Args:
        repo_root: Repository working directory.  When *None*, the current
            working directory is used.  Ignored when *global_config* is True.
        global_config: Write to the user-global ``~/.gitconfig`` instead of
            the repo-local ``.git/config``.

    Returns:
        True on success, False if git or mergiraf are not available.
    """
    mergiraf_bin = shutil.which("mergiraf")
    if not mergiraf_bin:
        return False

    # ------------------------------------------------------------------ #
    # 1.  Register the merge driver in git config                          #
    # ------------------------------------------------------------------ #
    # The driver receives: %O = base, %A = ours (overwritten in place),
    #                      %B = theirs, %P = path in repo.
    driver_cmd = f"{mergiraf_bin} merge --git %O %A %B -p %P"

    git_config_args_name = [
        "git",
        "config",
        *(["--global"] if global_config else []),
        "merge.mergiraf.name",
        "mergiraf",
    ]
    git_config_args_driver = [
        "git",
        "config",
        *(["--global"] if global_config else []),
        "merge.mergiraf.driver",
        driver_cmd,
    ]

    cwd = None if global_config else (repo_root or Path.cwd())

    try:
        shim_run(git_config_args_name, check=True, capture_output=True, cwd=cwd)
        shim_run(git_config_args_driver, check=True, capture_output=True, cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    # ------------------------------------------------------------------ #
    # 2.  Write .gitattributes entries (repo-local only)                  #
    # ------------------------------------------------------------------ #
    if global_config:
        return True

    root = repo_root or Path.cwd()
    gitattributes = root / ".gitattributes"

    # Collect existing lines so we do not duplicate entries.
    existing_lines: list[str] = []
    if gitattributes.exists():
        existing_lines = gitattributes.read_text(encoding="utf-8").splitlines()

    entries = {
        "*.py": "merge=mergiraf",
        "*.rs": "merge=mergiraf",
        "*.ts": "merge=mergiraf",
        "*.tsx": "merge=mergiraf",
        "*.js": "merge=mergiraf",
        "*.jsx": "merge=mergiraf",
        "*.java": "merge=mergiraf",
        "*.go": "merge=mergiraf",
    }

    added: list[str] = []
    for pattern, attr in entries.items():
        line = f"{pattern} {attr}"
        if not any(line in existing for existing in existing_lines):
            added.append(line)

    if added:
        with gitattributes.open("a", encoding="utf-8") as fh:
            if existing_lines and existing_lines[-1] != "":
                fh.write("\n")
            fh.write("# mergiraf AST-aware merge driver\n")
            for entry in added:
                fh.write(entry + "\n")

    return True


def merge_files(
    base: Path,
    ours: Path,
    theirs: Path,
    output: Path,
    *,
    path_hint: str | None = None,
) -> bool:
    """Perform an AST-aware three-way merge, writing the result to *output*.

    Tries Mergiraf first.  If Mergiraf is not installed or returns a non-zero
    exit code for a reason other than unresolved conflicts, falls back to
    ``git merge-file`` (diff3 strategy) writing to *output*.

    Args:
        base:      Common ancestor file.
        ours:      Our version of the file.
        theirs:    Their version of the file.
        output:    Destination for the merged result.
        path_hint: Logical file path (used by Mergiraf for language detection
                   when the temp-file names lose the original extension).

    Returns:
        True  – merge produced a clean result (no unresolved conflicts).
        False – merge completed with conflicts left in the file, or the merge
                tool itself failed unexpectedly.  The *output* file may still
                be written with conflict markers for manual resolution.
    """
    mergiraf_bin = shutil.which("mergiraf")

    if mergiraf_bin:
        return _merge_with_mergiraf(mergiraf_bin, base, ours, theirs, output, path_hint=path_hint)

    return _merge_with_git_merge_file(base, ours, theirs, output)


# --------------------------------------------------------------------------- #
# Private helpers                                                               #
# --------------------------------------------------------------------------- #


def _merge_with_mergiraf(
    mergiraf_bin: str,
    base: Path,
    ours: Path,
    theirs: Path,
    output: Path,
    *,
    path_hint: str | None,
) -> bool:
    """Run ``mergiraf merge`` and capture result to *output*.

    Mergiraf exit codes:
        0  – clean merge
        1  – conflicts present (output still written with markers)
        2+ – hard error
    """
    cmd: list[str] = [mergiraf_bin, "merge", str(base), str(ours), str(theirs)]

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
        )

        # Exit 0 = clean, 1 = conflicts written with markers (still usable).
        if result.returncode in (0, 1):
            # If mergiraf wrote to stdout instead of --output, capture it.
            if not output.exists() and result.stdout:
                output.write_text(result.stdout, encoding="utf-8")
            return result.returncode == 0

        # Hard failure (exit >=2): fall through to diff3 fallback.
    except FileNotFoundError:
        pass

    return _merge_with_git_merge_file(base, ours, theirs, output)


def _merge_with_git_merge_file(
    base: Path,
    ours: Path,
    theirs: Path,
    output: Path,
) -> bool:
    """Fall back to ``git merge-file --diff3`` for a text-level three-way merge.

    ``git merge-file`` overwrites *ours* in place, so we work on a temp copy
    then move it to *output*.
    """
    import tempfile

    # Work on a scratch copy of ours so the original is preserved.
    with tempfile.NamedTemporaryFile(suffix=ours.suffix, delete=False, dir=output.parent) as tmp:
        tmp_path = Path(tmp.name)

    try:
        tmp_path.write_bytes(ours.read_bytes())

        output_dir = output.parent
        if base.parent == output_dir:
            base_arg = base.name
        else:
            base_arg = str(base)
        if theirs.parent == output_dir:
            theirs_arg = theirs.name
        else:
            theirs_arg = str(theirs)

        result = shim_run(
            [
                "git",
                "merge-file",
                "--diff3",
                tmp_path.name,
                base_arg,
                theirs_arg,
            ],
            cwd=str(output_dir),
            capture_output=True,
            text=True,
            check=False,
        )

        # git merge-file: 0 = clean, >0 = conflicts or error.
        # Either way, copy whatever was written to output.
        output.write_bytes(tmp_path.read_bytes())
        return result.returncode == 0

    except (FileNotFoundError, OSError):
        # git not available - last resort: just copy ours.
        with contextlib.suppress(OSError):
            output.write_bytes(ours.read_bytes())
        return False
    finally:
        with contextlib.suppress(OSError):
            tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Back-compat re-exports (WL708 L1 split: SmartMerger class now lives in
# thegent.mesh.smart_merger.  These re-exports preserve the public surface
# so ``from thegent.mesh.smart_merge import SmartMerger`` still works.)
# ---------------------------------------------------------------------------

from .smart_merger import SmartMerger, make_smart_merger  # noqa: E402,F401


# Note: ``make_smart_merger`` is now defined in ``thegent.mesh.smart_merger``
# alongside the :class:`SmartMerger` class.  It is re-exported above so
# ``from thegent.mesh.smart_merge import make_smart_merger`` continues to work.
