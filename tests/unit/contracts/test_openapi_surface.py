"""Tests for :mod:`thegent.contracts.openapi_surface`.

L15 audit lane — verifies the vendored OpenAPI spec is loadable, well-formed,
and surfaces a non-trivial inventory. Targeted runs of this file should be
fast (well under 1s) so they can sit in the focused test lane.
"""

from __future__ import annotations

import pytest

from thegent.contracts.openapi_surface import (
    cli_commands,
    endpoint_count,
    load_spec,
    path_count,
    surface_summary,
)


@pytest.fixture(scope="module")
def spec() -> dict:
    """Load the vendored spec once per module."""
    return load_spec()


def test_spec_loads_as_mapping() -> None:
    """Spec must be a top-level mapping."""
    data = load_spec()
    assert isinstance(data, dict)


def test_spec_openapi_version_3_1() -> None:
    """Spec must declare OpenAPI 3.1."""
    data = load_spec()
    assert data.get("openapi") == "3.1.0"


def test_spec_has_info_block() -> None:
    """Spec must include title + version metadata."""
    data = load_spec()
    info = data.get("info") or {}
    assert info.get("title")
    assert info.get("version")


def test_spec_has_at_least_five_paths(spec: dict) -> None:
    """Spec must declare a non-trivial HTTP surface (>= 5 paths)."""
    assert path_count(spec) >= 5, f"only {path_count(spec)} paths declared"


def test_spec_has_at_least_five_operations(spec: dict) -> None:
    """Spec must declare >= 5 HTTP operations total."""
    assert endpoint_count(spec) >= 5


def test_spec_documents_health_endpoint(spec: dict) -> None:
    """The health endpoint is mandatory — it's the liveness probe."""
    paths = spec.get("paths") or {}
    assert "/health" in paths
    health = paths["/health"]
    assert "get" in health


def test_spec_documents_all_cli_entry_points(spec: dict) -> None:
    """All Typer entry points from pyproject must appear under x-cli-command."""
    commands = cli_commands(spec)
    names = {c.get("name") for c in commands}
    # The 8 entry points declared in pyproject.toml:
    expected = {"thegent", "clode", "roid", "droid", "dex", "anen", "fanta", "antigma"}
    assert expected.issubset(names), f"missing CLI commands: {expected - names}"


def test_surface_summary_returns_dataclass() -> None:
    """surface_summary must return a typed SurfaceSummary."""
    summary = surface_summary()
    assert summary.openapi_version == "3.1.0"
    assert summary.title
    assert summary.path_count >= 5
    assert summary.endpoint_count >= 5
    assert summary.cli_command_count >= 8
    d = summary.to_dict()
    assert isinstance(d, dict)
    assert d["path_count"] == summary.path_count


def test_load_spec_rejects_missing_path(tmp_path) -> None:
    """Loading a non-existent path must raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_spec(tmp_path / "missing.yaml")
