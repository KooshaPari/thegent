"""Tests for WL-183: Board-ID Collision Guard.

# @trace WL-183
"""

from __future__ import annotations

import pytest

from thegent.integrations.board_id_guard import (
    BoardIdCollisionError,
    BoardIdRegistry,
    validate_no_collisions,
)


@pytest.mark.requirement("WL-183")
def test_board_id_registry_initialization() -> None:
    """Test BoardIdRegistry initialization."""
    registry = BoardIdRegistry()

    # Should start empty
    assert registry.get_all() == {}


@pytest.mark.requirement("WL-183")
def test_board_id_registry_register() -> None:
    """Test registering a board ID."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")

    assert registry.check_collision("board-001")
    assert registry.get_all() == {"board-001": "github"}


@pytest.mark.requirement("WL-183")
def test_board_id_registry_register_multiple() -> None:
    """Test registering multiple board IDs."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")
    registry.register("board-002", "linear")
    registry.register("board-003", "asana")

    all_ids = registry.get_all()
    assert len(all_ids) == 3
    assert all_ids["board-001"] == "github"
    assert all_ids["board-002"] == "linear"
    assert all_ids["board-003"] == "asana"


@pytest.mark.requirement("WL-183")
def test_board_id_registry_register_same_id_same_connector() -> None:
    """Test registering the same board ID with same connector is idempotent."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")
    # Should not raise an error
    registry.register("board-001", "github")

    assert len(registry.get_all()) == 1


@pytest.mark.requirement("WL-183")
def test_board_id_registry_register_collision_different_connector() -> None:
    """Test registering duplicate board ID with different connector raises error."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")

    with pytest.raises(BoardIdCollisionError) as exc_info:
        registry.register("board-001", "linear")

    assert "board-001" in str(exc_info.value)
    assert "github" in str(exc_info.value)
    assert "linear" in str(exc_info.value)


@pytest.mark.requirement("WL-183")
def test_board_id_registry_check_collision_exists() -> None:
    """Test check_collision returns True for existing board ID."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")

    assert registry.check_collision("board-001")


@pytest.mark.requirement("WL-183")
def test_board_id_registry_check_collision_not_exists() -> None:
    """Test check_collision returns False for non-existent board ID."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")

    assert not registry.check_collision("board-002")


@pytest.mark.requirement("WL-183")
def test_board_id_registry_get_all() -> None:
    """Test get_all returns copy of internal registry."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")
    registry.register("board-002", "linear")

    all_ids = registry.get_all()

    assert all_ids == {"board-001": "github", "board-002": "linear"}

    # Modifying the returned dict should not affect registry
    all_ids["board-003"] = "asana"

    assert len(registry.get_all()) == 2


@pytest.mark.requirement("WL-183")
def test_board_id_registry_clear() -> None:
    """Test clearing the registry."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")
    registry.register("board-002", "linear")

    assert len(registry.get_all()) == 2

    registry.clear()

    assert len(registry.get_all()) == 0


@pytest.mark.requirement("WL-183")
def test_validate_no_collisions_success() -> None:
    """Test validate_no_collisions succeeds with no duplicates."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")
    registry.register("board-002", "linear")
    registry.register("board-003", "asana")

    # Should not raise
    validate_no_collisions(registry)


@pytest.mark.requirement("WL-183")
def test_validate_no_collisions_empty_registry() -> None:
    """Test validate_no_collisions succeeds with empty registry."""
    registry = BoardIdRegistry()

    # Should not raise
    validate_no_collisions(registry)


@pytest.mark.requirement("WL-183")
def test_validate_no_collisions_single_entry() -> None:
    """Test validate_no_collisions succeeds with single entry."""
    registry = BoardIdRegistry()

    registry.register("board-001", "github")

    # Should not raise
    validate_no_collisions(registry)


@pytest.mark.requirement("WL-183")
def test_board_id_collision_error_exception() -> None:
    """Test BoardIdCollisionError is properly raised and caught."""
    with pytest.raises(BoardIdCollisionError) as exc_info:
        raise BoardIdCollisionError("Test collision error")

    assert "Test collision error" in str(exc_info.value)


@pytest.mark.requirement("WL-183")
def test_board_id_registry_multiple_operations() -> None:
    """Test combined operations on registry."""
    registry = BoardIdRegistry()

    # Register some IDs
    registry.register("board-001", "github")
    registry.register("board-002", "linear")

    # Check existence
    assert registry.check_collision("board-001")
    assert not registry.check_collision("board-999")

    # Validate no collisions
    validate_no_collisions(registry)

    # Register more
    registry.register("board-003", "asana")

    # Validate again
    validate_no_collisions(registry)

    # Get all
    all_ids = registry.get_all()
    assert len(all_ids) == 3

    # Clear and verify
    registry.clear()
    assert len(registry.get_all()) == 0
