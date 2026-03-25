"""Consistent naming conventions enforcement."""

import re

__all__ = ["NamingConvention"]


class NamingConvention:
    """Naming convention enforcer.

    This class enforces consistent naming conventions across all components:
    - Commands: kebab-case
    - Config keys: snake_case
    - Functions: snake_case
    - Classes: PascalCase
    - Constants: UPPER_SNAKE_CASE

    Examples:
        >>> naming = NamingConvention()
        >>> is_valid = naming.validate("thegent-install", "command")
        >>> suggested = naming.suggest_name("thegent_install", "command")
    """

    def __init__(self) -> None:
        """Initialize naming convention enforcer."""
        self.conventions = {
            "command": r"^[a-z][a-z0-9-]*$",  # kebab-case
            "config_key": r"^[a-z][a-z0-9_]*$",  # snake_case
            "file": r"^[A-Z][A-Z0-9_]*\.md$",  # UPPER_SNAKE_CASE for docs
            "function": r"^[a-z][a-z0-9_]*$",  # snake_case
            "class": r"^[A-Z][A-Za-z0-9]*$",  # PascalCase
            "constant": r"^[A-Z][A-Z0-9_]*$",  # UPPER_SNAKE_CASE
        }

    def validate(self, name: str, convention_type: str) -> bool:
        """Validate name against convention.

        Args:
            name: Name to validate
            convention_type: Type of convention (command, config_key, function, class, constant)

        Returns:
            True if name follows convention, False otherwise
        """
        pattern = self.conventions.get(convention_type)
        if not pattern:
            return True

        return bool(re.match(pattern, name))

    def suggest_name(self, name: str, convention_type: str) -> str:
        """Suggest name following convention.

        Converts name to follow the specified convention.

        Args:
            name: Name to convert
            convention_type: Target convention type

        Returns:
            Suggested name following convention
        """
        pattern = self.conventions.get(convention_type)
        if not pattern:
            return name

        # Convert to convention
        if convention_type == "command":
            # Convert to kebab-case
            return re.sub(r"_", "-", name.lower())
        if convention_type in {"config_key", "function"}:
            # Convert to snake_case
            return re.sub(r"-", "_", name.lower())
        if convention_type == "class":
            # Convert to PascalCase
            parts = re.split(r"[-_]", name)
            return "".join(p.capitalize() for p in parts)
        if convention_type == "constant":
            # Convert to UPPER_SNAKE_CASE
            return re.sub(r"[-]", "_", name.upper())

        return name
