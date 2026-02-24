"""ACP (Agent Communication Protocol) Server Adapter.

Wraps thegent agent capabilities as an ACP-compatible HTTP endpoint using
Starlette, consistent with the existing MCP server pattern.

ACP request format:
    {"type": "task", "payload": {...}, "agent_id": "..."}

ACP response format:
    {"type": "result", "result": {...}, "agent_id": "..."}

JSON-RPC methods supported (over HTTP POST /rpc and stdio):
    - initialize       -> server capabilities
    - agent/spawn      -> spawn an agent with a prompt, returns result
    - agent/message    -> send a follow-up message to an existing session
    - agent/stop       -> stop an active session
    - session/attach   -> attach to or create a named mux session
    - session/inspect  -> capture pane output from a mux session
    - session/send     -> send keystrokes to a mux session

Independently startable::

    python -m thegent.adapters.acp_server            # stdio
    python -m thegent.adapters.acp_server --http     # HTTP on port 8420

"""

from __future__ import annotations

import asyncio
import orjson as json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from thegent.agents.registry import AGENT_NAMES, get_runner
from thegent.session import resolve_session_backend

if TYPE_CHECKING:
    from starlette.requests import Request

    from thegent.agents.base import AgentRunner, RunResult
    from thegent.session.zmx_backend import SessionBackend, ZmxSession

logger = logging.getLogger(__name__)

# Default HTTP port for the ACP server adapter
ACP_DEFAULT_PORT: int = int(os.environ.get("ACP_SERVER_PORT", "8420"))
app = typer.Typer(
    name="acp-server",
    help="thegent ACP server adapter",
    add_completion=False,
    no_args_is_help=False,
)


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


class AgentSession:
    """Represents an active ACP agent session."""

    def __init__(self, session_id: str, runner: AgentRunner, cwd: Path | None = None) -> None:
        self.session_id = session_id
        self.runner = runner
        self.cwd = cwd
        self.conversation_history: list[dict[str, str]] = []
        self.is_running: bool = False
        self._stop_event: asyncio.Event = asyncio.Event()

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the session conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def stop(self) -> None:
        """Signal the session to stop."""
        self.is_running = False
        self._stop_event.set()


# ---------------------------------------------------------------------------
# Session endpoints helper
# ---------------------------------------------------------------------------


