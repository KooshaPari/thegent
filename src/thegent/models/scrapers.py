"""Model scrapers for dynamic discovery.

OPT-005: Uses asyncio.gather for parallel async scraping (3-5x faster than sequential).
"""

import asyncio
import contextlib
import re
import subprocess
import time
from pathlib import Path
from typing import Protocol

import httpx

from thegent.cache.multi_level import MultiLevelCache
from thegent.config import ThegentSettings
from thegent.infra import run_subprocess_optimized


class ModelScraper(Protocol):
    """Protocol for provider-specific model scrapers (Phase 12). Returns model IDs."""

    def __call__(self, settings: ThegentSettings | None = None) -> list[str]:
        """Scrape models for this provider. Returns model IDs."""
        ...


def _make_models_cache() -> MultiLevelCache:
    """Create multi-level cache for scraped model lists.

    L1: fast in-process TTLCache (5 min);
    L2: diskcache on disk (1 h, survives restarts between CLI invocations).
    Falls back to L1-only if ThegentSettings cannot be loaded.
    """
    try:
        settings = ThegentSettings()
        l2_dir = settings.cache_dir / "models-cache"
    except Exception:
        l2_dir = Path.home() / ".cache" / "thegent" / "models-cache"
    return MultiLevelCache(l1_maxsize=32, l1_ttl=300, l2_dir=l2_dir, l2_ttl=3600)


_MODELS_CACHE: MultiLevelCache = _make_models_cache()


def _models_cache_dir() -> Path:
    """Return the L2 directory for the models cache (for introspection/invalidation)."""
    l2 = _MODELS_CACHE.l2_dir
    if l2 is not None:
        return l2
    return Path.home() / ".cache" / "thegent" / "models-cache"


def get_models_cache_path() -> Path:
    """Return path to models cache directory (for invalidation)."""
    return _models_cache_dir()


def invalidate_models_cache() -> bool:
    """Clear models cache. Returns True if cache had entries and was cleared."""
    try:
        had = _MODELS_CACHE.get("by_provider") is not None
        _MODELS_CACHE.clear()
        return had
    except Exception:
        return False


def _load_cached(ttl_sec: int = 300) -> tuple[dict[str, list[str]], float] | None:
    """Load cached scrape result. Returns (by_provider, mtime) or None on miss.

    TTL is enforced by MultiLevelCache layers; the ttl_sec argument is accepted for
    backwards-compatibility but is no longer used for manual expiry checks.
    """
    try:
        by_provider = _MODELS_CACHE.get("by_provider")
        if by_provider is None:
            return None
        mtime = _MODELS_CACHE.get("by_provider_mtime") or 0.0
        return (by_provider, float(mtime))
    except Exception:
        return None


def _save_cache(by_provider: dict[str, list[str]], ttl_sec: int = 300) -> None:
    """Save scrape result via MultiLevelCache (write-through to L1 + L2)."""
    try:
        _MODELS_CACHE.set("by_provider", by_provider, ttl=float(ttl_sec))
        _MODELS_CACHE.set("by_provider_mtime", time.time(), ttl=float(ttl_sec))
    except Exception:
        pass


