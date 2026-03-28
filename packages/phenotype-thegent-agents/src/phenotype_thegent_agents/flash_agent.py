"""Flash agent — ultra-short-lived agent that executes a single focused task and self-terminates.

Ported from the dex flash agent pattern. A FlashAgent fires a single LLM call via litellm,
enforces a strict timeout, and returns a structured result. Designed for sub-30-second
focused tasks without persistent state.

FR Traceability: FR-AGT-020 (flash agent lifecycle)
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass

import litellm


@dataclass
class FlashAgentConfig:
    """Configuration for a flash agent execution."""

    task_prompt: str
    model: str = "claude-haiku-4.5"
    timeout_s: float = 30.0
    max_tokens: int = 1024
    capture_output: bool = True


@dataclass
class FlashAgentResult:
    """Result of a flash agent execution."""

    output: str
    success: bool
    elapsed_s: float
    agent_id: str


class FlashAgent:
    """Ultra-short-lived agent that executes a single focused task via a single LLM call.

    Designed for sub-30-second focused tasks. Fires one litellm.acompletion call,
    enforces timeout via asyncio.wait_for, and self-terminates.
    """

    async def run(self, config: FlashAgentConfig) -> FlashAgentResult:
        """Execute a single LLM call and return the result.

        Args:
            config: FlashAgentConfig describing the task, model, timeout, and capture settings.

        Returns:
            FlashAgentResult with output, success flag, elapsed time, and unique agent ID.
        """
        agent_id = uuid.uuid4().hex[:8]
        start = time.monotonic()

        async def _call() -> str:
            response = await litellm.acompletion(
                model=config.model,
                messages=[{"role": "user", "content": config.task_prompt}],
                max_tokens=config.max_tokens,
            )
            choices = getattr(response, "choices", [])
            if not choices:
                return ""
            message = getattr(choices[0], "message", None)
            content = getattr(message, "content", "") or ""
            return str(content)

        try:
            output = await asyncio.wait_for(_call(), timeout=config.timeout_s)
            elapsed_s = time.monotonic() - start
            return FlashAgentResult(
                output=output,
                success=True,
                elapsed_s=elapsed_s,
                agent_id=agent_id,
            )
        except asyncio.TimeoutError:
            elapsed_s = time.monotonic() - start
            return FlashAgentResult(
                output="",
                success=False,
                elapsed_s=elapsed_s,
                agent_id=agent_id,
            )


async def flash(
    prompt: str,
    model: str = "claude-haiku-4.5",
    timeout_s: float = 30.0,
) -> FlashAgentResult:
    """Convenience function to run a flash agent with a single prompt.

    Args:
        prompt: The task prompt to execute.
        model: LLM model identifier (default: claude-haiku-4.5).
        timeout_s: Maximum execution time in seconds (default: 30.0).

    Returns:
        FlashAgentResult with output, success, elapsed time, and agent ID.

    Example::

        result = await flash("Summarize the Pythagorean theorem in one sentence.")
        if result.success:
            print(result.output)
    """
    config = FlashAgentConfig(task_prompt=prompt, model=model, timeout_s=timeout_s)
    agent = FlashAgent()
    return await agent.run(config)
