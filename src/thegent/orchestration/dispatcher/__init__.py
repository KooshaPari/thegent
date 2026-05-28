"""Stub module for thegent.orchestration.dispatcher.

This module provides dispatching capabilities for sub-agents and task distribution.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass
class DispatchConfig:
    timeout_s: float = 30.0
    retry_count: int = 3
    priority: int = 0
    metadata: Optional[dict[str, Any]] = None
    max_concurrent: int = 1
    hitl_enabled: bool = False

    def __init__(self, **kwargs):
        self.timeout_s = kwargs.get('timeout_s', 30.0)
        self.retry_count = kwargs.get('retry_count', 3)
        self.priority = kwargs.get('priority', 0)
        self.metadata = kwargs.get('metadata')
        self.max_concurrent = kwargs.get('max_concurrent', 1)
        self.hitl_enabled = kwargs.get('hitl_enabled', False)
        for k, v in kwargs.items():
            if not hasattr(self, k):
                setattr(self, k, v)


@dataclass
class DispatchResult:
    """Result of a dispatch operation."""
    success: bool
    task_id: str = ""
    error: str = ""
    result: Any = None


__all__ = ["DispatchConfig", "DispatchResult", "SubAgentDispatcher"]


class SubAgentDispatcher:
    """Dispatcher for sub-agents."""

    def __init__(
        self,
        registry: Any = None,
        hitl_approval: bool = False,
        runner: Any = None,
        policy_engine: Any = None,
        config: Optional[DispatchConfig] = None,
        **kwargs,
    ) -> None:
        self.agents: dict = {}
        self.registry = registry
        self.hitl_approval = hitl_approval
        self.runner = runner
        self.policy_engine = policy_engine
        self.config = config or DispatchConfig()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._running = False

    def start(self) -> None:
        """Start the dispatcher."""
        self._running = True

    def stop(self) -> None:
        """Stop the dispatcher."""
        self._running = False

    def dispatch(self, task: str, context: dict | None = None, config: DispatchConfig | None = None) -> DispatchResult:
        """Dispatch a task to a sub-agent.

        Args:
            task: Task identifier or description.
            context: Optional execution context.
            config: Optional dispatch configuration.

        Returns:
            DispatchResult with success status and details.
        """
        cfg = config or DispatchConfig()
        return DispatchResult(success=True, task_id=task)

    async def execute_task(self, task: Any, config: DispatchConfig) -> tuple[str, bool, Optional[str]]:
        """Execute a task with given config.

        Args:
            task: Task to execute (string or node object).
            config: Dispatch configuration.

        Returns:
            Tuple of (output, success, error).
        """
        # Check HITL policy if enabled
        if self.hitl_approval or (config and getattr(config, 'hitl_enabled', False)):
            # Check if approval is required (task could be a node or string)
            node_for_check = task if hasattr(task, 'metadata') else type('obj', (object,), {'metadata': getattr(task, 'metadata', {})})()
            result = await self._check_hitl_gate(node_for_check, config)
            if result is not None:
                return result

        if self.runner is None:
            return ("", False, "No runner configured")

        try:
            result = await self.runner(task)
            return (str(result), True, None)
        except Exception as e:
            return ("", False, str(e))

    async def _execute_task(self, node: Any, runner_name: str | None = None) -> tuple[str, bool, Optional[str]]:
        """Internal method to execute a task.

        Args:
            node: Node/task to execute (has id, task, metadata).
            runner_name: Name of runner to use.

        Returns:
            Tuple of (output, success, error).
        """
        # Check HITL gate first (before runner lookup)
        if getattr(node, 'metadata', {}).get('require_approval'):
            try:
                result = await self._check_hitl_gate(node, self.config)
                if result is not None:
                    return result
            except RuntimeError:
                raise  # Re-raise HITL errors

        # Get runner from registry if not set
        runner = self.runner
        if runner is None and runner_name:
            try:
                from thegent.agents.registry import get_runner
                runner = get_runner(node)
            except Exception:
                return ("", False, f"No runner resolved for node {node.id}")

        if runner is None:
            return ("", False, f"No runner resolved for node {node.id}")

        try:
            if hasattr(runner, 'run'):
                result = runner.run(task=node.task, **getattr(node, 'metadata', {}))
            else:
                result = runner(node.task)
            if asyncio.iscoroutine(result):
                result = await result

            if hasattr(result, 'exit_code'):
                if result.exit_code == 0:
                    return (result.stdout or "", True, None)
                else:
                    return ("", False, result.stderr or "Task failed")
            return (str(result), True, None)
        except Exception as e:
            return ("", False, f"{type(e).__name__}: {str(e)}")

    async def _check_hitl_gate(self, node: Any, config: Any) -> Optional[tuple[str, bool, Optional[str]]]:
        """Check HITL approval gate.

        Args:
            node: Node with metadata.
            config: Dispatch configuration.

        Returns:
            Tuple if blocked, None if allowed.
        """
        metadata = getattr(node, 'metadata', {})

        if not metadata.get('require_approval'):
            return None

        if metadata.get('approval_granted', False):
            return None

        # Check with policy engine if available
        if self.policy_engine and hasattr(self.policy_engine, 'await_approval'):
            result = self.policy_engine.await_approval(node=node, config=config)
            if result is None:
                raise RuntimeError(f"HITL approval required for node {getattr(node, 'id', 'unknown')}")

        # No policy engine - just raise
        raise RuntimeError(f"HITL approval required for node {getattr(node, 'id', 'unknown')}")