def scrape_all(settings: ThegentSettings | None = None) -> dict[str, list[str]]:
    """
    Synchronous wrapper for scrape_all_async. Uses asyncio.run() to execute async version.
    OPT-005: Model catalog scraping with async gather (3-5x faster than sequential).
    Scrape all providers. Returns by_provider: {provider: [model_id, ...]}.
    Filters blacklisted models; unparseable allowed. Per-provider fallback on adapter failure.
    SA2: gemini, SA3: claude, SA4: cursor/copilot, SA5: proxy (antigravity/minimax/glm).
    """
    # OPT-005: Use async version via asyncio.run()
    try:
        # Check if we're already in an event loop
        try:
            asyncio.get_running_loop()
            # If we're in a loop, use ThreadPoolExecutor fallback
            from concurrent.futures import ThreadPoolExecutor, as_completed

            from thegent.models.catalog import filter_models_for_provider

            settings = settings or ThegentSettings()
            by_provider: dict[str, list[str]] = {}

            def _scrape_cursor() -> tuple[str, list[str]]:
                try:
                    cursor_models = scrape_cursor()
                    filtered_cursor = filter_models_for_provider("cursor-agent", cursor_models) if cursor_models else []
                    return ("cursor-agent", filtered_cursor or [settings.default_cursor_model])
                except Exception:
                    return ("cursor-agent", [settings.default_cursor_model])

            def _scrape_cursor_api() -> tuple[str, list[str]]:
                try:
                    cursor_api_models = scrape_cursor_api(settings)
                    filtered_cursor_api = (
                        filter_models_for_provider("cursor-api", cursor_api_models) if cursor_api_models else []
                    )
                    return (
                        "cursor-api",
                        filtered_cursor_api
                        or ["claude-4.5-opus-high-thinking", "gpt-5.1-codex", "claude-4.5-sonnet-thinking"],
                    )
                except Exception:
                    return (
                        "cursor-api",
                        ["claude-4.5-opus-high-thinking", "gpt-5.1-codex", "claude-4.5-sonnet-thinking"],
                    )

            def _scrape_copilot() -> tuple[str, list[str]]:
                try:
                    copilot_models = scrape_copilot()
                    filtered_copilot = filter_models_for_provider("copilot", copilot_models) if copilot_models else []
                    return ("copilot", filtered_copilot or [settings.default_copilot_model])
                except Exception:
                    return ("copilot", [settings.default_copilot_model])

            def _scrape_gemini() -> tuple[str, list[str]]:
                try:
                    gemini_models = scrape_gemini()
                    filtered_gemini = filter_models_for_provider("gemini", gemini_models) if gemini_models else []
                    return ("gemini", filtered_gemini or [settings.default_gemini_model])
                except Exception:
                    return ("gemini", [settings.default_gemini_model])

            def _scrape_claude() -> tuple[str, list[str]]:
                try:
                    claude_models = scrape_claude()
                    filtered_claude = filter_models_for_provider("claude", claude_models) if claude_models else []
                    return ("claude", filtered_claude or [settings.default_claude_model])
                except Exception:
                    return ("claude", [settings.default_claude_model])

            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {
                    executor.submit(_scrape_cursor): "cursor-agent",
                    executor.submit(_scrape_cursor_api): "cursor-api",
                    executor.submit(_scrape_copilot): "copilot",
                    executor.submit(_scrape_gemini): "gemini",
                    executor.submit(_scrape_claude): "claude",
                }
                for future in as_completed(futures):
                    provider, models = future.result()
                    by_provider[provider] = models
            return by_provider
        except RuntimeError:
            # No running loop, use asyncio.run()
            return asyncio.run(scrape_all_async(settings))
    except Exception:
        # Fallback to sequential if async fails
        settings = settings or ThegentSettings()
        fallback_by_provider: dict[str, list[str]] = {}
        fallback_by_provider["cursor-agent"] = scrape_cursor() or [settings.default_cursor_model]
        fallback_by_provider["cursor-api"] = scrape_cursor_api(settings) or [
            "claude-4.5-opus-high-thinking",
            "gpt-5.1-codex",
        ]
        fallback_by_provider["copilot"] = scrape_copilot() or [settings.default_copilot_model]
        fallback_by_provider["gemini"] = scrape_gemini() or [settings.default_gemini_model]
        fallback_by_provider["claude"] = scrape_claude() or [settings.default_claude_model]
        return fallback_by_provider


def get_scraped_catalog(
    use_cache: bool = True,
    refresh: bool = False,
    settings: ThegentSettings | None = None,
) -> dict[str, list[str]]:
    """
    Get scraped by_provider. Uses cache if use_cache and not refresh.
    Returns {provider: [model_id, ...]}.
    """
    settings = settings or ThegentSettings()
    ttl = settings.models_cache_ttl_sec
    if use_cache and not refresh:
        cached = _load_cached(ttl_sec=ttl)
        if cached:
            return cached[0]
    result = scrape_all(settings)
    if use_cache:
        _save_cache(result, ttl_sec=ttl)
    return result


_PROXY_CHECK_TIMEOUT = 3


