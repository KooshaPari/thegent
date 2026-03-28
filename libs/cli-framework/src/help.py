"""
Help Generation for CLI Framework.

Provides consistent, formatted help text for commands.
"""

from typing import TYPE_CHECKING, Optional
import sys

from .command import BaseCommand
from .parser import Flag, PositionalArg

if TYPE_CHECKING:
    from .registry import CommandRegistration


class HelpColors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class HelpGenerator:
    """
    Generates formatted help text for CLI commands.

    Supports both plain text and colored terminal output.
    """

    # Default column widths
    LEFT_COL_WIDTH = 24
    INDENT = 2

    @classmethod
    def print_command_help(
        cls, command: BaseCommand, stream: Optional[object] = None
    ) -> None:
        """Print help for a command.

        Args:
            command: The command instance to show help for
            stream: Output stream (defaults to stdout)
        """
        output = stream or sys.stdout
        metadata = command.metadata

        # Command header
        print(f"{HelpColors.BOLD}NAME{HelpColors.RESET}", file=output)
        print(f"    {metadata.name} - {metadata.description}", file=output)
        print(file=output)

        # Usage
        print(f"{HelpColors.BOLD}USAGE{HelpColors.RESET}", file=output)
        usage = cls._build_usage(command)
        print(f"    {usage}", file=output)
        print(file=output)

        # Description
        if metadata.description:
            print(f"{HelpColors.BOLD}DESCRIPTION{HelpColors.RESET}", file=output)
            print(f"    {metadata.description}", file=output)
            print(file=output)

        # Options
        flags = [
            (name, flag_def)
            for name, flag_def in command._flags.items()
        ]
        if flags:
            print(f"{HelpColors.BOLD}OPTIONS{HelpColors.RESET}", file=output)
            for name, flag_def in flags:
                help_line = cls._format_option_help(name, flag_def)
                print(f"    {help_line}", file=output)
            print(file=output)

        # Positional arguments
        positional = command._positional
        if positional:
            print(f"{HelpColors.BOLD}ARGUMENTS{HelpColors.RESET}", file=output)
            for i, pos in enumerate(positional):
                help_line = cls._format_positional_help(i, pos)
                print(f"    {help_line}", file=output)
            print(file=output)

        # Examples
        if metadata.examples:
            print(f"{HelpColors.BOLD}EXAMPLES{HelpColors.RESET}", file=output)
            for example in metadata.examples:
                print(f"    {example}", file=output)
            print(file=output)

    @classmethod
    def _build_usage(cls, command: BaseCommand) -> str:
        """Build the usage line for a command."""
        parts = [command.metadata.name]

        # Add flags
        for name, flag_def in command._flags.items():
            if flag_def["required"]:
                if flag_def["default"] is True or flag_def["default"] is False:
                    parts.append(f"--{name}")
                else:
                    parts.append(f"--{name} <value>")
            else:
                parts.append(f"[--{name} <value>]")

        # Add positional arguments
        for pos in command._positional:
            if pos.get("required", True):
                parts.append(f"<{pos['name']}>")
            else:
                parts.append(f"[<{pos['name']}>]")

        return " ".join(parts)

    @classmethod
    def _format_option_help(cls, name: str, flag_def: dict) -> str:
        """Format a single option for help output."""
        # Build the flag syntax
        if flag_def["short"]:
            syntax = f"-{flag_def['short']}, --{name}"
        else:
            syntax = f"--{name}"

        # Add value placeholder for non-boolean flags
        default = flag_def["default"]
        if default is not None and not isinstance(default, bool):
            syntax += f" <{type(default).__name__}>"

        # Add default value
        if default is not None:
            if isinstance(default, bool):
                default_str = "true" if default else "false"
            elif isinstance(default, str):
                default_str = f'"{default}"'
            else:
                default_str = str(default)
            syntax += f" {HelpColors.DIM}[default: {default_str}]{HelpColors.RESET}"

        # Pad to alignment column
        padding = max(0, cls.LEFT_COL_WIDTH - len(syntax))
        syntax += " " * padding

        # Add description
        description = flag_def["description"]
        if flag_def["required"]:
            description = f"{HelpColors.RED}(required){HelpColors.RESET} {description}"

        return f"{HelpColors.CYAN}{syntax}{HelpColors.RESET} {description}"

    @classmethod
    def _format_positional_help(cls, index: int, pos: dict) -> str:
        """Format a positional argument for help output."""
        name = pos["name"]
        syntax = f"<{name}>"

        # Add count indicator for nargs
        nargs = pos.get("nargs", 1)
        if nargs != 1:
            syntax += f" (x{nargs})"

        # Pad to alignment column
        padding = max(0, cls.LEFT_COL_WIDTH - len(syntax))
        syntax += " " * padding

        # Add description
        required = pos.get("required", True)
        if not required:
            description = f"{HelpColors.DIM}(optional){HelpColors.RESET} {pos['description']}"
        else:
            description = pos["description"]

        return f"{HelpColors.CYAN}{syntax}{HelpColors.RESET} {description}"

    @classmethod
    def print_registry_help(cls, registry: "CommandRegistry") -> None:  # noqa: F821
        """Print help for a command registry.

        Args:
            registry: The command registry
        """
        print(f"{HelpColors.BOLD}Available commands:{HelpColors.RESET}")
        print()

        for group_name in registry.list_groups():
            print(f"{HelpColors.BOLD}{group_name}:{HelpColors.RESET}")
            commands = registry.commands_in_group(group_name)
            for reg in commands:
                print(f"  {HelpColors.GREEN}{reg.name}{HelpColors.RESET} - {reg.description}")
            print()

        # Commands without a group
        ungrouped = [
            reg
            for reg in registry.get_all_commands()
            if reg.group is None
        ]
        if ungrouped:
            print(f"{HelpColors.BOLD}Other commands:{HelpColors.RESET}")
            for reg in ungrouped:
                print(f"  {HelpColors.GREEN}{reg.name}{HelpColors.RESET} - {reg.description}")


class MinimalHelpFormatter:
    """Simple help formatter without colors for scripting."""

    @classmethod
    def format_command_help(cls, command: BaseCommand) -> str:
        """Format command help as plain text."""
        lines = []
        metadata = command.metadata

        lines.append(f"{metadata.name}: {metadata.description}")
        lines.append("")
        lines.append("Usage:")
        lines.append(f"  {cls._build_usage(command)}")
        lines.append("")

        flags = [(name, flag_def) for name, flag_def in command._flags.items()]
        if flags:
            lines.append("Options:")
            for name, flag_def in flags:
                if flag_def["short"]:
                    opt_str = f"  -{flag_def['short']}, --{name}"
                else:
                    opt_str = f"  --{name}"
                lines.append(f"{opt_str:<20} {flag_def['description']}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def _build_usage(cls, command: BaseCommand) -> str:
        """Build usage string."""
        parts = [command.metadata.name]
        for name, flag_def in command._flags.items():
            parts.append(f"[--{name}]")
        return " ".join(parts)
