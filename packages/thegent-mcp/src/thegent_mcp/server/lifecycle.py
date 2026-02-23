"""Lifespan lifecycle for thegent MCP server."""

import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator
from typing import Any

from fastmcp import FastMCP

from thegent.config import ThegentSettings


def _js_executor_config(package: str) -> dict[str, Any]:
    """Build JS executor proxy config (prefer Bun, fallback to npx)."""
    import shutil

    bun = shutil.which("bun")
    if bun:
        return {"mcpServers": {"default": {"command": "bun", "args": ["x", package], "env": {**os.environ}}}}
    return {
        "mcpServers": {
            "default": {
                "command": "npx",
                "args": ["-y", "--no-install", package],
                "env": {**os.environ, "npm_config_update_notifier": "false"},
            }
        }
    }


async def run_lifespan(
    mcp_app: FastMCP,
    logger: logging.Logger,
    *,
    ps_impl: Any,
    auto_init_on_startup: Any,
) -> AsyncIterator[dict[str, Any] | None]:
    """Startup and teardown for thegent MCP server."""
    logger.info("thegent MCP server starting")

    try:
        from thegent.infra.runtime_init import initialize_runtime_infrastructure

        initialize_runtime_infrastructure()
        logger.info("Runtime infrastructure initialized")
    except Exception as e:
        logger.warning("Failed to initialize runtime infrastructure: %s", e)

    settings = ThegentSettings()
    try:
        settings.validate_setup()
        logger.info("Configuration validated successfully")
    except Exception as e:
        logger.critical("Configuration validation failed: %s", e)

    try:
        auto_init_on_startup()
        logger.info("IDE integrations auto-initialized")
    except Exception as e:
        logger.debug("IDE auto-init failed (non-critical): %s", e)

    mounts_enabled = (
        settings.mcp_mount_flyto
        or settings.mcp_mount_playwright
        or settings.mcp_mount_serena
        or settings.mcp_mount_octocode
        or settings.mcp_mount_sequential_thinking
        or settings.mcp_mount_next_devtools
    )
    if mounts_enabled:
        try:
            from fastmcp.server import create_proxy

            if settings.mcp_mount_flyto:
                flyto_url = settings.flyto_url
                proxy = create_proxy(flyto_url, name="flyto")
                mcp_app.mount(proxy, namespace="browser")
                logger.info("mounted flyto-core at namespace browser (url=%s)", flyto_url)
            elif settings.mcp_mount_playwright:
                proxy = create_proxy(_js_executor_config("@playwright/mcp@latest"), name="playwright")
                mcp_app.mount(proxy, namespace="browser")
                logger.info("mounted @playwright/mcp at namespace browser")

            if settings.mcp_mount_serena:
                from thegent.lsp.serena_integration import detect_serena_backend, get_serena_mcp_config

                backend = detect_serena_backend()
                _ = get_serena_mcp_config()
                if backend == "jetbrains":
                    logger.info("Using Serena JetBrains plugin backend (port %s)", settings.serena_jetbrains_port)
                else:
                    logger.info("Using Serena LSP backend")
                serena_config = {
                    "command": "uvx",
                    "args": [
                        "--from",
                        "git+https://github.com/oraios/serena",
                        "serena",
                        "start-mcp-server",
                        "--transport",
                        "sse",
                        "--port",
                        "3848",
                        "--context",
                        "ide",
                        "--project-from-cwd",
                        "--open-web-dashboard",
                        "false",
                    ],
                    "env": {},
                }
                proxy = create_proxy(serena_config, name="serena")
                mcp_app.mount(proxy, namespace="serena")
                logger.info("mounted Serena at namespace serena (backend: %s)", backend)

            if settings.mcp_mount_octocode:
                proxy = create_proxy(_js_executor_config("octocode-mcp@latest"), name="octocode")
                mcp_app.mount(proxy, namespace="octocode")
                logger.info("mounted Octocode at namespace octocode")

            if settings.mcp_mount_sequential_thinking:
                proxy = create_proxy(
                    _js_executor_config("@modelcontextprotocol/server-sequential-thinking"), name="thinking"
                )
                mcp_app.mount(proxy, namespace="thinking")
                logger.info("mounted Sequential Thinking at namespace thinking")

            if settings.mcp_mount_next_devtools:
                proxy = create_proxy(_js_executor_config("@next/devtools-mcp"), name="next")
                mcp_app.mount(proxy, namespace="next")
                logger.info("mounted Next DevTools at namespace next")
        except Exception as e:
            logger.warning("failed to mount provider: %s", e)

    try:
        pass
    except Exception as e:
        logger.warning("failed to pre-warm dependencies: %s", e)

    proxy_proc = None
    if settings.bundle_proxy:
        try:
            from thegent.agents.cliproxy_manager import start_proxy_managed

            proxy_proc, base_url = start_proxy_managed(ThegentSettings())
            if proxy_proc is not None:
                logger.info("started CLIProxyAPIPlus proxy at %s", base_url)
        except Exception as e:
            logger.warning("could not start bundled proxy: %s", e)

    try:
        yield {}
    finally:
        wait_s = settings.shutdown_wait_s
        if wait_s > 0:
            logger.info("shutdown wait %ds for in-flight requests", wait_s)
            await asyncio.sleep(wait_s)

        active_wait_s = settings.shutdown_wait_active_s
        if active_wait_s > 0:
            start = time.monotonic()
            poll_interval = 2.0
            while (time.monotonic() - start) < active_wait_s:
                try:
                    rows = await asyncio.to_thread(ps_impl, None, True, None)
                    running = [r for r in rows if (r.get("status") or "").lower() == "running"]
                    if not running:
                        logger.info("no active runs; shutdown proceeding")
                        break
                    logger.info("shutdown waiting for %d active run(s)", len(running))
                except Exception as e:
                    logger.warning("ps_impl during shutdown: %s", e)
                    break
                await asyncio.sleep(min(poll_interval, active_wait_s - (time.monotonic() - start)))
            else:
                logger.info("active-run wait timeout (%ds); proceeding with shutdown", active_wait_s)

        if proxy_proc is not None and proxy_proc.poll() is None:
            proxy_proc.terminate()
            try:
                proxy_proc.wait(timeout=5)
            except Exception:
                proxy_proc.kill()
            logger.info("stopped bundled proxy")

        try:
            from thegent.utils.routing_impl.litellm_responses_handler import close_http_client

            await close_http_client()
            logger.info("closed persistent HTTP client")
        except Exception as e:
            logger.warning("failed to close HTTP client: %s", e)

        logger.info("shutting down")