class SessionEndpoints:
    """Wraps session-backend calls for the session/* ACP RPC methods.

    Keeps session management logic separate from agent lifecycle logic for
    testability.  Callers should use :meth:`get_or_resolve_backend` rather
    than constructing a backend themselves so that the backend is shared and
    lazily resolved.

    # @trace FR-SES-001
    """

    def __init__(self, backend: SessionBackend | None = None) -> None:
        """Create a ``SessionEndpoints`` instance.

        Args:
            backend: Optional pre-constructed backend.  When *None* the backend
                is resolved lazily on first use via
                :func:`~thegent.session.resolve_session_backend`.
        """
        self._backend: SessionBackend | None = backend
        self._backend_resolved: bool = backend is not None

    # ------------------------------------------------------------------
    # Backend access
    # ------------------------------------------------------------------

    def get_or_resolve_backend(self) -> SessionBackend | None:
        """Return the session backend, resolving it lazily if needed."""
        if not self._backend_resolved:
            self._backend = resolve_session_backend()
            self._backend_resolved = True
        return self._backend

    # ------------------------------------------------------------------
    # session/attach
    # ------------------------------------------------------------------

    def attach(self, session_name: str) -> dict[str, str]:
        """Attach to *session_name*, creating it if it does not exist.

        Returns a dict with ``session_id`` (same as *session_name* for
        backend-managed sessions) and ``status`` (``"attached"`` or
        ``"created"``).

        # @trace FR-SES-001
        """
        backend = self.get_or_resolve_backend()
        if backend is None:
            return {"session_id": "", "status": "unavailable", "error": "No session backend available"}

        # Check whether the session already exists
        existing: list[ZmxSession] = backend.list()
        names = {s.name for s in existing}

        if session_name in names:
            return {"session_id": session_name, "status": "attached"}

        # Create a new session running a shell
        created = backend.create(session_name, ["/bin/sh"])
        if not created:
            return {"session_id": "", "status": "error", "error": f"Failed to create session '{session_name}'"}
        return {"session_id": session_name, "status": "created"}

    # ------------------------------------------------------------------
    # session/inspect
    # ------------------------------------------------------------------

    def inspect(self, session_id: str, last_lines: int = 50) -> dict[str, object]:
        """Capture *last_lines* lines of output from *session_id*.

        Returns a dict with ``lines`` (list[str]) and ``backend`` (str name).

        # @trace FR-SES-001
        """
        backend = self.get_or_resolve_backend()
        if backend is None:
            return {"lines": [], "backend": "none", "error": "No session backend available"}

        raw = backend.capture(session_id, last_lines)
        lines = raw.splitlines() if raw else []
        return {"lines": lines, "backend": backend.name}

    # ------------------------------------------------------------------
    # session/send
    # ------------------------------------------------------------------

    def send(self, session_id: str, text: str, *, enter: bool = False) -> dict[str, bool]:
        """Send *text* (and optionally a carriage return) to *session_id*.

        The send is implemented as ``zmx send-keys`` semantics: if *enter* is
        True, a newline character is appended.  Returns ``{"success": bool}``.

        # @trace FR-SES-001
        """
        backend = self.get_or_resolve_backend()
        if backend is None:
            return {"success": False}

        payload = text + ("\n" if enter else "")
        # ZmxBackend does not expose a send-keys method; we model it through
        # create+capture.  Backends that support send-keys should override via
        # a richer protocol.  For now we detect the method dynamically to stay
        # forward-compatible.
        send_fn = getattr(backend, "send_keys", None)
        if send_fn is not None:
            ok: bool = send_fn(session_id, payload)
        else:
            # Gracefully degrade: log the intent but report success=False so
            # callers know the send did not complete.
            logger.warning(
                "session/send: backend %r does not implement send_keys; text not delivered to %r",
                backend.name,
                session_id,
            )
            ok = False

        return {"success": ok}


# ---------------------------------------------------------------------------
# Core adapter logic
# ---------------------------------------------------------------------------


