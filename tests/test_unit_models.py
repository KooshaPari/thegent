"""Unit tests for model catalog and route resolution."""


from thegent.models import (
    ModelCatalog,
    filter_models_for_provider,
    normalize_model_id,
    resolve_route,
    route_contract,
)


class TestResolveRoute:
    """Tests for resolve_route."""

    def test_resolves_gemini_3_flash_to_gemini_direct(self) -> None:
        """gemini-3-flash prefers gemini (direct) over antigravity (proxy)."""
        r = resolve_route("gemini-3-flash", policy="prefer_direct")
        assert r is not None
        provider, model_alias = r
        assert provider == "gemini"
        assert model_alias == "gemini-3-flash"

    def test_resolves_with_provider_hint(self) -> None:
        """provider_hint forces that provider if it serves the model."""
        r = resolve_route("gemini-3-flash", provider_hint="antigravity")
        assert r is not None
        provider, model_alias = r
        assert provider == "antigravity"
        assert model_alias == "gemini-3-flash"

    def test_resolves_claude_sonnet_alias(self) -> None:
        """sonnet alias maps to claude-sonnet-4.5 via claude provider."""
        r = resolve_route("sonnet", policy="prefer_direct")
        assert r is not None
        provider, model_alias = r
        assert provider == "claude"
        assert model_alias in ("sonnet", "claude-sonnet-4.5")

    def test_resolves_minimax_single_provider(self) -> None:
        """minimax-m2.5 only via minimax."""
        r = resolve_route("minimax-m2.5")
        assert r is not None
        provider, model_alias = r
        assert provider == "minimax"
        assert model_alias == "minimax-m2.5"

    def test_unknown_model_returns_none(self) -> None:
        """Unknown model returns None."""
        assert resolve_route("unknown-model-xyz") is None

    def test_invalid_provider_hint_returns_none(self) -> None:
        """provider_hint that doesn't serve model returns None."""
        assert resolve_route("minimax-m2.5", provider_hint="gemini") is None

    def test_provider_hint_gemini_via_minimax_returns_none(self) -> None:
        """gemini-3-flash not available via minimax (minimax only has MiniMax)."""
        assert resolve_route("gemini-3-flash", provider_hint="minimax") is None

    def test_routes_for_gemini_includes_providers_for_available_message(self) -> None:
        """routes_for returns providers for validation message (Phase 11)."""
        routes = ModelCatalog.routes_for("gemini-3-flash")
        providers = {r.provider for r in routes}
        assert "gemini" in providers
        assert "minimax" not in providers


class TestModelCatalog:
    """Tests for ModelCatalog."""

    def test_routes_for_returns_list(self) -> None:
        """routes_for returns non-empty list for known model."""
        routes = ModelCatalog.routes_for("gemini-3-flash")
        assert len(routes) >= 1
        assert any(r.provider == "gemini" for r in routes)

    def test_to_catalog_view_has_by_model(self) -> None:
        """to_catalog_view includes by_model with providers."""
        view = ModelCatalog.to_catalog_view()
        assert "by_model" in view.__dict__ or hasattr(view, "by_model")
        by_model = view.by_model
        assert "gemini-3-flash" in by_model
        assert "gemini" in by_model["gemini-3-flash"]

    def test_routes_for_use_scraped_false_returns_static_only(self) -> None:
        """routes_for(use_scraped=False) returns only static routes."""
        routes = ModelCatalog.routes_for("gemini-3-flash", use_scraped=False)
        assert len(routes) >= 1
        assert any(r.provider == "gemini" for r in routes)


class TestNormalizeModelId:
    """Tests for normalize_model_id (Phase 8 aliases)."""

    def test_sonnet_to_claude_sonnet_45(self) -> None:
        """sonnet -> claude-sonnet-4.5."""
        assert normalize_model_id("sonnet") == "claude-sonnet-4.5"

    def test_opus_to_claude_opus_46(self) -> None:
        """opus -> claude-opus-4.6."""
        assert normalize_model_id("opus") == "claude-opus-4.6"

    def test_unknown_passthrough(self) -> None:
        """Unknown model ID passes through."""
        assert normalize_model_id("custom-model-x") == "custom-model-x"


class TestFilterModels:
    """Tests for filter_models_for_provider (blacklist)."""

    def test_filters_gemini_pro(self) -> None:
        """gemini-*-pro variants are blacklisted."""
        filtered = filter_models_for_provider("gemini", ["gemini-3-flash", "gemini-3-pro-preview"])
        assert "gemini-3-flash" in filtered
        assert "gemini-3-pro-preview" not in filtered

    def test_filters_claude_3(self) -> None:
        """claude-3-* is blacklisted."""
        filtered = filter_models_for_provider("claude", ["claude-3-opus", "claude-haiku-4.5"])
        assert "claude-haiku-4.5" in filtered
        assert "claude-3-opus" not in filtered

    def test_allows_claude_45_46(self) -> None:
        """claude 4.5 and 4.6 are allowed."""
        filtered = filter_models_for_provider("claude", ["claude-haiku-4.5", "claude-opus-4.6"])
        assert "claude-haiku-4.5" in filtered
        assert "claude-opus-4.6" in filtered

    def test_filters_codex_gpt5_without_53(self) -> None:
        """codex: gpt-5 without 5.3 is blacklisted."""
        filtered = filter_models_for_provider("codex", ["gpt-5", "gpt-5.3-codex"])
        assert "gpt-5.3-codex" in filtered
        assert "gpt-5" not in filtered


class TestRouteContract:
    """Tests for route_contract (model routing schema metadata)."""

    def test_route_contract_has_schema_version(self) -> None:
        """route_contract returns schema_version for thegent://models/contract."""
        contract = route_contract()
        assert "schema_version" in contract
        assert contract["schema_version"] == 1

    def test_route_contract_has_backend_types(self) -> None:
        """route_contract includes backend_types."""
        contract = route_contract()
        assert "backend_types" in contract
        assert "direct" in contract["backend_types"]
        assert "proxy" in contract["backend_types"]

    def test_route_contract_has_policy_names(self) -> None:
        """route_contract includes policy_names."""
        contract = route_contract()
        assert "policy_names" in contract
        assert "prefer_direct" in contract["policy_names"]
