"""Consistency checks for e2e marker placement in split suites."""

from __future__ import annotations

import ast
from pathlib import Path

SPLIT_FILES = [
    Path(__file__).resolve().parents[1] / "test_e2e_cli_core_a.py",
    Path(__file__).resolve().parents[1] / "test_e2e_cli_core_b.py",
    Path(__file__).resolve().parents[1] / "test_e2e_cli_aliases.py",
    Path(__file__).resolve().parents[1] / "test_e2e_cli_overlays.py",
]


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _has_e2e_marker(decorators: list[ast.expr]) -> bool:
    for decorator in decorators:
        marker = decorator.func if isinstance(decorator, ast.Call) else decorator
        if (
            isinstance(marker, ast.Attribute)
            and marker.attr == "e2e"
            and isinstance(marker.value, ast.Attribute)
            and marker.value.attr == "mark"
            and isinstance(marker.value.value, ast.Name)
            and marker.value.value.id == "pytest"
        ):
            return True
    return False


def test_each_split_file_has_marker_on_class_or_function() -> None:
    for path in SPLIT_FILES:
        module = _parse(path)
        marked_items = [
            node
            for node in ast.walk(module)
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and _has_e2e_marker(node.decorator_list)
        ]
        assert marked_items, f"{path} missing explicit @pytest.mark.e2e placement"
