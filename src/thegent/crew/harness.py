"""Integration with thegent codex/cc/droid harness."""

from pathlib import Path
from typing import Any

from thegent.agents.direct_agents import DirectAgentRunner
from thegent.crew.executor import ExecutionResult


def create_agent_executor(
    cwd: Path | None = None,
    mode: str = "write",
    timeout: int = 300,
    model: str | None = None,
) -> callable:
    """
    Create agent_executor callback that uses thegent's codex/cc/droid harness.

    Args:
        cwd: Working directory for agent execution
        mode: Execution mode (read-only, write, full)
        timeout: Timeout in seconds
        model: Optional model override

    Returns:
        Callable (agent_id, prompt, context) -> ExecutionResult
    """

    def agent_executor(agent_id: str, prompt: str, context: dict[str, Any]) -> ExecutionResult:
        """
        Execute agent via thegent harness.

        Args:
            agent_id: Agent identifier (e.g., "codex", "cursor-agent", "claude", "copilot", "gemini", "droid")
            prompt: Task prompt
            context: Execution context

        Returns:
            ExecutionResult
        """
        # Map agent_id to agent name
        agent_name_map: dict[str, str] = {
            "codex": "codex",
            "cursor": "cursor-agent",
            "cursor-agent": "cursor-agent",
            "claude": "claude",
            "copilot": "copilot",
            "gemini": "gemini",
            "droid": "opencode",  # droid uses opencode CLI
        }

        agent_name = agent_name_map.get(agent_id.lower(), agent_id.lower())

        # Use model from context or default
        use_model = context.get("model") or model

        try:
            # Create agent runner
            runner = DirectAgentRunner(agent_name)

            # Execute agent
            result = runner.run(
                prompt=prompt,
                cwd=cwd,
                mode=mode,
                timeout=timeout,
                use_stream=True,
                live_output=False,
            )

            # Convert RunResult to ExecutionResult
            success = result.exit_code == 0 and not result.timed_out

            # Extract tokens/cost from result if available
            # (thegent agents may include this in stdout/stderr)
            tokens_used = 0
            cost_usd = 0.0

            # Try to parse cost info from output
            # This is a placeholder - actual parsing would depend on agent output format
            if "tokens" in result.stdout.lower():
                # Parse tokens if available
                pass

            return ExecutionResult(
                task_id=context.get("task_id", ""),
                success=success,
                result=result.stdout if success else None,
                error=result.stderr if not success else None,
                duration_seconds=timeout if result.timed_out else 0.0,  # Would need actual timing
                tokens_used=tokens_used,
                cost_usd=cost_usd,
            )

        except Exception as e:
            return ExecutionResult(
                task_id=context.get("task_id", ""),
                success=False,
                error=str(e),
                duration_seconds=0.0,
                tokens_used=0,
                cost_usd=0.0,
            )

    return agent_executor
