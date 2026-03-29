"""Tests for operator command aliases.

# @trace WL-278
"""

from __future__ import annotations

import pytest

from thegent.integrations.operator_aliases import (
    CommandAlias,
    OperatorCommandAliases,
)


@pytest.mark.requirement("WL-278")
class TestCommandAlias:
    """Test CommandAlias dataclass."""

    def test_command_alias_creation(self) -> None:
        """Test creating a CommandAlias."""
        alias = CommandAlias(alias="ll", command="ls -la")
        assert alias.alias == "ll"
        assert alias.command == "ls -la"

    def test_command_alias_fields(self) -> None:
        """Test CommandAlias has expected fields."""
        alias = CommandAlias(alias="ga", command="git add")
        assert hasattr(alias, "alias")
        assert hasattr(alias, "command")


@pytest.mark.requirement("WL-278")
class TestOperatorCommandAliases:
    """Test OperatorCommandAliases registry."""

    def test_register_alias(self) -> None:
        """Test registering a command alias."""
        registry = OperatorCommandAliases()
        alias = registry.register("ll", "ls -la")
        assert alias.alias == "ll"
        assert alias.command == "ls -la"

    def test_resolve_alias(self) -> None:
        """Test resolving an alias to its command."""
        registry = OperatorCommandAliases()
        registry.register("ll", "ls -la")
        command = registry.resolve("ll")
        assert command == "ls -la"

    def test_resolve_alias_not_found(self) -> None:
        """Test resolving non-existent alias raises KeyError."""
        registry = OperatorCommandAliases()
        with pytest.raises(KeyError):
            registry.resolve("ll")

    def test_all_aliases(self) -> None:
        """Test retrieving all aliases."""
        registry = OperatorCommandAliases()
        a1 = registry.register("ll", "ls -la")
        a2 = registry.register("ga", "git add")
        aliases = registry.all_aliases()
        assert len(aliases) == 2
        assert a1 in aliases
        assert a2 in aliases

    def test_all_aliases_empty(self) -> None:
        """Test all_aliases() returns empty list for new registry."""
        registry = OperatorCommandAliases()
        aliases = registry.all_aliases()
        assert aliases == []

    def test_unregister_alias(self) -> None:
        """Test unregistering an alias."""
        registry = OperatorCommandAliases()
        registry.register("ll", "ls -la")
        registry.unregister("ll")
        with pytest.raises(KeyError):
            registry.resolve("ll")

    def test_unregister_not_found(self) -> None:
        """Test unregistering non-existent alias raises KeyError."""
        registry = OperatorCommandAliases()
        with pytest.raises(KeyError):
            registry.unregister("ll")

    def test_register_multiple_aliases(self) -> None:
        """Test registering multiple aliases."""
        registry = OperatorCommandAliases()
        registry.register("ll", "ls -la")
        registry.register("ga", "git add")
        registry.register("gc", "git commit")
        aliases = registry.all_aliases()
        assert len(aliases) == 3

    def test_register_overwrites(self) -> None:
        """Test that registering same alias overwrites previous."""
        registry = OperatorCommandAliases()
        registry.register("ll", "ls -l")
        registry.register("ll", "ls -la")
        command = registry.resolve("ll")
        assert command == "ls -la"

    def test_resolve_error_message(self) -> None:
        """Test that KeyError has informative message."""
        registry = OperatorCommandAliases()
        with pytest.raises(KeyError, match="not found"):
            registry.resolve("nonexistent")

    def test_unregister_error_message(self) -> None:
        """Test that unregister KeyError has informative message."""
        registry = OperatorCommandAliases()
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")
