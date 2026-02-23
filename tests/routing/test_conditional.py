"""Tests for GW-56: Conditional routing.

# @trace FR-AROUTE-056
"""

from __future__ import annotations

import pytest

from thegent.utils.routing_impl.conditional import (
    ConditionalRoute,
    build_routing_context,
    evaluate_condition,
    match_conditional_route,
)


@pytest.mark.requirement("FR-AROUTE-056")
class TestEvaluateCondition:
    def test_evaluate_eq_match(self) -> None:
        condition = {"params.model": {"$eq": "gpt-4o"}}
        ctx = {"params.model": "gpt-4o"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_eq_no_match(self) -> None:
        condition = {"params.model": {"$eq": "gpt-4o"}}
        ctx = {"params.model": "claude-3"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_ne(self) -> None:
        condition = {"params.model": {"$ne": "gpt-4o"}}
        ctx = {"params.model": "claude-3"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_ne_matches_same(self) -> None:
        condition = {"params.model": {"$ne": "gpt-4o"}}
        ctx = {"params.model": "gpt-4o"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_in(self) -> None:
        condition = {"params.model": {"$in": ["gpt-4o", "gpt-4o-mini"]}}
        ctx = {"params.model": "gpt-4o-mini"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_in_no_match(self) -> None:
        condition = {"params.model": {"$in": ["gpt-4o", "gpt-4o-mini"]}}
        ctx = {"params.model": "claude-3"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_nin(self) -> None:
        condition = {"params.model": {"$nin": ["gpt-4o", "gpt-4o-mini"]}}
        ctx = {"params.model": "claude-3"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_nin_matches_excluded(self) -> None:
        condition = {"params.model": {"$nin": ["gpt-4o", "gpt-4o-mini"]}}
        ctx = {"params.model": "gpt-4o"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_regex(self) -> None:
        condition = {"metadata.user_id": {"$regex": "^user-"}}
        ctx = {"metadata.user_id": "user-123"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_regex_no_match(self) -> None:
        condition = {"metadata.user_id": {"$regex": "^admin-"}}
        ctx = {"metadata.user_id": "user-123"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_regex_case_insensitive(self) -> None:
        condition = {"params.model": {"$regex": "GPT"}}
        ctx = {"params.model": "gpt-4o"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_exists_true(self) -> None:
        condition = {"metadata.tier": {"$exists": True}}
        ctx = {"metadata.tier": "premium"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_exists_true_missing(self) -> None:
        condition = {"metadata.tier": {"$exists": True}}
        ctx = {}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_exists_false(self) -> None:
        condition = {"metadata.tier": {"$exists": False}}
        ctx = {}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_exists_false_present(self) -> None:
        condition = {"metadata.tier": {"$exists": False}}
        ctx = {"metadata.tier": "premium"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_and_both_true(self) -> None:
        condition = {
            "$and": [
                {"params.model": {"$eq": "gpt-4o"}},
                {"metadata.tier": {"$eq": "premium"}},
            ]
        }
        ctx = {"params.model": "gpt-4o", "metadata.tier": "premium"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_and_one_false(self) -> None:
        condition = {
            "$and": [
                {"params.model": {"$eq": "gpt-4o"}},
                {"metadata.tier": {"$eq": "premium"}},
            ]
        }
        ctx = {"params.model": "gpt-4o", "metadata.tier": "free"}
        assert evaluate_condition(condition, ctx) is False

    def test_evaluate_or_one_true(self) -> None:
        condition = {
            "$or": [
                {"params.model": {"$eq": "gpt-4o"}},
                {"params.model": {"$eq": "claude-3"}},
            ]
        }
        ctx = {"params.model": "claude-3"}
        assert evaluate_condition(condition, ctx) is True

    def test_evaluate_or_both_false(self) -> None:
        condition = {
            "$or": [
                {"params.model": {"$eq": "gpt-4o"}},
                {"params.model": {"$eq": "claude-3"}},
            ]
        }
        ctx = {"params.model": "gemini-pro"}
        assert evaluate_condition(condition, ctx) is False

    def test_unknown_operator_raises(self) -> None:
        condition = {"params.model": {"$unknown": "value"}}
        ctx = {"params.model": "gpt-4o"}
        with pytest.raises(ValueError, match="Unknown operator"):
            evaluate_condition(condition, ctx)


@pytest.mark.requirement("FR-AROUTE-056")
class TestMatchConditionalRoute:
    def test_match_conditional_route_first_match(self) -> None:
        routes = [
            ConditionalRoute(
                condition={"params.model": {"$eq": "gpt-4o"}},
                target="openai-premium",
                name="premium",
            ),
            ConditionalRoute(
                condition={"params.model": {"$eq": "gpt-4o-mini"}},
                target="openai-standard",
                name="standard",
            ),
        ]
        ctx = {"params.model": "gpt-4o"}
        result = match_conditional_route(routes, ctx)
        assert result is not None
        assert result.target == "openai-premium"
        assert result.name == "premium"

    def test_match_no_match_returns_none(self) -> None:
        routes = [
            ConditionalRoute(
                condition={"params.model": {"$eq": "gpt-4o"}},
                target="openai-premium",
            ),
        ]
        ctx = {"params.model": "claude-3"}
        result = match_conditional_route(routes, ctx)
        assert result is None

    def test_match_returns_first_of_multiple_matches(self) -> None:
        routes = [
            ConditionalRoute(
                condition={"params.model": {"$in": ["gpt-4o", "gpt-4o-mini"]}},
                target="first-target",
            ),
            ConditionalRoute(
                condition={"params.model": {"$eq": "gpt-4o"}},
                target="second-target",
            ),
        ]
        ctx = {"params.model": "gpt-4o"}
        result = match_conditional_route(routes, ctx)
        assert result is not None
        assert result.target == "first-target"

    def test_match_empty_routes(self) -> None:
        result = match_conditional_route([], {"params.model": "gpt-4o"})
        assert result is None


@pytest.mark.requirement("FR-AROUTE-056")
class TestBuildRoutingContext:
    def test_build_routing_context_params(self) -> None:
        body = {"model": "gpt-4o", "stream": True, "temperature": 0.7}
        ctx = build_routing_context(body)
        assert ctx["params.model"] == "gpt-4o"
        assert ctx["params.stream"] is True
        assert ctx["params.temperature"] == 0.7

    def test_build_routing_context_metadata(self) -> None:
        body = {"model": "gpt-4o"}
        metadata = {"user_id": "u123", "tier": "premium"}
        ctx = build_routing_context(body, metadata)
        assert ctx["params.model"] == "gpt-4o"
        assert ctx["metadata.user_id"] == "u123"
        assert ctx["metadata.tier"] == "premium"

    def test_build_routing_context_no_metadata(self) -> None:
        body = {"model": "gpt-4o"}
        ctx = build_routing_context(body)
        assert "metadata.user_id" not in ctx

    def test_build_routing_context_empty_body(self) -> None:
        ctx = build_routing_context({})
        assert ctx == {}

    def test_build_routing_context_empty_metadata(self) -> None:
        body = {"model": "gpt-4o"}
        ctx = build_routing_context(body, {})
        assert "metadata." not in " ".join(ctx.keys())
