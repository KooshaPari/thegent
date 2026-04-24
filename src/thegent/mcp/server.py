"""MCP server implementation for thegent.

This module implements the Model Context Protocol server, exposing
thegent task execution and agent management via MCP tools.

Architecture:
- Depends on thegent.execution (injected executor)
- Depends on thegent.core (port interfaces)
- NO CLI imports (clean separation of concerns)
"""

from __future__ import annotations

import json
import logging
from typing import Any

_logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server adapter for thegent execution.

    Implements the Model Context Protocol by wrapping the execution
    layer and exposing it as MCP tools. Uses dependency injection
    to receive the executor, avoiding circular imports.

    Attributes:
        executor: The execution engine (injected).
        logger: Logger interface (injected).
    """

    def __init__(
        self,
        executor: Any = None,
        logger: Any = None,
        agent_registry: Any = None,
        model_registry: Any = None,
    ) -> None:
        """Initialize the MCP server.

        Args:
            executor: Executor instance (thegent.execution.Executor).
                      If None, lazy-loaded from CLI on first use.
            logger: Logger interface (thegent.core.ports.LoggerInterface).
            agent_registry: Agent registry (thegent.agents.AgentRegistry).
            model_registry: Model registry (thegent.models.ModelRegistry).
        """
        self._executor = executor
        self._logger = logger or _create_default_logger()
        self._agent_registry = agent_registry
        self._model_registry = model_registry

    def _ensure_executor(self) -> Any:
        """Lazy-load executor if not provided (for standalone usage)."""
        if self._executor is None:
            try:
                from thegent.execution import Executor
                self._executor = Executor()
                self._logger.info("Lazy-loaded executor for MCP server")
            except ImportError as e:
                raise RuntimeError(
                    "MCPServer requires executor; either pass it to __init__ "
                    "or ensure thegent.execution is importable"
                ) from e
        return self._executor

    def run_task(
        self,
        prompt: str,
        agent: str | None = None,
        model: str | None = None,
        timeout: int = 300,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """MCP tool: Execute a task.

        Args:
            prompt: Task description.
            agent: Agent name (optional).
            model: Model override (optional).
            timeout: Execution timeout in seconds.
            **kwargs: Additional execution parameters.

        Returns:
            Result dict with 'output', 'status', and metadata.
        """
        executor = self._ensure_executor()
        try:
            self._logger.debug(
                "MCP run_task: prompt=%s, agent=%s, model=%s",
                prompt[:50],
                agent,
                model,
            )

            # Build execution spec
            spec = {
                "prompt": prompt,
                "agent": agent,
                "model": model,
                "timeout": timeout,
                **kwargs,
            }

            # Execute via executor (no CLI imports here)
            result = executor.run(spec)

            # Format result for MCP
            return {
                "status": "success",
                "output": str(result),
                "metadata": {
                    "agent": agent,
                    "model": model,
                    "timeout": timeout,
                },
            }
        except Exception as e:
            self._logger.exception("MCP run_task failed: %s", e)
            return {
                "status": "error",
                "output": str(e),
                "error": type(e).__name__,
            }

    def list_agents(self) -> dict[str, Any]:
        """MCP tool: List available agents.

        Returns:
            Dict with 'agents' list and metadata.
        """
        try:
            if self._agent_registry is None:
                self._logger.warning("No agent registry provided to MCP server")
                return {"status": "success", "agents": []}

            agents = self._agent_registry.list_all()
            return {
                "status": "success",
                "agents": agents,
                "count": len(agents),
            }
        except Exception as e:
            self._logger.exception("MCP list_agents failed: %s", e)
            return {"status": "error", "error": str(e)}

    def list_models(self) -> dict[str, Any]:
        """MCP tool: List available models.

        Returns:
            Dict with 'models' list and metadata.
        """
        try:
            if self._model_registry is None:
                self._logger.warning("No model registry provided to MCP server")
                return {"status": "success", "models": []}

            models = self._model_registry.list_all()
            return {
                "status": "success",
                "models": models,
                "count": len(models),
            }
        except Exception as e:
            self._logger.exception("MCP list_models failed: %s", e)
            return {"status": "error", "error": str(e)}

    def get_status(self) -> dict[str, Any]:
        """MCP tool: Get server and executor status.

        Returns:
            Status dict with health information.
        """
        try:
            executor = self._ensure_executor()
            return {
                "status": "healthy",
                "executor": "ready",
                "agents": self._agent_registry is not None,
                "models": self._model_registry is not None,
            }
        except Exception as e:
            self._logger.exception("MCP get_status failed: %s", e)
            return {"status": "unhealthy", "error": str(e)}


def _create_default_logger() -> Any:
    """Create a default logger interface if none provided."""

    class SimpleLogger:
        """Minimal logger implementation."""

        def debug(self, msg: str, *args: Any) -> None:
            _logger.debug(msg, *args)

        def info(self, msg: str, *args: Any) -> None:
            _logger.info(msg, *args)

        def warning(self, msg: str, *args: Any) -> None:
            _logger.warning(msg, *args)

        def error(self, msg: str, *args: Any) -> None:
            _logger.error(msg, *args)

        def exception(self, msg: str, *args: Any) -> None:
            _logger.exception(msg, *args)

    return SimpleLogger()


__all__ = ["MCPServer"]
