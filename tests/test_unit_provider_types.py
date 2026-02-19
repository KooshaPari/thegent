"""Tests for provider type classification."""

import pytest

from thegent.routing.provider_types import (
    NATIVE_CLI_PROVIDERS,
    ExecutionPath,
    get_execution_path,
)


class TestProviderClassification:
    """Test provider type classification for execution path routing."""

    def test_native_cli_providers_immutable(self):
        """Native CLI providers set is frozen."""
        with pytest.raises((AttributeError, TypeError)):
            NATIVE_CLI_PROVIDERS.add("new_provider")

    def test_codex_is_native_cli(self):
        """Codex uses native CLI execution."""
        assert get_execution_path("codex") == ExecutionPath.NATIVE_CLI

    def test_claude_is_native_cli(self):
        """Claude uses native CLI execution (interactive)."""
        assert get_execution_path("claude") == ExecutionPath.NATIVE_CLI

    def test_minimax_is_api_key(self):
        """Minimax uses LiteLLM direct API."""
        assert get_execution_path("minimax") == ExecutionPath.LITELLM_API

    def test_nim_is_api_key(self):
        """NIM uses LiteLLM direct API."""
        assert get_execution_path("nim") == ExecutionPath.LITELLM_API

    def test_glm_is_api_key(self):
        """GLM uses LiteLLM direct API."""
        assert get_execution_path("glm") == ExecutionPath.LITELLM_API

    def test_kilo_is_api_key(self):
        """Kilo uses LiteLLM direct API."""
        assert get_execution_path("kilo") == ExecutionPath.LITELLM_API

    def test_unknown_provider_is_login_auth(self):
        """Unknown providers default to CLIProxyAPIPlus."""
        assert get_execution_path("unknown_provider") == ExecutionPath.CLIPROXY_API

    def test_antigravity_is_login_auth(self):
        """Antigravity uses CLIProxyAPIPlus (LOGIN auth)."""
        assert get_execution_path("antigravity") == ExecutionPath.CLIPROXY_API