def _scrape_proxy_models(base_url: str) -> list[str]:
    """Fetch model IDs from proxy GET /v1/models (OpenAI-compatible)."""
    models: list[str] = []
    url = f"{base_url.rstrip('/')}/v1/models"
    try:
        resp = httpx.get(
            url,
            headers={"Authorization": "Bearer sk-dummy"},
            timeout=_PROXY_CHECK_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            mid = item.get("id")
            if mid and isinstance(mid, str):
                models.append(mid)
    except Exception:
        pass
    return models


def scrape_proxy(settings: ThegentSettings | None = None) -> dict[str, list[str]]:
    """
    Scrape proxy models. Returns {provider: [model_id, ...]} for antigravity, minimax, glm.
    Maps proxy model IDs to thegent providers by prefix/heuristic.
    """
    settings = settings or ThegentSettings()
    base_url = f"http://127.0.0.1:{settings.cliproxy_port}/v1"
    try:
        from thegent.agents.cliproxy_manager import ensure_proxy_running

        base_url = ensure_proxy_running(settings)
    except Exception:
        pass

    raw = _scrape_proxy_models(base_url)
    result: dict[str, list[str]] = {
        "antigravity": [],
        "minimax": [],
        "glm": [],
        "roo": [],
        "kilo": [],
        "gemini": [],
        "claude": [],
    }
    for m in raw:
        m_lower = m.lower()
        if "minimax" in m_lower or m == "minimax-m2.5":
            result["minimax"].append(m)
        elif "glm" in m_lower or m == "glm-5":
            result["glm"].append(m)
        elif "gemini" in m_lower:
            result["gemini"].append(m)
        elif "claude" in m_lower:
            result["claude"].append(m)
        elif "roo" in m_lower:
            result["roo"].append(m)
        elif "kilo" in m_lower:
            result["kilo"].append(m)
        else:
            result["antigravity"].append(m)
    if not result["minimax"]:
        result["minimax"] = ["minimax-m2.5"]
    if not result["glm"]:
        result["glm"] = ["glm-5"]
    return result


def scrape_cursor() -> list[str]:
    """Scrape cursor agent --list-models."""
    try:
        proc = run_subprocess_optimized(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout:
            stdout_text = proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", errors="replace")
            return [l.strip() for l in stdout_text.splitlines() if l.strip() and not l.strip().startswith("Tip:")]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return []


def scrape_cursor_api(settings: ThegentSettings | None = None) -> list[str]:
    """Scrape cursor-api (wisdgod) GET /v1/models."""
    settings = settings or ThegentSettings()
    base_url = settings.cursor_api_url.rstrip("/")
    token = settings.cursor_api_token or ""
    return _scrape_cursor_api_models(base_url, token)


def _scrape_cursor_api_models(base_url: str, token: str) -> list[str]:
    """Fetch model IDs from cursor-api GET /v1/models."""
    models: list[str] = []
    url = f"{base_url}/v1/models"
    try:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        resp = httpx.get(url, headers=headers, timeout=_PROXY_CHECK_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            mid = item.get("id")
            if mid and isinstance(mid, str):
                models.append(mid)
    except Exception:
        pass
    return models


def scrape_copilot() -> list[str]:
    """Scrape copilot --help for --model choices."""
    try:
        proc = run_subprocess_optimized(
            ["copilot", "--help"],
            check=False,
            capture_output=True,
            timeout=8,
        )
        if proc.returncode == 0 and proc.stdout:
            stdout_text = proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", errors="replace")
            if "--model" in stdout_text:
                start = stdout_text.find("--model")
                chunk = stdout_text[start : start + 600] if start >= 0 else ""
                choices = re.findall(r'"([a-zA-Z0-9.-]+)"', chunk)
                seen: set[str] = set()
                out: list[str] = []
                for c in choices:
                    if c not in seen and ("claude" in c or "gpt" in c or "gemini" in c):
                        seen.add(c)
                        out.append(c)
                return out
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ["claude-haiku-4.5", "gpt-5.3-codex", "gemini-3-flash"]


def scrape_gemini() -> list[str]:
    """Scrape gemini models: try 'gemini models list' or 'gemini list-models', else --help."""
    fallback = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-3-flash"]
    for cmd in [["gemini", "models", "list"], ["gemini", "list-models"], ["gemini", "--help"]]:
        try:  # noqa: PERF203 -- fallback chain pattern, trying multiple commands
            proc = run_subprocess_optimized(
                cmd,
                check=False,
                capture_output=True,
                timeout=4,
            )
            if proc.returncode == 0 and proc.stdout:
                stdout_text = (
                    proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", errors="replace")
                )
                matches = re.findall(r"gemini-[a-zA-Z0-9.-]+", stdout_text)
                if matches:
                    return list(dict.fromkeys(matches))
        except (FileNotFoundError, subprocess.TimeoutExpired):  # noqa: PERF203 - intentional per-item error handling
            continue
    return fallback


def scrape_claude() -> list[str]:
    """Scrape claude models: try 'claude models list', else --help for --model aliases."""
    fallback = ["haiku", "sonnet", "opus", "claude-haiku-4.5", "claude-sonnet-4.5", "claude-opus-4.6"]
    for cmd in [["claude", "models", "list"], ["claude", "list-models"], ["claude", "--help"]]:
        try:  # noqa: PERF203 -- fallback chain pattern, trying multiple commands
            proc = run_subprocess_optimized(
                cmd,
                check=False,
                capture_output=True,
                timeout=4,
            )
            if proc.returncode == 0 and proc.stdout:
                stdout_text = (
                    proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", errors="replace")
                )
                out: list[str] = ["haiku", "sonnet", "opus"]
                matches = re.findall(r"claude-[a-zA-Z0-9.-]+", stdout_text)
                for m in matches:
                    if m not in out:
                        out.append(m)
                if len(out) > 3:
                    return out
        except (FileNotFoundError, subprocess.TimeoutExpired):  # noqa: PERF203 - intentional per-item error handling
            continue
    return fallback


def scrape_minimax_from_proxy() -> list[str]:
    """MiniMax models from proxy (minimax: block in config). Fallback to static."""
    return ["minimax-m2.5"]


def scrape_ante() -> list[str]:
    """Scrape Ante agent available models from settings.json."""
    from thegent.models.ante_scraper import scrape_ante_models

    return scrape_ante_models()


# Registry: provider -> scraper callable (settings) -> list[str]. Phase 12.
# SA2: gemini, SA3: claude, SA4: cursor/copilot, SA5: antigravity/minimax/glm (via scrape_proxy in scrape_all)
# SA6: ante (Ante agent harness)
SCRAPER_REGISTRY: dict[str, ModelScraper] = {
    "cursor-agent": lambda settings=None: scrape_cursor(),
    "copilot": lambda settings=None: scrape_copilot(),
    "gemini": lambda settings=None: scrape_gemini(),
    "claude": lambda settings=None: scrape_claude(),
    "ante": lambda settings=None: scrape_ante(),
}


async def scrape_all_async(settings: ThegentSettings | None = None) -> dict[str, list[str]]:
    """
    OPT-005: Async version of scrape_all using asyncio.gather for parallel execution.
    Scrape all providers. Returns by_provider: {provider: [model_id, ...]}.
    Filters blacklisted models; unparseable allowed. Per-provider fallback on adapter failure.
    SA2: gemini, SA3: claude, SA4: cursor/copilot, SA5: proxy (antigravity/minimax/glm).
    """
    from thegent.models.catalog import filter_models_for_provider

    settings = settings or ThegentSettings()
    by_provider: dict[str, list[str]] = {}

    # Proxy (antigravity, minimax, glm, gemini, claude) - SA5
    proxy_result: dict[str, list[str]] = {
        "antigravity": [],
        "minimax": [],
        "glm": [],
        "roo": [],
        "kilo": [],
        "gemini": [],
        "claude": [],
    }
    with contextlib.suppress(Exception):
        proxy_result = scrape_proxy(settings)

    # OPT-016: Parallel scraping for independent providers (3-5x faster)
    def _scrape_cursor() -> tuple[str, list[str]]:
        try:
            cursor_models = scrape_cursor()
            filtered_cursor = filter_models_for_provider("cursor-agent", cursor_models) if cursor_models else []
            return ("cursor-agent", filtered_cursor or [settings.default_cursor_model])
        except Exception:
            return ("cursor-agent", [settings.default_cursor_model])

    def _scrape_cursor_api() -> tuple[str, list[str]]:
        try:
            cursor_api_models = scrape_cursor_api(settings)
            filtered_cursor_api = (
                filter_models_for_provider("cursor-api", cursor_api_models) if cursor_api_models else []
            )
            return (
                "cursor-api",
                filtered_cursor_api
                or [
                    "claude-4.5-opus-high-thinking",
                    "gpt-5.1-codex",
                    "claude-4.5-sonnet-thinking",
                ],
            )
        except Exception:
            return ("cursor-api", ["claude-4.5-opus-high-thinking", "gpt-5.1-codex", "claude-4.5-sonnet-thinking"])

    def _scrape_copilot() -> tuple[str, list[str]]:
        try:
            copilot_models = scrape_copilot()
            filtered_copilot = filter_models_for_provider("copilot", copilot_models) if copilot_models else []
            return ("copilot", filtered_copilot or [settings.default_copilot_model])
        except Exception:
            return ("copilot", [settings.default_copilot_model])

    def _scrape_gemini() -> tuple[str, list[str]]:
        try:
            gemini_models = scrape_gemini()
            proxy_gemini = proxy_result.get("gemini", [])
            combined_gemini = list(dict.fromkeys(gemini_models + proxy_gemini))
            filtered_gemini = filter_models_for_provider("gemini", combined_gemini) if combined_gemini else []
            return ("gemini", filtered_gemini or [settings.default_gemini_model])
        except Exception:
            return ("gemini", [settings.default_gemini_model])

    def _scrape_claude() -> tuple[str, list[str]]:
        try:
            claude_models = scrape_claude()
            proxy_claude = proxy_result.get("claude", [])
            combined_claude = list(dict.fromkeys(claude_models + proxy_claude))
            filtered_claude = filter_models_for_provider("claude", combined_claude) if combined_claude else []
            return ("claude", filtered_claude or [settings.default_claude_model])
        except Exception:
            return ("claude", [settings.default_claude_model])

    def _scrape_ante() -> tuple[str, list[str]]:
        try:
            ante_models = scrape_ante()
            filtered_ante = filter_models_for_provider("ante", ante_models) if ante_models else []
            return ("ante", filtered_ante or ["claude-haiku-4-5"])
        except Exception:
            return ("ante", ["claude-haiku-4-5"])

    # OPT-005: Use asyncio.gather for parallel async execution (3-5x faster)
    # Wrap sync functions in async using asyncio.to_thread (Python 3.9+) or run_in_executor
    async def _scrape_cursor_async() -> tuple[str, list[str]]:
        return (
            await asyncio.to_thread(_scrape_cursor)
            if hasattr(asyncio, "to_thread")
            else await asyncio.get_event_loop().run_in_executor(None, _scrape_cursor)
        )

    async def _scrape_cursor_api_async() -> tuple[str, list[str]]:
        return (
            await asyncio.to_thread(_scrape_cursor_api)
            if hasattr(asyncio, "to_thread")
            else await asyncio.get_event_loop().run_in_executor(None, _scrape_cursor_api)
        )

    async def _scrape_copilot_async() -> tuple[str, list[str]]:
        return (
            await asyncio.to_thread(_scrape_copilot)
            if hasattr(asyncio, "to_thread")
            else await asyncio.get_event_loop().run_in_executor(None, _scrape_copilot)
        )

    async def _scrape_gemini_async() -> tuple[str, list[str]]:
        return (
            await asyncio.to_thread(_scrape_gemini)
            if hasattr(asyncio, "to_thread")
            else await asyncio.get_event_loop().run_in_executor(None, _scrape_gemini)
        )

    async def _scrape_claude_async() -> tuple[str, list[str]]:
        return (
            await asyncio.to_thread(_scrape_claude)
            if hasattr(asyncio, "to_thread")
            else await asyncio.get_event_loop().run_in_executor(None, _scrape_claude)
        )

    async def _scrape_ante_async() -> tuple[str, list[str]]:
        return (
            await asyncio.to_thread(_scrape_ante)
            if hasattr(asyncio, "to_thread")
            else await asyncio.get_event_loop().run_in_executor(None, _scrape_ante)
        )

    # OPT-005: Parallel execution with asyncio.gather
    results = await asyncio.gather(
        _scrape_cursor_async(),
        _scrape_cursor_api_async(),
        _scrape_copilot_async(),
        _scrape_gemini_async(),
        _scrape_claude_async(),
        _scrape_ante_async(),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, BaseException):
            continue
        provider, models = result
        by_provider[provider] = models

    # Get cursor models for codex extraction
    cursor_models = by_provider.get("cursor-agent", [])

    # Codex (from cursor)
    try:
        codex_models = [m for m in cursor_models if "codex" in m.lower() or "gpt" in m]
        filtered_codex = filter_models_for_provider("codex", codex_models) if codex_models else []
        by_provider["codex"] = filtered_codex or [settings.default_codex_model]
    except Exception:
        by_provider["codex"] = [settings.default_codex_model]

    # Proxy (antigravity, minimax, glm) - SA5
    try:
        filtered_antigravity = filter_models_for_provider("antigravity", proxy_result.get("antigravity", []))
        by_provider["antigravity"] = filtered_antigravity or [settings.default_antigravity_model]
        by_provider["minimax"] = proxy_result.get("minimax", []) or scrape_minimax_from_proxy()
        by_provider["glm"] = proxy_result.get("glm", []) or ["glm-5"]
        by_provider["roo"] = proxy_result.get("roo", []) or ["roo-v1"]
        by_provider["kilo"] = proxy_result.get("kilo", []) or ["kilo-v1"]
    except Exception:
        by_provider["antigravity"] = [settings.default_antigravity_model]
        by_provider["minimax"] = scrape_minimax_from_proxy()
        by_provider["glm"] = ["glm-5"]

    return by_provider
