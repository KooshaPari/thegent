#!/usr/bin/env python3
"""Analyze test coverage for agent-only environment.

This script:
1. Maps all CLI commands to test coverage
2. Identifies missing E2E tests
3. Generates test coverage report
4. Creates test templates for missing tests
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "thegent"
TESTS_DIR = PROJECT_ROOT / "tests"
MAIN_PY = SRC_DIR / "main.py"
CLI_PY = SRC_DIR / "cli.py"


def extract_cli_commands_from_main() -> list[dict[str, Any]]:
    """Extract all CLI commands from main.py."""
    commands = []

    with open(MAIN_PY) as f:
        content = f.read()

    # Find all @app.command, @*_app.command decorators
    pattern = r'@(\w+_app|app)\.command\(["\']([^"\']+)["\']'
    matches = re.finditer(pattern, content)

    for match in matches:
        app_name = match.group(1)
        cmd_name = match.group(2)

        # Find the function definition after this decorator
        start_pos = match.end()
        func_match = re.search(r"def\s+(\w+)\(", content[start_pos : start_pos + 500])
        if func_match:
            func_name = func_match.group(1)
            commands.append(
                {
                    "app": app_name,
                    "command": cmd_name,
                    "function": func_name,
                    "full_path": f"thegent {app_name.replace('_app', '')} {cmd_name}"
                    if app_name != "app"
                    else f"thegent {cmd_name}",
                }
            )

    return commands


def extract_cli_functions_from_cli() -> list[str]:
    """Extract all CLI command functions from cli.py."""
    functions = []

    with open(CLI_PY) as f:
        content = f.read()

    # Find all functions ending with _cmd
    pattern = r"^def\s+(\w+_cmd)\("
    matches = re.finditer(pattern, content, re.MULTILINE)

    for match in matches:
        functions.append(match.group(1))

    return functions


def find_e2e_tests() -> dict[str, list[str]]:
    """Find all E2E tests and map them to commands."""
    e2e_tests = defaultdict(list)

    # Check both old and new test locations
    test_files = []
    e2e_dir = TESTS_DIR / "e2e"
    if e2e_dir.exists():
        test_files.extend(e2e_dir.glob("test_*.py"))

    # Also check the old test file if it exists
    old_test_file = TESTS_DIR / "test_e2e_cli.py"
    if old_test_file.exists():
        test_files.append(old_test_file)

    for test_file in test_files:
        with open(test_file) as f:
            content = f.read()

        # Find test methods
        # Look for patterns like: runner.invoke(app, ["cmd", "subcmd", ...])
        pattern = r"runner\.invoke\(app,\s*\[([^\]]+)\]"
        matches = re.finditer(pattern, content)

        for match in matches:
            cmd_args_str = match.group(1)
            # Parse the list of strings
            # This handles both "cmd", "subcmd" and 'cmd', 'subcmd'
            cmd_args = [arg.strip().strip("\"'") for arg in cmd_args_str.split(",")]

            # Remove flags (anything starting with -- or -) to get the base command
            base_cmd_args = [arg for arg in cmd_args if not arg.startswith("-")]

            if not base_cmd_args:
                continue

            # The full command path (excluding thegent)
            full_cmd = " ".join(base_cmd_args)

            # Find the test function name
            test_start = content.rfind("def test_", 0, match.start())
            if test_start != -1:
                test_match = re.search(r"def\s+(test_\w+)", content[test_start : test_start + 200])
                if test_match:
                    test_name = test_match.group(1)
                    e2e_tests[full_cmd].append(test_name)

    return dict(e2e_tests)


def generate_coverage_report() -> dict[str, Any]:
    """Generate comprehensive coverage report."""
    commands = extract_cli_commands_from_main()
    cli_functions = extract_cli_functions_from_cli()
    e2e_tests = find_e2e_tests()

    # Map commands to tests
    coverage_map = {}
    for cmd in commands:
        full_path = cmd["full_path"]
        # The lookup key in e2e_tests is the command path without "thegent"
        lookup_key = full_path.replace("thegent ", "")

        tests = e2e_tests.get(lookup_key, [])
        coverage_map[full_path] = {
            "command": cmd["command"],
            "function": cmd["function"],
            "app": cmd["app"],
            "has_e2e_test": len(tests) > 0,
            "test_count": len(tests),
            "tests": tests,
        }

    # Calculate statistics
    unique_commands = {cmd["full_path"]: cmd for cmd in commands}
    total_commands = len(unique_commands)
    commands_with_tests = sum(1 for c in coverage_map.values() if c["has_e2e_test"])
    coverage_percent = (commands_with_tests / total_commands * 100) if total_commands > 0 else 0

    return {
        "summary": {
            "total_commands": total_commands,
            "commands_with_e2e_tests": commands_with_tests,
            "commands_without_e2e_tests": total_commands - commands_with_tests,
            "coverage_percent": round(coverage_percent, 2),
            "total_cli_functions": len(cli_functions),
        },
        "commands": coverage_map,
        "missing_tests": [full_path for full_path, data in coverage_map.items() if not data["has_e2e_test"]],
    }


def generate_test_template(command_path: str, command_data: dict[str, Any]) -> str:
    """Generate BDD-style test template for a command."""
    cmd_parts = command_path.split()
    test_name = "_".join(cmd_parts[1:]).replace("-", "_")
    class_name = "".join(word.capitalize() for word in cmd_parts[1:])

    template = f'''"""