class ACPServerAdapter:
    """Wraps thegent agent capabilities as an ACP-compatible endpoint.

    Handles both simple task/result messages (native ACP format) and the
    JSON-RPC method envelope used by the stdio transport.

    ACP message flow:
        Client  ->  {"type": "task", "payload": {...}, "agent_id": "..."}
        Server  ->  {"type": "result", "result": {...}, "agent_id": "..."}
    """

    def __init__(self, session_endpoints: SessionEndpoints | None = None) -> None:
        self.agents: dict[str, AgentRunner] = {}
        self.sessions: dict[str, AgentSession] = {}
        self.session_endpoints: SessionEndpoints = session_endpoints or SessionEndpoints()
        self._load_agents()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _load_agents(self) -> None:
        """Populate agent registry from thegent agent names."""
        for name in AGENT_NAMES:
            self._load_agent(name)

        if not self.agents:
            logger.warning("Agent registry empty; no agents available")

    def _load_agent(self, name: str) -> None:
        """Load a single agent by name."""
        try:
            runner = get_runner(name)
            if runner is not None:
                self.agents[name] = runner
                logger.debug("Registered agent: %s", name)
        except Exception:
            logger.warning("Skipping agent %s (failed to load)", name, exc_info=True)

    # ------------------------------------------------------------------
    # Native ACP format: {"type": "task", "payload": {...}, "agent_id": "..."}
    # ------------------------------------------------------------------

    async def handle_acp_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a native ACP message and return an ACP response.

        Args:
            message: ACP message with keys ``type``, ``payload``, and
                optional ``agent_id``.

        Returns:
            ACP response dict with ``type``, ``result``, and ``agent_id``.
        """
        msg_type = message.get("type")
        payload = message.get("payload", {})
        caller_agent_id: str = message.get("agent_id", "")

        if msg_type != "task":
            return {
                "type": "error",
                "agent_id": caller_agent_id,
                "error": {"code": "UNSUPPORTED_TYPE", "message": f"Unsupported message type: {msg_type!r}"},
            }

        agent_name: str = payload.get("agent", "claude")
        prompt: str = payload.get("prompt", "")
        cwd_str: str | None = payload.get("cwd")

        runner = self._resolve_runner(agent_name)
        if runner is None:
            return {
                "type": "error",
                "agent_id": caller_agent_id,
                "error": {
                    "code": "AGENT_NOT_FOUND",
                    "message": f"Agent '{agent_name}' not found. Available: {sorted(self.agents)}",
                },
            }

        session_id = f"thegent-{agent_name}-{uuid.uuid4().hex[:8]}"
        cwd = Path(cwd_str) if cwd_str else None
        session = AgentSession(session_id, runner, cwd)
        self.sessions[session_id] = session

        if prompt:
            session.add_message("user", prompt)

        run_result = await self._run_agent(session, runner, prompt, cwd)
        if isinstance(run_result, dict):
            # Error dict from _run_agent
            return {"type": "error", "agent_id": session_id, **run_result}

        return {
            "type": "result",
            "agent_id": session_id,
            "result": {
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
                "exit_code": run_result.exit_code,
                "timed_out": run_result.timed_out,
            },
        }

    # ------------------------------------------------------------------
    # JSON-RPC envelope (used over stdio and /rpc HTTP endpoint)
    # ------------------------------------------------------------------

    async def handle_jsonrpc(self, request: dict[str, Any]) -> dict[str, Any]:
        """Dispatch a JSON-RPC 2.0 request.

        Supported methods: ``initialize``, ``agent/spawn``, ``agent/message``,
        ``agent/stop``, ``session/attach``, ``session/inspect``,
        ``session/send``.

        Args:
            request: JSON-RPC request with ``method``, optional ``params``
                and optional ``id``.

        Returns:
            JSON-RPC response dict.
        """
        method: str | None = request.get("method")
        params: dict[str, Any] = request.get("params") or {}
        req_id: Any = request.get("id")

        dispatch = {
            "initialize": self._rpc_initialize,
            "agent/spawn": self._rpc_spawn,
            "agent/message": self._rpc_message,
            "agent/stop": self._rpc_stop,
            "session/attach": self._rpc_session_attach,
            "session/inspect": self._rpc_session_inspect,
            "session/send": self._rpc_session_send,
        }

        handler = dispatch.get(method or "")
        if handler is None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }

        return await handler(req_id, params)

    # ------------------------------------------------------------------
    # JSON-RPC method handlers
    # ------------------------------------------------------------------

    async def _rpc_initialize(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "0.1",
                "capabilities": {
                    "agents": sorted(self.agents),
                    "methods": [
                        "initialize",
                        "agent/spawn",
                        "agent/message",
                        "agent/stop",
                        "session/attach",
                        "session/inspect",
                        "session/send",
                    ],
                },
            },
        }

    async def _rpc_spawn(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        agent_name: str = params.get("agent", "claude")
        prompt: str = params.get("prompt", "")
        cwd_str: str | None = params.get("cwd")

        runner = self._resolve_runner(agent_name)
        if runner is None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Agent '{agent_name}' not found. Available: {sorted(self.agents)}",
                },
            }

        cwd = Path(cwd_str) if cwd_str else None
        session_id = f"thegent-{agent_name}-{uuid.uuid4().hex[:8]}"
        session = AgentSession(session_id, runner, cwd)
        self.sessions[session_id] = session

        if prompt:
            session.add_message("user", prompt)

        run_result = await self._run_agent(session, runner, prompt, cwd)
        if isinstance(run_result, dict):
            return {"jsonrpc": "2.0", "id": req_id, "error": run_result.get("error", run_result)}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "agent_id": session_id,
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
                "exit_code": run_result.exit_code,
                "timed_out": run_result.timed_out,
            },
        }

    async def _rpc_message(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        session_id: str | None = params.get("agent_id")
        message: str = params.get("message", "")

        if not session_id:
            return _rpc_error(req_id, -32602, "agent_id parameter required")

        session = self.sessions.get(session_id)
        if session is None:
            return _rpc_error(req_id, -32602, f"Session '{session_id}' not found")

        session.add_message("user", message)
        context_prompt = "\n\n".join(f"{m['role']}: {m['content']}" for m in session.conversation_history)

        run_result = await self._run_agent(session, session.runner, context_prompt, session.cwd)
        if isinstance(run_result, dict):
            return {"jsonrpc": "2.0", "id": req_id, "error": run_result.get("error", run_result)}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "agent_id": session_id,
                "stdout": run_result.stdout,
                "stderr": run_result.stderr,
                "exit_code": run_result.exit_code,
                "timed_out": run_result.timed_out,
            },
        }

    async def _rpc_stop(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        session_id: str | None = params.get("agent_id")

        if not session_id:
            return _rpc_error(req_id, -32602, "agent_id parameter required")

        session = self.sessions.get(session_id)
        if session is None:
            return _rpc_error(req_id, -32602, f"Session '{session_id}' not found")

        session.stop()
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"stopped": True, "agent_id": session_id},
        }

    # ------------------------------------------------------------------
    # JSON-RPC session method handlers
    # ------------------------------------------------------------------

    async def _rpc_session_attach(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Handle ``session/attach``.

        Params:
            session_name (str): Name of the mux session to attach or create.

        Returns:
            ``{"session_id": str, "status": str}`` on success or JSON-RPC
            error on missing/invalid params.
        """
        session_name: str | None = params.get("session_name")
        if not session_name:
            return _rpc_error(req_id, -32602, "session_name parameter required")

        result = self.session_endpoints.attach(session_name)
        if result.get("status") == "error" or result.get("status") == "unavailable":
            error_msg = result.get("error", "Session attach failed")
            return _rpc_error(req_id, -32603, str(error_msg))

        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    async def _rpc_session_inspect(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Handle ``session/inspect``.

        Params:
            session_id (str): The session to inspect.
            last_lines (int, optional): Number of trailing lines to return
                (default 50).

        Returns:
            ``{"lines": [...], "backend": str}`` on success.
        """
        session_id: str | None = params.get("session_id")
        if not session_id:
            return _rpc_error(req_id, -32602, "session_id parameter required")

        last_lines: int = int(params.get("last_lines", 50))
        result = self.session_endpoints.inspect(session_id, last_lines)
        if "error" in result:
            return _rpc_error(req_id, -32603, str(result["error"]))

        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    async def _rpc_session_send(self, req_id: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Handle ``session/send``.

        Params:
            session_id (str): Target session.
            text (str): Text to send.
            enter (bool, optional): Whether to append a newline (default False).

        Returns:
            ``{"success": bool}`` always (never raises).
        """
        session_id: str | None = params.get("session_id")
        if not session_id:
            return _rpc_error(req_id, -32602, "session_id parameter required")

        text: str = params.get("text", "")
        enter: bool = bool(params.get("enter", False))
        result = self.session_endpoints.send(session_id, text, enter=enter)
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_runner(self, agent_name: str) -> AgentRunner | None:
        """Return a runner for *agent_name*, loading on demand if needed."""
        runner = self.agents.get(agent_name)
        if runner is None:
            runner = get_runner(agent_name)
            if runner is not None:
                self.agents[agent_name] = runner
        return runner

    async def _run_agent(
        self,
        session: AgentSession,
        runner: AgentRunner,
        prompt: str,
        cwd: Path | None,
    ) -> RunResult | dict[str, Any]:
        """Execute the runner in a thread executor and update session state.

        Returns either a :class:`RunResult` on success or an error dict on
        failure.
        """
        loop = asyncio.get_event_loop()
        session.is_running = True
        try:
            result: RunResult = await loop.run_in_executor(
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
            return result
        except Exception as exc:
            logger.error("Agent execution error for session %s: %s", session.session_id, exc, exc_info=True)
            return {"error": {"code": -32603, "message": f"Agent execution failed: {exc}"}}
        finally:
            session.is_running = False

    # ------------------------------------------------------------------
    # Transports
    # ------------------------------------------------------------------

    async def run_stdio(self) -> None:
        """Serve JSON-RPC requests over stdin/stdout (local agent mode)."""
        logger.info("ACP server adapter listening on stdio")
        loop = asyncio.get_event_loop()

        while True:
            try:
                line: str = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                raw = json.loads(line)

                # Route by envelope type
                if raw.get("type") == "task":
                    response = await self.handle_acp_message(raw)
                else:
                    response = await self.handle_jsonrpc(raw)

                sys.stdout.write(json.dumps(response).decode() + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError as exc:
                err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
                sys.stdout.write(json.dumps(err).decode() + "\n")
                sys.stdout.flush()
            except Exception as exc:
                logger.error("Unexpected error in stdio loop: %s", exc, exc_info=True)
                err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": f"Internal error: {exc}"}}
                sys.stdout.write(json.dumps(err).decode() + "\n")
                sys.stdout.flush()

    def build_starlette_app(self) -> Starlette:
        """Build a Starlette ASGI application exposing the ACP server over HTTP.

        Endpoints:
            GET  /health    Liveness probe.
            POST /rpc       JSON-RPC 2.0 endpoint.
            POST /acp       Native ACP message endpoint.
        """

        async def health(request: Request) -> PlainTextResponse:
            return PlainTextResponse("ok")

        async def rpc(request: Request) -> JSONResponse:
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(
                    {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
                    status_code=400,
                )
            response = await self.handle_jsonrpc(body)
            status = 200 if "error" not in response else 422
            return JSONResponse(response, status_code=status)

        async def acp(request: Request) -> JSONResponse:
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(
                    {"type": "error", "error": {"code": "PARSE_ERROR", "message": "Invalid JSON"}},
                    status_code=400,
                )
            response = await self.handle_acp_message(body)
            status = 200 if response.get("type") != "error" else 422
            return JSONResponse(response, status_code=status)

        return Starlette(
            routes=[
                Route("/health", health, methods=["GET"]),
                Route("/rpc", rpc, methods=["POST"]),
                Route("/acp", acp, methods=["POST"]),
            ]
        )

    def run_http(self, host: str = "127.0.0.1", port: int = ACP_DEFAULT_PORT) -> None:
        """Start the HTTP server (blocking).

        Args:
            host: Bind address (default ``127.0.0.1``).
            port: Bind port (default :data:`ACP_DEFAULT_PORT`).
        """
        app = self.build_starlette_app()
        logger.info("ACP server adapter listening on http://%s:%d", host, port)
        uvicorn.run(app, host=host, port=port)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(
    *,
    http: bool = False,
    host: str = "127.0.0.1",
    port: int = ACP_DEFAULT_PORT,
    log_level: str = "INFO",
) -> None:
    """CLI entry point.  Use ``--http`` flag to start HTTP server."""
    normalized_log_level = log_level.upper()
    if normalized_log_level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=getattr(logging, normalized_log_level))

    adapter = ACPServerAdapter()

    if http:
        adapter.run_http(host=host, port=port)
    else:
        asyncio.run(adapter.run_stdio())


@app.callback(invoke_without_command=True)
def cli(
    http: bool = typer.Option(False, "--http", help="Start HTTP server instead of stdio"),
    host: str = typer.Option("127.0.0.1", "--host", help="HTTP bind host"),
    port: int = typer.Option(ACP_DEFAULT_PORT, "--port", help="HTTP bind port"),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR)"),
) -> None:
    """Run ACP server in stdio mode by default, or HTTP mode with ``--http``."""
    try:
        main(http=http, host=host, port=port, log_level=log_level)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


if __name__ == "__main__":
    app()
