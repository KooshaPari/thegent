"""Hook installation functions for thegent.

Extracted from install.py for maintainability.
"""

from __future__ import annotations

import stat
import sys
from pathlib import Path


def _get_thegent_root() -> Path:
    """Get the thegent root directory."""
    # Walk up from this file to find the project root
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parent.parent.parent


def setup_hooks(
    cwd: Path | None = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, int]:
    """Install thegent hooks into .git/hooks.

    Args:
        cwd: Working directory (defaults to cwd)
        dry_run: If True, don't make changes
        verbose: If True, print details

    Returns:
        Dict with counts: installed, skipped, errors
    """
    root = _get_thegent_root()
    hooks_src = root / "hooks"
    cwd = cwd or Path.cwd()
    git_hooks = cwd / ".git" / "hooks"
    counts: dict[str, int] = {"installed": 0, "skipped": 0, "errors": 0}

    if not git_hooks.parent.exists():
        if verbose:
            sys.stdout.write("  Not a git repo; skipping hooks.\n")
        counts["skipped"] += 1
        return counts

    if not hooks_src.exists():
        if verbose:
            sys.stdout.write(f"  Hooks source not found at {hooks_src}\n")
        counts["errors"] += 1
        return counts

    # Map git hook names to thegent hook scripts
    hook_map = {
        "pre-commit": "pre-commit-quality.sh",
        "pre-push": "pre-push-quality.sh",
    }

    for hook_name, default_script in hook_map.items():
        _setup_git_hook(git_hooks, hooks_src, hook_name, default_script, dry_run, counts, verbose)

    return counts


def _setup_git_hook(
    git_hooks: Path,
    hooks_src: Path,
    hook_name: str,
    default_script: str,
    dry_run: bool,
    counts: dict[str, int],
    verbose: bool,
) -> None:
    """Setup a single git hook safely.

    Args:
        git_hooks: Path to .git/hooks directory
        hooks_src: Path to thegent hooks source
        hook_name: Name of the git hook (e.g., 'pre-commit')
        default_script: Default script name to use
        dry_run: If True, don't make changes
        counts: Dict to update with counts
        verbose: If True, print details
    """
    dst = git_hooks / hook_name
    hook_script = hooks_src / default_script

    if not hook_script.exists():
        # Try fallback scripts
        fallback_map = {
            "pre-commit": ("pre-commit-docs.sh", "quality-gate.sh"),
            "pre-push": ("quality-gate.sh",),
        }
        candidates = fallback_map.get(hook_name, ("quality-gate.sh",))

        for candidate in candidates:
            candidate_path = hooks_src / candidate
            if candidate_path.exists():
                hook_script = candidate_path
                break
        else:
            if verbose:
                sys.stdout.write(f"  No hook script found for {hook_name}\n")
            counts["errors"] += 1
            return

    if dst.exists():
        if verbose:
            sys.stdout.write(f"  Hook {hook_name} already exists, skipping\n")
        counts["skipped"] += 1
        return

    if dry_run:
        if verbose:
            sys.stdout.write(f"  Would install {hook_name} from {hook_script}\n")
        counts["installed"] += 1
        return

    try:
        # Read source and write to destination
        content = hook_script.read_text()
        dst.write_text(content)

        # Make executable
        current_mode = dst.stat().st_mode
        dst.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        if verbose:
            sys.stdout.write(f"  Installed {hook_name}\n")
        counts["installed"] += 1
    except Exception as e:
        if verbose:
            sys.stdout.write(f"  Failed to install {hook_name}: {e}\n")
        counts["errors"] += 1


