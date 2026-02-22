"""Unit tests for CLI coverage analyzer command normalization."""

from unittest.mock import patch

from scripts import analyze_test_coverage


def test_normalize_command_path_ignores_prompts_and_aliases() -> None:
    known_commands = {
        "clode max",
        "dex max",
        "project setup",
    }

    assert analyze_test_coverage._normalize_command_path(
        ["clode", "max", "hello prompt", "--force", "--dangerously-skip-permissions"],
        known_commands,
    ) == "clode max"
    assert analyze_test_coverage._normalize_command_path(
        ["dex", "max", "prompt text", "--yolo"],
        known_commands,
    ) == "dex max"
    assert analyze_test_coverage._normalize_command_path(
        ["clode", "max", "--force-yolo", "--force", "--dangerously-bypass-approvals-and-sandbox"],
        known_commands,
    ) == "clode max"
    assert analyze_test_coverage._normalize_command_path(
        ["project", "setup", "--help"],
        known_commands,
    ) == "project setup"
    assert analyze_test_coverage._normalize_command_path(
        ["--help"],
        known_commands,
    ) is None


def test_find_e2e_tests_maps_alias_variants_for_same_base_command(tmp_path) -> None:
    fake_test_file = tmp_path / "test_cli_smoke.py"
    fake_test_file.write_text(
        """
from typer.testing import CliRunner

app = None
runner = CliRunner()

def test_clode_max_with_forced_alias():
    runner.invoke(app, ["clode", "max", "say this once", "--force"])

def test_clode_max_with_bypass_alias():
    runner.invoke(app, ["clode", "max", "say this once", "--dangerously-skip-permissions"])

def test_dex_max_with_force_yolo():
    runner.invoke(app, ["dex", "max", "say this once", "--force-yolo"])

def test_dex_max_with_dangerous_bypass_alias():
    runner.invoke(app, ["dex", "max", "say this once", "--dangerously-bypass-approvals-and-sandbox"])
"""
    )

    with patch("scripts.analyze_test_coverage.TESTS_DIR", tmp_path):
        # Use explicit command paths so the normalization can match canonical commands.
        e2e_tests = analyze_test_coverage.find_e2e_tests(
            command_paths={"clode max", "dex max"},
        )

    assert e2e_tests["clode max"] == [
        "test_clode_max_with_forced_alias",
        "test_clode_max_with_bypass_alias",
    ]
    assert e2e_tests["dex max"] == [
        "test_dex_max_with_force_yolo",
        "test_dex_max_with_dangerous_bypass_alias",
    ]
