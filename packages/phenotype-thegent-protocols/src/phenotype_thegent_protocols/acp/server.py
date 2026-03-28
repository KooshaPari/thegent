"""ACP server adapter for exposing thegent agents via ACP protocol."""

import asyncio
from phenotype_thegent_core.utils.json_utils import json_dumps, json_loads
import logging
import sys
from pathlib import Path
from typing import Any

from phenotype_thegent_agents.agents.base import AgentRunner
from phenotype_thegent_agents.agents.registry import AGENT_NAMES, get_runner

logger = logging.getLogger(__name__)


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
        self._load_agents()

    def _load_agents(self) -> None:
        """Load available thegent agents from registry."""
        for agent_name in AGENT_NAMES:
            self._load_agent(agent_name)

        if not self.agents:
            logger.warning("No agents loaded from registry, falling back to common agents")
            common_agents = ["claude", "codex", "copilot", "gemini", "opencode"]
            for agent_name in common_agents:
                self._load_agent(agent_name)

    def _load_agent(self, agent_name: str) -> None:
        """Load a single agent from the registry."""
        try:
            runner = get_runner(agent_name)
            if runner:
                self.agents[agent_name] = runner
                logger.debug("Loaded agent: %s", agent_name)
        except Exception as e:
            logger.warning("Failed to load agent %s: %s", agent_name, e)

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle ACP JSON-RPC request.

        Args:
            request: JSON-RPC request dict with method, params, and optional id.

        Returns:
            JSON-RPC response dict.
        """
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "initialize":
            return await self._handle_initialize(req_id, params)
        if method == "agent/spawn":
            return await self._handle_spawn(req_id, params)
        if method == "agent/message":
            return await self._handle_message(req_id, params)
        if method == "agent/stop":
            return await self._handle_stop(req_id, params)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
        }

    async def _handle_initialize(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Handle ACP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "capabilities": {
                    "agents": list(self.agents.keys()),
                },
            },
        }

    async def _handle_spawn(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Spawn a thegent agent via ACP."""
        agent_name = params.get("agent", "claude")
        prompt = params.get("prompt", "")
        cwd_str = params.get("cwd")

        runner = self.agents.get(agent_name)
        if not runner:
            runner = get_runner(agent_name)
            if runner:
                self.agents[agent_name] = runner

        if not runner:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Agent '{agent_name}' not found. Available: {list(self.agents.keys())}",
                },
            }

        cwd = Path(cwd_str) if cwd_str else None
        agent_id = f"thegent-{agent_name}-{len(self.sessions)}"
        session = AgentSession(agent_id, runner, cwd)
        self.sessions[agent_id] = session

        if prompt:
            session.add_message("user", prompt)

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
            logger.error("Error running agent %s: %s", agent_name, e, exc_info=True)
            session.is_running = False
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Agent execution failed: {e}",
                },
            }
        finally:
            session.is_running = False

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "agent_id": agent_id,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
            },
        }

    async def _handle_message(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Handle message to existing agent session."""
        agent_id = params.get("agent_id")
        message = params.get("message", "")

        if not agent_id:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": "agent_id parameter required",
                },
            }

        session = self.sessions.get(agent_id)
        if not session:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Session '{agent_id}' not found",
                },
            }

        session.add_message("user", message)
        context_prompt = "\n\n".join(f"{msg['role']}: {msg['content']}" for msg in session.conversation_history)

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
            logger.error("Error in session %s: %s", agent_id, e, exc_info=True)
            session.is_running = False
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Agent execution failed: {e}",
                },
            }
        finally:
            session.is_running = False

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "agent_id": agent_id,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "timed_out": result.timed_out,
            },
        }

    async def _handle_stop(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Stop an agent session."""
        agent_id = params.get("agent_id")

        if not agent_id:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": "agent_id parameter required",
                },
            }

        session = self.sessions.get(agent_id)
        if not session:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Session '{agent_id}' not found",
                },
            }

        session.stop()

        return {
            "jsonrpc": "2.0",
            "id": req_id,
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
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json_loads(line)
                response = await self.handle_request(request)
                sys.stdout.write(json_dumps(response) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error("Invalid JSON-RPC request: %s", e)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
                sys.stdout.write(json_dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                logger.error("Error handling request: %s", e, exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {e}"},
                }
                sys.stdout.write(json_dumps(error_response) + "\n")
                sys.stdout.flush()


async def main() -> None:
    """Entry point for ACP server."""
    adapter = ACPServerAdapter()
    await adapter.run_stdio()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