def setup_rust_dispatcher(verbose: bool = False) -> bool:
    """Setup the Rust dispatcher binary.

    Args:
        verbose: If True, print details

    Returns:
        True if setup succeeded
    """
    root = _get_thegent_root()
    rust_dir = root / "crates" / "thegent-hooks"

    if not rust_dir.exists():
        if verbose:
            sys.stdout.write("  Rust dispatcher crate not found\n")
        return False

    # Check if cargo is available
    import shutil

    cargo = shutil.which("cargo")
    if not cargo:
        if verbose:
            sys.stdout.write("  Cargo not found, skipping Rust dispatcher\n")
        return False

    # Build the dispatcher
    import subprocess

    try:
        result = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=rust_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            if verbose:
                sys.stdout.write(f"  Cargo build failed: {result.stderr}\n")
            return False

        if verbose:
            sys.stdout.write("  Rust dispatcher built successfully\n")
        return True
    except Exception as e:
        if verbose:
            sys.stdout.write(f"  Failed to build Rust dispatcher: {e}\n")
        return False


def setup_harness(verbose: bool = False) -> bool:
    """Setup the test harness.

    Args:
        verbose: If True, print details

    Returns:
        True if setup succeeded
    """
    root = _get_thegent_root()
    harness_dir = root / "tests" / "harness"

    if not harness_dir.exists():
        if verbose:
            sys.stdout.write("  Harness directory not found\n")
        return True  # Not an error, just not present

    # Setup any harness dependencies
    if verbose:
        sys.stdout.write("  Harness setup complete\n")
    return True


def setup_skills(
    skills_dir: Path | None = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, int]:
    """Setup skills from factory directory.

    Args:
        skills_dir: Target directory for skills
        dry_run: If True, don't make changes
        verbose: If True, print details

    Returns:
        Dict with counts: installed, skipped, errors
    """
    root = _get_thegent_root()
    factory_skills = root / "factory-seed" / "skills"

    if not factory_skills.exists():
        if verbose:
            sys.stdout.write("  Factory skills directory not found\n")
        return {"installed": 0, "skipped": 0, "errors": 1}

    counts: dict[str, int] = {"installed": 0, "skipped": 0, "errors": 0}

    # Sync skills to target directory
    if skills_dir is None:
        skills_dir = root / "skills"

    _sync_base_dir_skills(factory_skills, skills_dir, dry_run, counts, verbose)

    return counts


def _sync_base_dir_skills(
    src: Path,
    dst: Path,
    dry_run: bool,
    counts: dict[str, int],
    verbose: bool,
) -> None:
    """Sync skills from source to destination.

    Args:
        src: Source directory
        dst: Destination directory
        dry_run: If True, don't make changes
        counts: Dict to update with counts
        verbose: If True, print details
    """
    import shutil

    if not src.exists():
        return

    if dry_run:
        if verbose:
            sys.stdout.write(f"  Would sync skills from {src} to {dst}\n")
        counts["installed"] += 1
        return

    try:
        if dst.exists():
            shutil.rmtree(dst)

        shutil.copytree(src, dst)

        if verbose:
            sys.stdout.write(f"  Synced skills to {dst}\n")
        counts["installed"] += 1
    except Exception as e:
        if verbose:
            sys.stdout.write(f"  Failed to sync skills: {e}\n")
        counts["errors"] += 1


def _sync_cursor_rules(
    src: Path,
    dst: Path,
    dry_run: bool,
    counts: dict[str, int],
    verbose: bool,
) -> None:
    """Sync cursor rules from source to destination.

    Args:
        src: Source file
        dst: Destination file
        dry_run: If True, don't make changes
        counts: Dict to update with counts
        verbose: If True, print details
    """
    if not src.exists():
        return

    if dry_run:
        if verbose:
            sys.stdout.write(f"  Would sync cursor rules from {src} to {dst}\n")
        counts["installed"] += 1
        return

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text())

        if verbose:
            sys.stdout.write(f"  Synced cursor rules to {dst}\n")
        counts["installed"] += 1
    except Exception as e:
        if verbose:
            sys.stdout.write(f"  Failed to sync cursor rules: {e}\n")
        counts["errors"] += 1


__all__ = [
    "setup_hooks",
    "setup_rust_dispatcher",
    "setup_harness",
    "setup_skills",
    "_get_thegent_root",
    "_sync_cursor_rules",
]
