"""
Argument Parsing for CLI Framework.

Provides flexible argument parsing with support for flags, positional
arguments, and subcommands.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Union
import re


@dataclass
class Flag:
    """Represents a command-line flag/option."""

    name: str
    short: Optional[str] = None
    description: str = ""
    default: Any = None
    required: bool = False
    choices: Optional[list[str]] = None
    type: type = str

    def __post_init__(self) -> None:
        """Validate flag configuration."""
        if self.short and len(self.short) != 1:
            raise ValueError(f"Short flag must be a single character: {self.short}")
        if self.choices and self.default not in self.choices and self.default is not None:
            raise ValueError(f"Default value must be one of choices: {self.choices}")


@dataclass
class PositionalArg:
    """Represents a positional command-line argument."""

    name: str
    description: str = ""
    required: bool = True
    default: Any = None
    nargs: Union[int, str] = 1  # Number of args or '*', '+', '?'

    def matches(self, value: str) -> bool:
        """Check if this argument matches the given value."""
        if value.startswith("-"):
            return False
        return True


class ParseError(Exception):
    """Raised when argument parsing fails."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)


class ArgumentParser:
    """
    Flexible argument parser for CLI commands.

    Supports:
    - Long flags (--flag)
    - Short flags (-f)
    - Flag values (--flag value or --flag=value)
    - Positional arguments
    - Required vs optional flags
    - Default values
    """

    def __init__(self, command: "BaseCommand"):  # noqa: F821
        self.command = command
        self.parsed_flags: dict[str, Any] = {}
        self.parsed_positional: list[str] = []
        self.errors: list[str] = []

    def parse(self, args: list[str]) -> bool:
        """Parse command-line arguments.

        Args:
            args: List of argument strings

        Returns:
            True if parsing succeeded, False otherwise
        """
        self.parsed_flags = {}
        self.parsed_positional = []
        self.errors = []

        # Initialize flags with defaults
        flags = self.command._get_flags()
        for name, flag_def in flags.items():
            self.parsed_flags[name] = flag_def["default"]

        # Collect flag definitions
        flags_by_name = {name: flag_def for name, flag_def in flags.items()}
        flags_by_short = {
            flag_def["short"]: name
            for name, flag_def in flags.items()
            if flag_def["short"]
        }

        i = 0
        while i < len(args):
            arg = args[i]

            # Handle long flags (--flag)
            if arg.startswith("--"):
                name = arg[2:]
                if not self._parse_long_flag(name, flags_by_name, args, i):
                    return False
                i += 1
                if self._get_flag_value_after(name, flags_by_name) != (None, -1)[0]:
                    i += 1

            # Handle short flags (-f)
            elif arg.startswith("-"):
                name = arg[1:]
                if len(name) == 1:
                    if not self._parse_short_flag(name, flags_by_short, flags_by_name, args, i):
                        return False
                    i += 1
                    if self._get_flag_value_after(name, flags_by_name) != (None, -1)[0]:
                        i += 1
                else:
                    # Combined short flags: -abc -> -a -b -c
                    for ch in name:
                        if ch not in flags_by_short:
                            self.errors.append(f"Unknown flag: -{ch}")
                            return False
                        self.parsed_flags[flags_by_short[ch]] = True
                    i += 1

            # Handle positional arguments
            else:
                self.parsed_positional.append(arg)
                i += 1

        # Update command state
        command_flags = self.command._get_flags()
        for name, value in self.parsed_flags.items():
            command_flags[name]["value"] = value

        positional = self.command._get_positional()
        self.command._set_positional([
            {**pos, "value": self.parsed_positional[i] if i < len(self.parsed_positional) else None}
            for i, pos in enumerate(positional)
        ])

        # Validate required flags
        for name, flag_def in command_flags.items():
            if flag_def["required"] and flag_def["value"] is None:
                self.errors.append(f"Required flag --{name} is missing")

        # Validate required positional args
        positional = self.command._get_positional()
        for i, pos in enumerate(positional):
            if pos.get("required", True) and i >= len(self.parsed_positional):
                self.errors.append(f"Required positional argument '{pos['name']}' is missing")

        if self.errors:
            return False

        return True

    def _parse_long_flag(
        self, name: str, flags_by_name: dict[str, dict], args: list[str], index: int
    ) -> bool:
        """Parse a long flag (--flag or --flag=value)."""
        # Handle --flag=value syntax
        if "=" in name:
            flag_name, value = name.split("=", 1)
            if flag_name not in flags_by_name:
                self.errors.append(f"Unknown flag: --{flag_name}")
                return False
            self.parsed_flags[flag_name] = self._convert_value(flag_name, value, flags_by_name)
            return True

        # Handle --flag value syntax
        if name not in flags_by_name:
            self.errors.append(f"Unknown flag: --{name}")
            return False

        flag_def = flags_by_name[name]

        # Boolean flags don't need values
        if flag_def["default"] is True or flag_def["default"] is False:
            self.parsed_flags[name] = True
            return True

        # Get value from next arg or use True
        if index + 1 < len(args) and not args[index + 1].startswith("-"):
            value = args[index + 1]
            self.parsed_flags[name] = self._convert_value(name, value, flags_by_name)
        else:
            self.parsed_flags[name] = True

        return True

    def _parse_short_flag(
        self,
        short: str,
        flags_by_short: dict[str, str],
        flags_by_name: dict[str, dict],
        args: list[str],
        index: int,
    ) -> bool:
        """Parse a short flag."""
        if short not in flags_by_short:
            self.errors.append(f"Unknown flag: -{short}")
            return False

        name = flags_by_short[short]
        flag_def = flags_by_name[name]

        # Boolean flags don't need values
        if flag_def["default"] is True or flag_def["default"] is False:
            self.parsed_flags[name] = True
            return True

        # Get value from next arg or use True
        if index + 1 < len(args) and not args[index + 1].startswith("-"):
            value = args[index + 1]
            self.parsed_flags[name] = self._convert_value(name, value, flags_by_name)
        else:
            self.parsed_flags[name] = True

        return True

    def _get_flag_value_after(self, name: str, flags_by_name: dict[str, dict]) -> tuple:
        """Check if there's a value for the flag in the next position."""
        return (None, -1)

    def _convert_value(self, name: str, value: str, flags_by_name: dict[str, dict]) -> Any:
        """Convert a string value to the appropriate type."""
        flag_def = flags_by_name.get(name, {})
        flag_type = flag_def.get("type", str)

        try:
            if flag_type == bool:
                return value.lower() in ("true", "1", "yes", "on")
            elif flag_type == int:
                return int(value)
            elif flag_type == float:
                return float(value)
            else:
                return value
        except ValueError:
            self.errors.append(f"Invalid value for --{name}: {value}")
            return value


class SubcommandParser:
    """Parser for commands with subcommands."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.subcommands: dict[str, type] = {}

    def add_subcommand(self, name: str, command_class: type) -> None:
        """Register a subcommand."""
        self.subcommands[name] = command_class

    def parse(self, args: list[str]) -> tuple[Optional[type], list[str]]:
        """Parse and return the subcommand class.

        Returns:
            Tuple of (command_class, remaining_args)
        """
        if not args:
            return None, []

        subcommand_name = args[0]
        if subcommand_name not in self.subcommands:
            return None, args

        return self.subcommands[subcommand_name], args[1:]
