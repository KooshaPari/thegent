"""Tests for GW-48: inject_usage_cost — usage.cost injected into every response.

# @trace FR-REQEXT-048
"""

from __future__ import annotations

import pytest

from thegent.cliproxy_adapter import inject_usage_cost


@pytest.mark.requirement("FR-REQEXT-048")
def test_inject_usage_cost_known_model() -> None:
    """GW-48: inject usage.cost for a known model (gpt-4o) with token counts."""
    body = {
        "model": "gpt-4o",
        "usage": {
            "prompt_tokens": 1000,
            "completion_tokens": 500,
        },
    }
    result = inject_usage_cost(body)
    assert "cost" in result["usage"]
    assert isinstance(result["usage"]["cost"], float)
    assert result["usage"]["cost"] > 0.0


@pytest.mark.requirement("FR-REQEXT-048")
def test_inject_usage_cost_no_usage_returns_unchanged() -> None:
    """GW-48: body with no usage dict is returned unchanged (no cost to compute)."""
    body = {"model": "gpt-4o", "choices": []}
    result = inject_usage_cost(body)
    assert result == body
    assert "usage" not in result


@pytest.mark.requirement("FR-REQEXT-048")
def test_inject_usage_cost_zero_cost_returns_unchanged() -> None:
    """GW-48: unknown model produces 0.0 cost — body returned unchanged."""
    body = {
        "model": "unknown-model-xyz",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
        },
    }
    result = inject_usage_cost(body)
    # cost should not be injected when calculated cost is 0.0
    assert "cost" not in result.get("usage", {})


@pytest.mark.requirement("FR-REQEXT-048")
def test_inject_usage_cost_does_not_mutate() -> None:
    """GW-48: original body dict and nested usage dict must not be mutated."""
    original_usage = {"prompt_tokens": 2000, "completion_tokens": 1000}
    body = {"model": "gpt-4o", "usage": original_usage}
    original_body_id = id(body)
    original_usage_id = id(original_usage)

    result = inject_usage_cost(body)

    # The returned dicts must be new objects
    assert id(result) != original_body_id
    assert id(result["usage"]) != original_usage_id
    # The originals are unchanged
    assert "cost" not in original_usage
    assert body is body  # sanity: body variable unchanged


@pytest.mark.requirement("FR-REQEXT-048")
def test_inject_usage_cost_preserves_existing_usage_fields() -> None:
    """GW-48: existing fields in usage (e.g. total_tokens) are preserved after injection."""
    body = {
        "model": "gpt-4o",
        "usage": {
            "prompt_tokens": 500,
            "completion_tokens": 250,
            "total_tokens": 750,
            "some_custom_field": "preserved",
        },
    }
    result = inject_usage_cost(body)
    usage = result["usage"]
    assert usage["prompt_tokens"] == 500
    assert usage["completion_tokens"] == 250
    assert usage["total_tokens"] == 750
    assert usage["some_custom_field"] == "preserved"
    assert "cost" in usage
    assert isinstance(usage["cost"], float)
    assert usage["cost"] > 0.0
