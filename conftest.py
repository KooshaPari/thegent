"""Pytest configuration for thegent."""

from pathlib import Path

import pytest

# thegent project root (where conftest.py lives)
_THGENT_ROOT = Path(__file__).resolve().parent


@pytest.fixture
def project_root() -> Path:
    """Project root - thegent directory (has .git, pyproject.toml)."""
    return _THGENT_ROOT


@pytest.fixture
def thegent_readme_path(project_root: Path) -> Path:
    """Path to README.md - used for deterministic content assertions."""
    return project_root / "README.md"


@pytest.fixture
def thegent_readme_first_line(thegent_readme_path: Path) -> str:
    """First line of thegent README - deterministic expected content."""
    if not thegent_readme_path.exists():
        pytest.skip(f"README not found: {thegent_readme_path}")
    return thegent_readme_path.read_text().splitlines()[0].strip()


@pytest.fixture
def thegent_pyproject_path(project_root: Path) -> Path:
    """Path to pyproject.toml."""
    return project_root / "pyproject.toml"


@pytest.fixture
def thegent_pyproject_name_line(thegent_pyproject_path: Path) -> str:
    """Line containing name = "thegent" - deterministic expected content."""
    if not thegent_pyproject_path.exists():
        pytest.skip(f"pyproject.toml not found: {thegent_pyproject_path}")
    for line in thegent_pyproject_path.read_text().splitlines():
        if 'name = "thegent"' in line or "name = 'thegent'" in line:
            return line.strip()
    return 'name = "thegent"'  # fallback
