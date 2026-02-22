"""Tests for WL-165: Linear Priority Round-Trip.

# @trace WL-165
"""

from __future__ import annotations

import pytest

from thegent.integrations.linear_priority import (
    LinearPriority,
    LocalPriority,
    linear_to_local,
    local_to_linear,
)


@pytest.mark.requirement("WL-165")
def test_linear_priority_enum_values() -> None:
    """Test LinearPriority enum has correct values."""
    assert LinearPriority.NO_PRIORITY == 0
    assert LinearPriority.URGENT == 1
    assert LinearPriority.HIGH == 2
    assert LinearPriority.MEDIUM == 3
    assert LinearPriority.LOW == 4


@pytest.mark.requirement("WL-165")
def test_local_priority_enum_values() -> None:
    """Test LocalPriority enum has correct values."""
    assert LocalPriority.P0 == 0
    assert LocalPriority.P1 == 1
    assert LocalPriority.P2 == 2
    assert LocalPriority.P3 == 3


@pytest.mark.requirement("WL-165")
def test_linear_to_local_urgent() -> None:
    """Test converting LinearPriority.URGENT to LocalPriority."""
    result = linear_to_local(LinearPriority.URGENT)
    assert result == LocalPriority.P0


@pytest.mark.requirement("WL-165")
def test_linear_to_local_high() -> None:
    """Test converting LinearPriority.HIGH to LocalPriority."""
    result = linear_to_local(LinearPriority.HIGH)
    assert result == LocalPriority.P1


@pytest.mark.requirement("WL-165")
def test_linear_to_local_medium() -> None:
    """Test converting LinearPriority.MEDIUM to LocalPriority."""
    result = linear_to_local(LinearPriority.MEDIUM)
    assert result == LocalPriority.P2


@pytest.mark.requirement("WL-165")
def test_linear_to_local_low() -> None:
    """Test converting LinearPriority.LOW to LocalPriority."""
    result = linear_to_local(LinearPriority.LOW)
    assert result == LocalPriority.P3


@pytest.mark.requirement("WL-165")
def test_linear_to_local_no_priority() -> None:
    """Test converting LinearPriority.NO_PRIORITY to LocalPriority."""
    result = linear_to_local(LinearPriority.NO_PRIORITY)
    assert result == LocalPriority.P3


@pytest.mark.requirement("WL-165")
def test_linear_to_local_with_integer() -> None:
    """Test linear_to_local accepts integer values."""
    result = linear_to_local(1)  # URGENT
    assert result == LocalPriority.P0

    result = linear_to_local(2)  # HIGH
    assert result == LocalPriority.P1


@pytest.mark.requirement("WL-165")
def test_linear_to_local_invalid_value() -> None:
    """Test linear_to_local raises ValueError for invalid input."""
    with pytest.raises(ValueError):
        linear_to_local(99)


@pytest.mark.requirement("WL-165")
def test_local_to_linear_p0() -> None:
    """Test converting LocalPriority.P0 to LinearPriority."""
    result = local_to_linear(LocalPriority.P0)
    assert result == LinearPriority.URGENT


@pytest.mark.requirement("WL-165")
def test_local_to_linear_p1() -> None:
    """Test converting LocalPriority.P1 to LinearPriority."""
    result = local_to_linear(LocalPriority.P1)
    assert result == LinearPriority.HIGH


@pytest.mark.requirement("WL-165")
def test_local_to_linear_p2() -> None:
    """Test converting LocalPriority.P2 to LinearPriority."""
    result = local_to_linear(LocalPriority.P2)
    assert result == LinearPriority.MEDIUM


@pytest.mark.requirement("WL-165")
def test_local_to_linear_p3() -> None:
    """Test converting LocalPriority.P3 to LinearPriority."""
    result = local_to_linear(LocalPriority.P3)
    assert result == LinearPriority.LOW


@pytest.mark.requirement("WL-165")
def test_local_to_linear_with_string() -> None:
    """Test local_to_linear accepts string values."""
    result = local_to_linear("P0")
    assert result == LinearPriority.URGENT

    result = local_to_linear("P3")
    assert result == LinearPriority.LOW


@pytest.mark.requirement("WL-165")
def test_local_to_linear_invalid_string() -> None:
    """Test local_to_linear raises ValueError for invalid string."""
    with pytest.raises(ValueError):
        local_to_linear("P99")


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_p0() -> None:
    """Test round-trip stability: local -> linear -> local for P0."""
    original = LocalPriority.P0
    linear = local_to_linear(original)
    result = linear_to_local(linear)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_p1() -> None:
    """Test round-trip stability: local -> linear -> local for P1."""
    original = LocalPriority.P1
    linear = local_to_linear(original)
    result = linear_to_local(linear)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_p2() -> None:
    """Test round-trip stability: local -> linear -> local for P2."""
    original = LocalPriority.P2
    linear = local_to_linear(original)
    result = linear_to_local(linear)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_p3() -> None:
    """Test round-trip stability: local -> linear -> local for P3."""
    original = LocalPriority.P3
    linear = local_to_linear(original)
    result = linear_to_local(linear)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_urgent() -> None:
    """Test round-trip stability: linear -> local -> linear for URGENT."""
    original = LinearPriority.URGENT
    local = linear_to_local(original)
    result = local_to_linear(local)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_high() -> None:
    """Test round-trip stability: linear -> local -> linear for HIGH."""
    original = LinearPriority.HIGH
    local = linear_to_local(original)
    result = local_to_linear(local)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_medium() -> None:
    """Test round-trip stability: linear -> local -> linear for MEDIUM."""
    original = LinearPriority.MEDIUM
    local = linear_to_local(original)
    result = local_to_linear(local)
    assert result == original


@pytest.mark.requirement("WL-165")
def test_round_trip_stability_low() -> None:
    """Test round-trip stability: linear -> local -> linear for LOW."""
    original = LinearPriority.LOW
    local = linear_to_local(original)
    result = local_to_linear(local)
    assert result == original
