"""Model scrapers for dynamic discovery."""

import contextlib
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Protocol

from thegent.config import ThegentSettings


class ModelScraper(Protocol):
    """Protocol for provider-specific model scrapers (Phase 12). Returns model IDs."""

    def __call__(self, settings: ThegentSettings | None = None) -> list[str]:
        """Scrape models for this provider. Returns model IDs."""
        ...


_CACHE_PATH = Path.home() / ".cache" / "thegent" / "models-cache.json"


def get_models_cache_path() -> Path:
    """Return path to models cache file (for invalidation)."""
    return _CACHE_PATH


def invalidate_models_cache() -> bool:
    """Delete models cache file. Returns True if file existed and was removed."""
    if _CACHE_PATH.exists():
        try:
            _CACHE_PATH.unlink()
            return True
        except OSError:
            return False
    return False


def _load_cached(ttl_sec: int = 300) -> tuple[dict[str, list[str]], float] | None:
    """Load cached scrape result. Returns (by_provider, mtime) or None if expired/missing."""
    if not _CACHE_PATH.exists():
        return None
    try:
        data = json.loads(_CACHE_PATH.read_text())
        by_provider = data.get("by_provider", {})
        mtime = data.get("mtime", 0)
        if time.time() - mtime > ttl_sec:
            return None
        return (by_provider, mtime)
    except (json.JSONDecodeError, OSError):
        return None


def _save_cache(by_provider: dict[str, list[str]]) -> None:
    """Save scrape result to cache."""
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(
        json.dumps({"by_provider": by_provider, "mtime": time.time()}, indent=0),
        encoding="utf-8",
    )


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
        _save_cache(result)
    return result


_PROXY_CHECK_TIMEOUT = 3


def _scrape_proxy_models(base_url: str) -> list[str]:
    """Fetch model IDs from proxy GET /v1/models (OpenAI-compatible)."""
    models: list[str] = []
    url = f"{base_url.rstrip('/')}/v1/models"
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": "Bearer sk-dummy"},
        )
        with urllib.request.urlopen(req, timeout=_PROXY_CHECK_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
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
        proc = subprocess.run(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return [l.strip() for l in proc.stdout.splitlines() if l.strip() and not l.strip().startswith("Tip:")]
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
        req = urllib.request.Request(url, method="GET")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=_PROXY_CHECK_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
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
        proc = subprocess.run(
            ["copilot", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
        if proc.returncode == 0 and "--model" in proc.stdout:
            start = proc.stdout.find("--model")
            chunk = proc.stdout[start : start + 600] if start >= 0 else ""
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
        try:
            proc = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=4,
            )
            if proc.returncode == 0 and proc.stdout:
                matches = re.findall(r"gemini-[a-zA-Z0-9.-]+", proc.stdout)
                if matches:
                    return list(dict.fromkeys(matches))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return fallback


def scrape_claude() -> list[str]:
    """Scrape claude models: try 'claude models list', else --help for --model aliases."""
    fallback = ["haiku", "sonnet", "opus", "claude-haiku-4.5", "claude-sonnet-4.5", "claude-opus-4.6"]
    for cmd in [["claude", "models", "list"], ["claude", "list-models"], ["claude", "--help"]]:
        try:
            proc = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=4,
            )
            if proc.returncode == 0 and proc.stdout:
                out: list[str] = ["haiku", "sonnet", "opus"]
                matches = re.findall(r"claude-[a-zA-Z0-9.-]+", proc.stdout)
                for m in matches:
                    if m not in out:
                        out.append(m)
                if len(out) > 3:
                    return out
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return fallback


def scrape_minimax_from_proxy() -> list[str]:
    """MiniMax models from proxy (minimax: block in config). Fallback to static."""
    return ["minimax-m2.5"]


# Registry: provider -> scraper callable (settings) -> list[str]. Phase 12.
# SA2: gemini, SA3: claude, SA4: cursor/copilot, SA5: antigravity/minimax/glm (via scrape_proxy in scrape_all)
SCRAPER_REGISTRY: dict[str, ModelScraper] = {
    "cursor-agent": lambda settings=None: scrape_cursor(),
    "copilot": lambda settings=None: scrape_copilot(),
    "gemini": lambda settings=None: scrape_gemini(),
    "claude": lambda settings=None: scrape_claude(),
}


def scrape_all(settings: ThegentSettings | None = None) -> dict[str, list[str]]:
    """
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

    # Cursor (CLI) - SA4
    cursor_models: list[str] = []
    try:
        cursor_models = scrape_cursor()
        filtered_cursor = filter_models_for_provider("cursor-agent", cursor_models) if cursor_models else []
        by_provider["cursor-agent"] = filtered_cursor or [settings.default_cursor_model]
    except Exception:
        by_provider["cursor-agent"] = [settings.default_cursor_model]

    # Cursor-api (wisdgod HTTP)
    try:
        cursor_api_models = scrape_cursor_api(settings)
        filtered_cursor_api = filter_models_for_provider("cursor-api", cursor_api_models) if cursor_api_models else []
        by_provider["cursor-api"] = filtered_cursor_api or [
            "claude-4.5-opus-high-thinking",
            "gpt-5.1-codex",
            "claude-4.5-sonnet-thinking",
        ]
    except Exception:
        by_provider["cursor-api"] = ["claude-4.5-opus-high-thinking", "gpt-5.1-codex", "claude-4.5-sonnet-thinking"]

    # Copilot - SA4
    try:
        copilot_models = scrape_copilot()
        filtered_copilot = filter_models_for_provider("copilot", copilot_models) if copilot_models else []
        by_provider["copilot"] = filtered_copilot or [settings.default_copilot_model]
    except Exception:
        by_provider["copilot"] = [settings.default_copilot_model]

    # Gemini - SA2
    try:
        gemini_models = scrape_gemini()
        proxy_gemini = proxy_result.get("gemini", [])
        combined_gemini = list(dict.fromkeys(gemini_models + proxy_gemini))
        filtered_gemini = filter_models_for_provider("gemini", combined_gemini) if combined_gemini else []
        by_provider["gemini"] = filtered_gemini or [settings.default_gemini_model]
    except Exception:
        by_provider["gemini"] = [settings.default_gemini_model]

    # Claude - SA3
    try:
        claude_models = scrape_claude()
        proxy_claude = proxy_result.get("claude", [])
        combined_claude = list(dict.fromkeys(claude_models + proxy_claude))
        filtered_claude = filter_models_for_provider("claude", combined_claude) if combined_claude else []
        by_provider["claude"] = filtered_claude or [settings.default_claude_model]
    except Exception:
        by_provider["claude"] = [settings.default_claude_model]

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
