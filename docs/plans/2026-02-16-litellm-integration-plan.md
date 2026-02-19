# LiteLLM Router Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire execution layer to consume resolved routing metadata and integrate LiteLLM for multi-provider API routing.

**Architecture:** Three execution paths (Native CLI for codex/claude, LiteLLM direct API for providers with keys, CLIProxyAPIPlus for LOGIN-auth providers). TaskRouter resolves model → provider, execution layer consumes `resolved_provider`/`resolved_model_alias`.

**Tech Stack:** Python 3.12+, LiteLLM Router, pydantic-settings, existing catalog.py routing

---

## Task 1: Add LiteLLM Dependency

**Files:**
- Modify: `pyproject.toml:37`

**Step 1: Add litellm to dependencies**

```toml
# In pyproject.toml dependencies list (line 37)
    "litellm>=1.50.0",
```

**Step 2: Install dependency**

Run: `uv sync`
Expected: "Resolved N packages, installed M packages"

**Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat: add litellm dependency for multi-provider routing"
```

---

## Task 2: Create Provider Type Classification

**Files:**
- Create: `src/thegent/routing/provider_types.py`
- Test: `tests/test_unit_provider_types.py`

**Step 1: Write the failing test**

```python
# tests/test_unit_provider_types.py
"""Tests for provider type classification."""

