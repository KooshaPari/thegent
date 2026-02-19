"""ACP server adapter for exposing thegent agents via ACP protocol."""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from thegent.agents.base import AgentRunner
from thegent.agents.registry import AGENT_NAMES, get_runner

logger = logging.getLogger(__name__)

class AgentSession:
    """Represents an active agent session."""

    def __init__(self, agent_id: str, runner, cwd=None) -> None:
        """Initialize agent session."""
        self.agent_id = agent_id
        self.runner = runner
        self.cwd = cwd
        self.conversation_history = []
        self.is_running = False
        self._stop_event = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def stop(self) -> None:
        """Stop the session."""
        self.is_running = False
        if self._stop_event:
            self._stop_event.set()


class AgentSession:
    """Represents an active agent session."""

    def __init__(self, agent_id: str, runner: AgentRunner, cwd: Path | None = None) -> None:
        """Initialize agent session."""
        self.agent_id = agent_id
        self.runner = runner
        self.cwd = cwd
        self.conversation_history: list[dict[str, Any]] = []
        self.is_running = False
        self._stop_event = asyncio.Event()

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def stop(self) -> None:
        """Stop the session."""
        self.is_running = False
        self._stop_event.set()


class ACPServerAdapter:
    """Exposes thegent agents via ACP protocol (JSON-RPC over stdio)."""

    def __init__(self) -> None:
        """Initialize ACP server adapter."""
        self.agents: dict[str, AgentRunner] = {}
        self.sessions: dict[str, AgentSession] = {}
        self.sessions: dict[str, AgentSession] = {}
        self._load_agents()

    def _load_agents(self) -> None:
        """Load available thegent agents from registry."""
        # Load all agents from AGENT_NAMES registry
        for agent_name in AGENT_NAMES:
            try:
                runner = get_runner(agent_name, default_model="")
                if runner:
                    self.agents[agent_name] = runner
                    logger.debug(f"Loaded agent: {agent_name}")
            except Exception as e:
                logger.warning(f"Failed to load agent {agent_name}: {e}")

        if not self.agents:
            logger.warning("No agents loaded from registry, falling back to common agents")
            # Fallback to common agents if registry loading failed
            common_agents = ["claude", "codex", "copilot", "gemini", "opencode"]
            for agent_name in common_agents:
                runner = get_runner(agent_name, default_model="")
                if runner:
                    self.agents[agent_name] = runner

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle ACP JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return await self._handle_initialize(params)
        if method == "agent/spawn":
            return await self._handle_spawn(params)
        if method == "agent/message":
            return await self._handle_message(params)
        if method == "agent/stop":
            return await self._handle_stop(params)
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
        }

    async def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle ACP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": params.get("id", 1),
            "result": {
                "capabilities": {
                    "agents": list(self.agents.keys()),
                },
            },
        }

    async def _handle_spawn(self, params: dict[str, Any]) -> dict[str, Any]:
        """Spawn a thegent agent via ACP."""
        agent_name = params.get("agent", "claude")
        prompt = params.get("prompt", "")
        cwd_str = params.get("cwd")

        runner = self.agents.get(agent_name)
        if not runner:
            # Try to get from registry
            runner = get_runner(agent_name, default_model="")
            if runner:
                self.agents[agent_name] = runner

        if not runner:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 2),
                "error": {
                    "code": -32602,
                    "message": f"Agent '{agent_name}' not found. Available: {list(self.agents.keys())}",
                },
            }

        # Create session
        cwd = Path(cwd_str) if cwd_str else None
        agent_id = f"thegent-{agent_name}-{len(self.sessions)}"
        session = AgentSession(agent_id, runner, cwd)
        self.sessions[agent_id] = session
        
        if prompt:
            session.add_message("user", prompt)

        # Run agent asynchronously in executor to avoid blocking
        loop = asyncio.get_event_loop()
        session.is_running = True
        
        try:
            result = await loop.run_in_executor(
                None,
                lambda: runner.run(
                    prompt=prompt,
                    cwd=cwd,
                    mode="default",
                    timeout=3600,
                    use_stream=True,
                ),
            )
            
            if result.stdout:
                session.add_message("assistant", result.stdout)
        except Exception as e:
            logger.error(f"Error running agent {agent_name}: {e}", exc_info=True)
            session.is_running = False
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 2),
                "error": {
                    "code": -32603,
                    "message": f"Agent execution failed: {e}",
                },
            }
        finally:
            session.is_running = False

        # Convert RunResult to ACP response
        return {
            "jsonrpc": "2.0",
            "id": params.get("id", 2),
            "result": {
                "agent_id": agent_id,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
            },
        }

    async def _handle_message(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle message to existing agent session."""
        agent_id = params.get("agent_id")
        message = params.get("message", "")

        if not agent_id:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 3),
                "error": {
                    "code": -32602,
                    "message": "agent_id parameter required",
                },
            }

        session = self.sessions.get(agent_id)
        if not session:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 3),
                "error": {
                    "code": -32602,
                    "message": f"Session '{agent_id}' not found",
                },
            }

        # Add user message to conversation history
        session.add_message("user", message)

        # Build context from conversation history
        context_prompt = "\n\n".join(
            f"{msg['role']}: {msg['content']}" for msg in session.conversation_history
        )

        # Run agent asynchronously
        loop = asyncio.get_event_loop()
        session.is_running = True

        try:
            result = await loop.run_in_executor(
                None,
                lambda: session.runner.run(
                    prompt=context_prompt,
                    cwd=session.cwd,
                    mode="default",
                    timeout=3600,
                    use_stream=True,
                ),
            )

            if result.stdout:
                session.add_message("assistant", result.stdout)
        except Exception as e:
            logger.error(f"Error in session {agent_id}: {e}", exc_info=True)
            session.is_running = False
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 3),
                "error": {
                    "code": -32603,
                    "message": f"Agent execution failed: {e}",
                },
            }
        finally:
            session.is_running = False

        return {
            "jsonrpc": "2.0",
            "id": params.get("id", 3),
            "result": {
                "agent_id": agent_id,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
            },
        }

    async def _handle_stop(self, params: dict[str, Any]) -> dict[str, Any]:
        """Stop an agent session."""
        agent_id = params.get("agent_id")

        if not agent_id:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 4),
                "error": {
                    "code": -32602,
                    "message": "agent_id parameter required",
                },
            }

        session = self.sessions.get(agent_id)
        if not session:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id", 4),
                "error": {
                    "code": -32602,
                    "message": f"Session '{agent_id}' not found",
                },
            }

        # Stop the session
        session.stop()
        
        # Optionally remove from sessions dict (or keep for history)
        # For now, we keep it but mark as stopped

        return {
            "jsonrpc": "2.0",
            "id": params.get("id", 4),
            "result": {
                "stopped": True,
                "agent_id": agent_id,
            },
        }

    async def run_stdio(self) -> None:
        """Run ACP server over stdio (for local agents)."""
        logger.info("Starting ACP server adapter (stdio)")

        while True:
            try:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)
                response = await self.handle_request(request)

                # Write JSON-RPC response to stdout

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON-RPC request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
            except Exception as e:
                logger.error(f"Error handling request: {e}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {e}"},
                }


async def main() -> None:
    """Entry point for ACP server."""
    adapter = ACPServerAdapter()
    await adapter.run_stdio()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
