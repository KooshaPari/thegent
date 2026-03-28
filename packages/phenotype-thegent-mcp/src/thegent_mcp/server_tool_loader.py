"""Tool group module loaders for the MCP server (WL-120 W3-C3)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_SERVER_PY = Path(__file__).parent / "server.py"


def load_session_tools(load_module: Any) -> Any:
    """Load session tool registrations from server/session_tools.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="session_tools.py",
        module_import_name="thegent.mcp._server_session_tools",
        failure_message="Unable to load session tool registrations",
    )


def load_handoff_queue_tools(load_module: Any) -> Any:
    """Load handoff/queue tool registrations from server/tools_handoff_queue.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_handoff_queue.py",
        module_import_name="thegent.mcp._server_handoff_queue_tools",
        failure_message="Unable to load handoff/queue tool registrations",
    )


def load_queue_mutations_tools(load_module: Any) -> Any:
    """Load queue mutation tool registrations from server/tools_queue_mutations.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_queue_mutations.py",
        module_import_name="thegent.mcp._server_queue_mutations_tools",
        failure_message="Unable to load queue mutation tool registrations",
    )


def load_tools_sessions(load_module: Any) -> Any:
    """Load session tool helpers from server/tools_sessions.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_sessions.py",
        module_import_name="thegent.mcp._server_tools_sessions",
        failure_message="Unable to load session tool helpers",
    )


def load_tools_queue(load_module: Any) -> Any:
    """Load queue tool helpers from server/tools_queue.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_queue.py",
        module_import_name="thegent.mcp._server_tools_queue",
        failure_message="Unable to load queue tool helpers",
    )


def load_tools_terminal(load_module: Any) -> Any:
    """Load terminal tool helpers from server/tools_terminal.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_terminal.py",
        module_import_name="thegent.mcp._server_tools_terminal",
        failure_message="Unable to load terminal tool helpers",
    )


def load_tools_escalation(load_module: Any) -> Any:
    """Load escalation tool helpers from server/tools_escalation.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_escalation.py",
        module_import_name="thegent.mcp._server_tools_escalation",
        failure_message="Unable to load escalation tool helpers",
    )


def load_tools_governance(load_module: Any) -> Any:
    """Load governance tool helpers from server/tools_governance.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_governance.py",
        module_import_name="thegent.mcp._server_tools_governance",
        failure_message="Unable to load governance tool helpers",
    )


def load_tools_research(load_module: Any) -> Any:
    """Load research tool helpers from server/tools_research.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_research.py",
        module_import_name="thegent.mcp._server_tools_research",
        failure_message="Unable to load research tool helpers",
    )


def load_tools_planning(load_module: Any) -> Any:
    """Load planning tool helpers from server/tools_planning.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_planning.py",
        module_import_name="thegent.mcp._server_tools_planning",
        failure_message="Unable to load planning tool helpers",
    )


def load_tools_contract_observe(load_module: Any) -> Any:
    """Load contract/observe tool helpers from server/tools_contract_observe.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_contract_observe.py",
        module_import_name="thegent.mcp._server_tools_contract_observe",
        failure_message="Unable to load contract/observe tool helpers",
    )


def load_tools_locking_planning(load_module: Any) -> Any:
    """Load locking/planning tool helpers from server/tools_locking_planning.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_locking_planning.py",
        module_import_name="thegent.mcp._server_tools_locking_planning",
        failure_message="Unable to load locking/planning tool helpers",
    )


def load_tools_skills(load_module: Any) -> Any:
    """Load skills tool helpers from server/tools_skills.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_skills.py",
        module_import_name="thegent.mcp._server_tools_skills",
        failure_message="Unable to load skills tool helpers",
    )


def load_tools_coordination(load_module: Any) -> Any:
    """Load coordination tool helpers from server/tools_coordination.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_coordination.py",
        module_import_name="thegent.mcp._server_tools_coordination",
        failure_message="Unable to load coordination tool helpers",
    )


def load_tools_runtime(load_module: Any) -> Any:
    """Load runtime tool helpers from server/tools_runtime.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_runtime.py",
        module_import_name="thegent.mcp._server_tools_runtime",
        failure_message="Unable to load runtime tool helpers",
    )


def load_tools_batch4(load_module: Any) -> Any:
    """Load batch4 tool registrations from server/tools_batch4.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_batch4.py",
        module_import_name="thegent.mcp._server_tools_batch4",
        failure_message="Unable to load batch4 tool registrations",
    )


def load_tools_workstream_lsp(load_module: Any) -> Any:
    """Load workstream/LSP tool helpers from server/tools_workstream_lsp.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_workstream_lsp.py",
        module_import_name="thegent.mcp._server_tools_workstream_lsp",
        failure_message="Unable to load workstream/LSP tool helpers",
    )


def load_tools_workstream_governance(load_module: Any) -> Any:
    """Load workstream/governance tool registrations from server/tools_workstream_governance.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_workstream_governance.py",
        module_import_name="thegent.mcp._server_tools_workstream_governance",
        failure_message="Unable to load workstream/governance tool registrations",
    )


def load_tools_prompt_and_handoff(load_module: Any) -> Any:
    """Load prompt/handoff tool wrappers from server/tools_prompt_and_handoff.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_prompt_and_handoff.py",
        module_import_name="thegent.mcp._server_tools_prompt_and_handoff",
        failure_message="Unable to load prompt/handoff tool wrappers",
    )


def load_tools_dynamic_registry(load_module: Any) -> Any:
    """Load dynamic registry tool registrations from server/tools_dynamic_registry.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_dynamic_registry.py",
        module_import_name="thegent.mcp._server_tools_dynamic_registry",
        failure_message="Unable to load dynamic registry tool registrations",
    )


def load_tools_provider_models(load_module: Any) -> Any:
    """Load provider/model tool registrations from server/tools_provider_models.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="tools_provider_models.py",
        module_import_name="thegent.mcp._server_tools_provider_models",
        failure_message="Unable to load provider/model tool registrations",
    )