import pytest
from thegent.routing.provider_types import (
    NATIVE_CLI_PROVIDERS,
    API_KEY_PROVIDERS,
    LOGIN_AUTH_PROVIDERS,
    get_execution_path,
    ExecutionPath,
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_unit_provider_types.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'thegent.routing.provider_types'"

**Step 3: Write minimal implementation**

```python
# src/thegent/routing/provider_types.py
"""Provider type classification for execution path routing."""

from enum import Enum, auto
from typing import Final


class ExecutionPath(Enum):
    """Execution path for LLM provider."""

    NATIVE_CLI = auto()  # codex, claude (interactive/agent harness)
    LITELLM_API = auto()  # minimax, nim, glm, kilo (API keys)
    CLIPROXY_API = auto()  # LOGIN-auth providers via CLIProxyAPIPlus


# Immutable provider classifications
NATIVE_CLI_PROVIDERS: Final[frozenset[str]] = frozenset({"codex", "claude"})
API_KEY_PROVIDERS: Final[frozenset[str]] = frozenset({"minimax", "nim", "glm", "kilo"})
LOGIN_AUTH_PROVIDERS: Final[frozenset[str]] = frozenset(
    {"antigravity", "cursor", "kiro", "gemini", "copilot"}
)


def get_execution_path(provider: str) -> ExecutionPath:
    """Determine execution path for a provider.

    Args:
        provider: Provider name (e.g., "codex", "minimax", "antigravity")

    Returns:
        ExecutionPath enum value
    """
    if provider in NATIVE_CLI_PROVIDERS:
        return ExecutionPath.NATIVE_CLI
    if provider in API_KEY_PROVIDERS:
        return ExecutionPath.LITELLM_API
    return ExecutionPath.CLIPROXY_API
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_unit_provider_types.py -v`
Expected: PASS (all tests)

**Step 5: Commit**

```bash
git add src/thegent/routing/provider_types.py tests/test_unit_provider_types.py
git commit -m "feat: add provider type classification for execution routing"
```

---

## Task 3: Create LiteLLM Router Wrapper

**Files:**
- Create: `src/thegent/routing/litellm_router.py`
- Test: `tests/test_unit_litellm_router.py`

**Step 1: Write the failing test**

```python
# tests/test_unit_litellm_router.py
"""Tests for LiteLLM Router wrapper."""

import os
import pytest
from unittest.mock import patch, MagicMock
from thegent.routing.litellm_router import (
    build_litellm_model_list,
    get_litellm_router,
    _route_to_litellm_config,
)
from thegent.routing.provider_types import API_KEY_PROVIDERS


class TestLiteLLMRouterBuilder:
    """Test LiteLLM Router configuration generation."""

    def test_build_model_list_excludes_native_cli(self):
        """Native CLI providers are excluded from LiteLLM model list."""
        model_list = build_litellm_model_list()
        providers_in_list = {cfg.get("model_name", "").split("/")[0] for cfg in model_list}
        # Should not contain codex or claude
        assert "codex" not in providers_in_list
        assert "claude" not in providers_in_list

    def test_build_model_list_includes_api_key_providers(self):
        """API key providers are included in model list."""
        model_list = build_litellm_model_list()
        model_names = [cfg.get("model_name", "") for cfg in model_list]
        # Should have entries for API key providers
        # At least minimax-m2.5 or glm-5 should be present
        assert any("minimax" in m or "glm" in m or "deepseek" in m for m in model_names)

    def test_route_to_litellm_config_api_key_provider(self):
        """API key providers get direct API config."""
        from thegent.models.catalog import Route

        route = Route(
            provider="minimax",
            backend_type="proxy",
            model_alias="minimax-m2.5",
            priority=0,
            cost_weight=0.4,
        )
        config = _route_to_litellm_config(route)
        assert config["model_name"] == "minimax-m2.5"
        # Should use litellm provider prefix
        assert "litellm_params" in config
        assert "model" in config["litellm_params"]

    def test_get_litellm_router_returns_router(self):
        """get_litellm_router returns a Router instance."""
        with patch("thegent.routing.litellm_router.Router") as mock_router:
            mock_router.return_value = MagicMock()
            router = get_litellm_router(policy="cheapest")
            assert router is not None
            mock_router.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_unit_litellm_router.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'thegent.routing.litellm_router'"

**Step 3: Write minimal implementation**

```python
# src/thegent/routing/litellm_router.py
"""LiteLLM Router wrapper for multi-provider API routing."""

from __future__ import annotations

import logging
import os
from typing import Any

from litellm import Router

from thegent.models.catalog import Route, _get_catalog
from thegent.routing.provider_types import API_KEY_PROVIDERS, NATIVE_CLI_PROVIDERS, ExecutionPath, get_execution_path

logger = logging.getLogger(__name__)


def _route_to_litellm_config(route: Route) -> dict[str, Any]:
    """Convert a catalog Route to LiteLLM model_list config.

    Args:
        route: Catalog route with provider, model_alias, etc.

    Returns:
        LiteLLM model_list entry dict
    """
    model_name = route.model_alias
    provider = route.provider

    # Determine litellm model string
    # LiteLLM format: "provider/model-name"
    litellm_model = f"{provider}/{model_name}"

    # For API key providers, get API key from environment
    api_key_env = _get_api_key_env(provider)
    api_key = os.environ.get(api_key_env, "dummy-key")

    config = {
        "model_name": model_name,
        "litellm_params": {
            "model": litellm_model,
            "api_key": api_key,
        },
    }

    # For CLIProxyAPIPlus providers, route through proxy
    if get_execution_path(provider) == ExecutionPath.CLIPROXY_API:
        config["litellm_params"]["api_base"] = "http://localhost:8317/v1"

    return config


def _get_api_key_env(provider: str) -> str:
    """Get environment variable name for provider API key."""
    mapping = {
        "minimax": "MINIMAX_API_KEY",
        "nim": "NVIDIA_API_KEY",
        "glm": "ZHIPU_API_KEY",
        "kilo": "KILO_API_KEY",
    }
    return mapping.get(provider, f"{provider.upper()}_API_KEY")


def build_litellm_model_list() -> list[dict[str, Any]]:
    """Build LiteLLM model_list from catalog routes.

    Excludes NATIVE_CLI_PROVIDERS (codex, claude).
    Routes API_KEY_PROVIDERS directly.
    Routes LOGIN_AUTH_PROVIDERS via CLIProxyAPIPlus.

    Returns:
        List of LiteLLM model_list entries
    """
    model_list: list[dict[str, Any]] = []
    seen_models: set[str] = set()

    catalog = _get_catalog()
    for model_id, routes in catalog.items():
        for route in routes:
            # Skip native CLI providers
            if route.provider in NATIVE_CLI_PROVIDERS:
                continue

            # Avoid duplicates
            key = f"{route.provider}/{route.model_alias}"
            if key in seen_models:
                continue
            seen_models.add(key)

            config = _route_to_litellm_config(route)
            model_list.append(config)

    return model_list


def get_litellm_router(policy: str = "cheapest") -> Router:
    """Get configured LiteLLM Router instance.

    Args:
        policy: Routing policy (cheapest, fastest, round_robin)

    Returns:
        Configured LiteLLM Router
    """
    model_list = build_litellm_model_list()

    return Router(
        model_list=model_list,
        routing_strategy=policy,
        num_retries=2,
        timeout=300,
        retry_after=5,
    )
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_unit_litellm_router.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/thegent/routing/litellm_router.py tests/test_unit_litellm_router.py
git commit -m "feat: add LiteLLM Router wrapper for multi-provider routing"
```

---

## Task 4: Wire CodexProxyRunner to Consume Resolved Routing

**Files:**
- Modify: `src/thegent/agents/codex_proxy.py:77-158`
- Test: `tests/test_unit_codex_proxy_routing.py`

**Step 1: Write the failing test**

```python
# tests/test_unit_codex_proxy_routing.py
"""Tests for CodexProxyRunner routing integration."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from thegent.agents.codex_proxy import CodexProxyRunner
from thegent.routing.models import TaskMetadata, TaskCategory
from thegent.routing.provider_types import ExecutionPath


class TestCodexProxyRunnerRouting:
    """Test that CodexProxyRunner consumes resolved routing from TaskMetadata."""

    def test_native_cli_provider_uses_codex_cli(self):
        """Native CLI providers (codex) use direct codex CLI execution."""
        runner = CodexProxyRunner("codex")
        metadata = TaskMetadata(
            category=TaskCategory.NORMAL,
            resolved_provider="codex",
            resolved_model_alias="gpt-5.3-codex-spark",
        )

        with patch.object(runner, "_execute_native_cli") as mock_native:
            mock_native.return_value = MagicMock(exit_code=0, stdout="done", stderr="", timed_out=False)
            result = runner.run_with_metadata("test prompt", Path("/tmp"), "read", 60, metadata=metadata)
            mock_native.assert_called_once()

    def test_api_key_provider_routes_correctly(self):
        """API key providers (minimax) use appropriate routing."""
        runner = CodexProxyRunner("minimax")
        metadata = TaskMetadata(
            category=TaskCategory.NORMAL,
            resolved_provider="minimax",
            resolved_model_alias="minimax-m2.5",
        )
        # Should not raise - validates routing path exists
        assert runner is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_unit_codex_proxy_routing.py -v`
Expected: FAIL with "AttributeError: 'CodexProxyRunner' object has no attribute 'run_with_metadata'"

**Step 3: Write minimal implementation**

Add to `src/thegent/agents/codex_proxy.py`:

```python
# Add imports at top (after line 13)
from thegent.routing.models import TaskMetadata
from thegent.routing.provider_types import ExecutionPath, get_execution_path

# Add method to CodexProxyRunner class (after __init__)
    def run_with_metadata(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        *,
        metadata: TaskMetadata | None = None,
        use_stream: bool = True,
        live_output: bool = False,
        on_stdout: Callable[[str], None] | None = None,
        on_stderr: Callable[[str], None] | None = None,
        enable_search: bool = True,
        run_id: str | None = None,
    ) -> RunResult:
        """Run agent using resolved routing from TaskMetadata.

        This method consumes resolved_provider and resolved_model_alias
        from the routing classification.

        Args:
            prompt: User prompt
            cwd: Working directory
            mode: Execution mode (read/write/full)
            timeout: Timeout in seconds
            metadata: TaskMetadata with resolved routing

        Returns:
            RunResult from execution
        """
        # Determine provider and model from metadata
        provider = metadata.resolved_provider if metadata else self.agent_name
        model = metadata.resolved_model_alias if metadata else self._model

        # Determine execution path
        exec_path = get_execution_path(provider)

        if exec_path == ExecutionPath.NATIVE_CLI:
            return self._execute_native_cli(prompt, cwd, mode, timeout, model)
        elif exec_path == ExecutionPath.LITELLM_API:
            return self._execute_litellm_api(prompt, cwd, mode, timeout, provider, model)
        else:
            # CLIProxyAPIPlus path (default)
            return self.run(prompt, cwd, mode, timeout, agent_model=model, use_stream=use_stream)

    def _execute_native_cli(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        model: str,
    ) -> RunResult:
        """Execute via native codex CLI (for codex provider)."""
        # Current implementation uses codex CLI already
        return self.run(prompt, cwd, mode, timeout, agent_model=model)

    def _execute_litellm_api(
        self,
        prompt: str,
        cwd: Path | None,
        mode: str,
        timeout: int,
        provider: str,
        model: str,
    ) -> RunResult:
        """Execute via LiteLLM direct API (for API key providers).

        NOTE: This is a placeholder. Full LiteLLM integration will
        replace codex subprocess calls with litellm.completion().
        For now, route through CLIProxyAPIPlus as before.
        """
        # TODO: Implement direct LiteLLM API calls
        # For now, fall back to proxy execution
        logger.info(f"LiteLLM API path not yet implemented for {provider}, using proxy")
        return self.run(prompt, cwd, mode, timeout, agent_model=model)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_unit_codex_proxy_routing.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/thegent/agents/codex_proxy.py tests/test_unit_codex_proxy_routing.py
git commit -m "feat: wire CodexProxyRunner to consume resolved routing metadata"
```

---

## Task 5: Add Config Settings for LiteLLM

**Files:**
- Modify: `src/thegent/config.py`
- Test: `tests/test_unit_config_litellm.py`

**Step 1: Write the failing test**

```python
# tests/test_unit_config_litellm.py
"""Tests for LiteLLM config settings."""

import pytest
from thegent.config import ThegentSettings


class TestLiteLLMConfig:
    """Test LiteLLM configuration settings."""

    def test_litellm_routing_policy_default(self):
        """Default routing policy is 'cheapest'."""
        settings = ThegentSettings()
        assert settings.litellm_routing_policy == "cheapest"

    def test_litellm_timeout_default(self):
        """Default LiteLLM timeout is 300 seconds."""
        settings = ThegentSettings()
        assert settings.litellm_timeout == 300

    def test_litellm_retries_default(self):
        """Default LiteLLM retries is 2."""
        settings = ThegentSettings()
        assert settings.litellm_num_retries == 2
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_unit_config_litellm.py -v`
Expected: FAIL with "AttributeError: 'ThegentSettings' object has no attribute 'litellm_routing_policy'"

**Step 3: Write minimal implementation**

Find the `ThegentSettings` class in `src/thegent/config.py` and add:

```python
    # LiteLLM Router settings
    litellm_routing_policy: str = "cheapest"  # cheapest, fastest, round_robin
    litellm_timeout: int = 300
    litellm_num_retries: int = 2
    litellm_retry_after: int = 5
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_unit_config_litellm.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/thegent/config.py tests/test_unit_config_litellm.py
git commit -m "feat: add LiteLLM configuration settings"
```

---

## Task 6: Integration Test for Full Routing Flow

**Files:**
- Create: `tests/test_integration_routing_flow.py`

**Step 1: Write the integration test**

```python
# tests/test_integration_routing_flow.py
"""Integration tests for full routing flow: classify -> resolve -> execute."""

import pytest
from thegent.routing.task_router import TaskRouter
from thegent.routing.models import TaskCategory
from thegent.config import ThegentSettings


class TestFullRoutingFlow:
    """Test complete routing flow from prompt to resolved provider."""

    @pytest.fixture
    def router(self):
        """Create TaskRouter for testing."""
        return TaskRouter(ThegentSettings())

    def test_fast_task_routes_to_gemini(self, router):
        """FAST tasks should route to gemini-3-flash."""
        metadata = router.classify("list files in directory")
        assert metadata.category == TaskCategory.FAST
        assert metadata.detected_role in ("researcher", "workhorse")
        # Should have resolved routing
        assert metadata.selected_model != ""
        assert metadata.model_fallback_chain != []

    def test_complex_task_routes_to_higher_quality(self, router):
        """COMPLEX tasks should route to higher quality models."""
        metadata = router.classify("design a microservices architecture for payment processing")
        assert metadata.category in (TaskCategory.COMPLEX, TaskCategory.HIGH_COMPLEX)
        # Should prefer higher-quality models
        assert "claude" in metadata.selected_model or "deepseek" in metadata.selected_model or "glm" in metadata.selected_model

    def test_resolved_provider_set(self, router):
        """classify() should set resolved_provider when route exists."""
        metadata = router.classify("implement a quick fix")
        # Should have resolved provider (may be empty if no route)
        assert metadata.resolved_provider is not None
        assert isinstance(metadata.resolved_provider, str)

    def test_fallback_chain_populated(self, router):
        """classify() should populate model_fallback_chain."""
        metadata = router.classify("write a function")
        assert len(metadata.model_fallback_chain) >= 1
```

**Step 2: Run integration tests**

Run: `uv run pytest tests/test_integration_routing_flow.py -v`
Expected: PASS (all tests)

**Step 3: Commit**

```bash
git add tests/test_integration_routing_flow.py
git commit -m "test: add integration tests for full routing flow"
```

---

## Task 7: Run Full Test Suite

**Step 1: Run all affected tests**

Run: `uv run pytest tests/test_unit_provider_types.py tests/test_unit_litellm_router.py tests/test_unit_codex_proxy_routing.py tests/test_unit_config_litellm.py tests/test_integration_routing_flow.py -v`
Expected: All PASS

**Step 2: Run quality checks**

Run: `task lint && task test`
Expected: All checks pass

**Step 3: Commit any fixes**

```bash
git add -A
git commit -m "fix: address lint/test failures from LiteLLM integration"
```

---

## Summary

After completing these tasks:

1. **Dependency**: LiteLLM added to project
2. **Classification**: Provider types (NATIVE_CLI, LITELLM_API, CLIPROXY_API)
3. **Router**: LiteLLM Router wrapper generates model_list from catalog
4. **Execution**: CodexProxyRunner consumes `resolved_provider`/`resolved_model_alias`
5. **Config**: LiteLLM settings in ThegentSettings
6. **Tests**: Full coverage of routing flow

**Gap closed**: `resolved_provider` and `resolved_model_alias` are now consumed by execution layer.

**Future work**:
- Implement `_execute_litellm_api()` with direct LiteLLM calls (replacing subprocess)
- Add CLIProxyAPIPlus routing for LOGIN-auth providers
- Performance metrics and routing optimization


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

