#!/usr/bin/env python3
"""
Generate interactive CLI examples from Typer commands for VitePress documentation.

Part of VitePress Rich Documentation Implementation Plan - Phase 2.
"""

import ast
import sys
from pathlib import Path
from typing import Any


def extract_typer_commands(cli_file: Path) -> list[dict[str, Any]]:
    """Extract Typer commands from CLI file."""
    commands = []

    try:
        with open(cli_file, encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=str(cli_file))
    except Exception as e:
        print(f"Error: Could not parse {cli_file}: {e}", file=sys.stderr)
        return commands

    # Find all function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if function has typer command decorator
            has_command_decorator = False
            command_name = None
            help_text = None

            for decorator in node.decorator_list:
                # Check for @app.command() or similar patterns
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr == "command":
                            has_command_decorator = True
                            # Extract command name from decorator args
                            if decorator.args:
                                if isinstance(decorator.args[0], ast.Constant):
                                    command_name = decorator.args[0].value
                                elif isinstance(decorator.args[0], ast.Str):
                                    command_name = decorator.args[0].s

            if has_command_decorator or node.name.endswith("_cmd"):
                # Extract docstring as help text
                docstring = ast.get_docstring(node)
                if docstring:
                    help_text = docstring.split("\n")[0]  # First line

                # Extract function name
                if not command_name:
                    command_name = node.name.replace("_cmd", "").replace("_", "-")

                # Extract parameters
                params = []
                for arg in node.args.args:
                    if arg.arg not in ["self", "ctx"]:
                        params.append(
                            {
                                "name": arg.arg,
                                "required": True,  # Simplified - would need to check defaults
                            }
                        )

                commands.append(
                    {
                        "name": command_name,
                        "function": node.name,
                        "help": help_text or "",
                        "params": params,
                        "docstring": docstring or "",
                    }
                )

    return commands


def generate_code_playground_markdown(commands: list[dict[str, Any]]) -> str:
    """Generate Markdown with CodePlayground components for CLI examples."""
    md = "# CLI Examples\n\n"
    md += "Interactive examples of thegent CLI commands.\n\n"
    md += "---\n\n"

    for cmd in sorted(commands, key=lambda x: x["name"]):
        md += f"## `thegent {cmd['name']}`\n\n"

        if cmd.get("help"):
            md += f"{cmd['help']}\n\n"

        if cmd.get("docstring"):
            # Add full docstring in a collapsible section
            md += "<details>\n<summary>Full documentation</summary>\n\n"
            md += f"{cmd['docstring']}\n\n"
            md += "</details>\n\n"

        # Generate example command
        example_cmd = f"thegent {cmd['name']}"

        # Add parameters if any
        if cmd.get("params"):
            param_examples = []
            for param in cmd["params"][:3]:  # Limit to 3 params for readability
                param_name = param["name"].replace("_", "-")
                param_examples.append(f"--{param_name} VALUE")

            if param_examples:
                example_cmd += " " + " ".join(param_examples)
            if len(cmd["params"]) > 3:
                example_cmd += " ..."

        # Escape quotes for Vue component
        escaped_cmd = example_cmd.replace("'", "\\'")

        md += f"<CodePlayground lang='bash' code='{escaped_cmd}' />\n\n"
        md += "---\n\n"

    return md


def generate_simple_examples(commands: list[dict[str, Any]]) -> str:
    """Generate simple markdown examples without CodePlayground."""
    md = "# CLI Command Reference\n\n"

    for cmd in sorted(commands, key=lambda x: x["name"]):
        md += f"## `thegent {cmd['name']}`\n\n"

        if cmd.get("help"):
            md += f"**Description**: {cmd['help']}\n\n"

        # Usage example
        example = f"thegent {cmd['name']}"
        if cmd.get("params"):
            example += " [options]"

        md += f"**Usage**:\n```bash\n{example}\n```\n\n"

        if cmd.get("params"):
            md += "**Options**:\n"
            for param in cmd["params"]:
                param_name = param["name"].replace("_", "-")
                md += f"- `--{param_name}` - Parameter\n"
            md += "\n"

        md += "---\n\n"

    return md


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate CLI examples from Typer commands")
    parser.add_argument(
        "--cli-file",
        type=str,
        default="src/thegent/main.py",
        help="CLI file path (current Typer entrypoint)",
    )
    parser.add_argument("--output", type=str, default="docs/reference/cli-examples.md", help="Output file")
    parser.add_argument("--format", choices=["playground", "simple"], default="playground", help="Output format")

    args = parser.parse_args()

    cli_file = Path(args.cli_file)
    if not cli_file.exists():
        print(f"Error: CLI file not found: {cli_file}", file=sys.stderr)
        sys.exit(1)

    commands = extract_typer_commands(cli_file)
    print(f"Found {len(commands)} commands")

    if args.format == "playground":
        md_content = generate_code_playground_markdown(commands)
    else:
        md_content = generate_simple_examples(commands)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content, encoding="utf-8")

    print(f"✅ Generated: {output_path}")


if __name__ == "__main__":
    main()
