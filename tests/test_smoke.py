"""Package-level smoke tests for thegent.

Fast-lane sentinel: confirms the package imports cleanly and exposes its
public entry points.  These run in the unit fast-lane (no I/O, no external
services) and are the first gate for any CI run.

Traces to: FR-INFRA-001 (package import health), FR-INFRA-002 (CLI entry points)
"""

import importlib
import sys

import pytest


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.requirement("FR-INFRA-001")
def test_thegent_package_importable() -> None:
    """The thegent package must be importable without side effects."""
    spec = importlib.util.find_spec("thegent")
    assert spec is not None, "thegent package not found on sys.path"


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.requirement("FR-INFRA-001")
def test_thegent_top_level_init() -> None:
    """Importing thegent.__init__ must not raise."""
    import thegent  # noqa: F401

    assert "thegent" in sys.modules


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.requirement("FR-INFRA-002")
def test_thegent_exit_codes_importable() -> None:
    """exit_codes module must expose EXIT_TIMEOUT at minimum."""
    from thegent import exit_codes

    assert hasattr(exit_codes, "EXIT_TIMEOUT"), "exit_codes.EXIT_TIMEOUT missing"


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.requirement("FR-INFRA-002")
def test_thegent_constants_importable() -> None:
    """constants module must be importable."""
    from thegent import constants  # noqa: F401

    assert "thegent.constants" in sys.modules


@pytest.mark.unit
@pytest.mark.fast
@pytest.mark.requirement("FR-INFRA-001")
def test_python_version_meets_minimum() -> None:
    """Runtime Python version must be >= 3.10 (project minimum)."""
    assert sys.version_info >= (3, 10), (
        f"Python {sys.version_info.major}.{sys.version_info.minor} is below the"
        " required minimum of 3.10"
    )