E2E test for: {command_path}

Agent Journey: Agent executes {command_path} command
Expected Behavior: Command executes successfully and returns expected output
"""
import pytest
from typer.testing import CliRunner

from thegent.main import app

runner = CliRunner()


@pytest.mark.e2e
class Test{class_name}:
    """E2E tests for {command_path} command."""

    def test_{test_name}_exits_zero(self) -> None:
        """{command_path} exits with code 0."""
        result = runner.invoke(app, {cmd_parts[1:]})
        assert result.exit_code == 0, f"Command failed: {{result.stdout}} {{result.stderr}}"

    def test_{test_name}_produces_output(self) -> None:
        """{command_path} produces expected output."""
        result = runner.invoke(app, {cmd_parts[1:]})
        assert result.exit_code == 0
        # TODO: Add specific output assertions based on command behavior
        assert len(result.stdout) > 0 or len(result.stderr) == 0

    def test_{test_name}_help_exits_zero(self) -> None:
        """{command_path} --help exits with code 0."""
        result = runner.invoke(app, {[*cmd_parts[1:], "--help"]})
        assert result.exit_code == 0
'''
    return template


def main():
    """Generate coverage report and test templates."""
    print("🔍 Analyzing test coverage for agent-only environment...")
    print("=" * 80)

    report = generate_coverage_report()

    print("\n📊 Coverage Summary:")
    print(f"  Total CLI Commands: {report['summary']['total_commands']}")
    print(f"  Commands with E2E Tests: {report['summary']['commands_with_e2e_tests']}")
    print(f"  Commands without E2E Tests: {report['summary']['commands_without_e2e_tests']}")
    print(f"  Coverage: {report['summary']['coverage_percent']}%")
    print(f"  Total CLI Functions: {report['summary']['total_cli_functions']}")

    print(f"\n❌ Missing E2E Tests ({len(report['missing_tests'])} commands):")
    for cmd in sorted(report["missing_tests"])[:20]:  # Show first 20
        print(f"  - {cmd}")
    if len(report["missing_tests"]) > 20:
        print(f"  ... and {len(report['missing_tests']) - 20} more")

    # Save report
    report_file = PROJECT_ROOT / "docs" / "governance" / "test_coverage_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Coverage report saved to: {report_file}")

    # Generate test templates for missing tests
    templates_dir = PROJECT_ROOT / "tests" / "e2e" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    print("\n📝 Generating test templates for missing tests...")
    for cmd_path in report["missing_tests"][:10]:  # Generate templates for first 10
        cmd_data = report["commands"][cmd_path]
        template = generate_test_template(cmd_path, cmd_data)
        template_file = templates_dir / f"test_{cmd_path.replace(' ', '_').replace('-', '_')}.py"
        template_file.write_text(template)
        print(f"  ✓ Generated: {template_file.name}")

    print("\n✅ Analysis complete!")
    print("\n🎯 Next Steps:")
    print(f"  1. Review coverage report: {report_file}")
    print("  2. Implement E2E tests for missing commands")
    print("  3. Target: 100% E2E coverage (agent-only requirement)")
    print("  4. Run: pytest tests/test_e2e_cli.py -v")


if __name__ == "__main__":
    main()
