"""Resource group module loaders for the MCP server (WL-120 W3-C2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_SERVER_PY = Path(__file__).parent / "server.py"


def load_resource_sessions(load_module: Any) -> Any:
    """Load session resource helpers from server/resources_sessions.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="resources_sessions.py",
        module_import_name="thegent.mcp._server_resource_sessions",
        failure_message="Unable to load session resource helpers",
    )


def load_resource_catalog(load_module: Any) -> Any:
    """Load catalog resource helpers from server/resources_catalog.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="resources_catalog.py",
        module_import_name="thegent.mcp._server_resource_catalog",
        failure_message="Unable to load catalog resource helpers",
    )


def load_resource_workstream(load_module: Any) -> Any:
    """Load workstream resource helpers from server/resources_workstream.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="resources_workstream.py",
        module_import_name="thegent.mcp._server_resource_workstream",
        failure_message="Unable to load workstream resource helpers",
    )


def load_resource_contracts(load_module: Any) -> Any:
    """Load contracts resource helpers from server/resources_contracts.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="resources_contracts.py",
        module_import_name="thegent.mcp._server_resource_contracts",
        failure_message="Unable to load contracts resource helpers",
    )


def load_resource_system(load_module: Any) -> Any:
    """Load system resource helpers from server/resources_system.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="resources_system.py",
        module_import_name="thegent.mcp._server_resource_system",
        failure_message="Unable to load system resource helpers",
    )


def load_resource_workflow(load_module: Any) -> Any:
    """Load workflow resource helpers from server/resources_workflow.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="resources_workflow.py",
        module_import_name="thegent.mcp._server_resource_workflow",
        failure_message="Unable to load workflow resource helpers",
    )


def load_workflow_prompts(load_module: Any) -> Any:
    """Load workflow prompt helpers from server/workflow_prompts.py."""
    return load_module(
        server_file=_SERVER_PY,
        module_filename="workflow_prompts.py",
        module_import_name="thegent.mcp._server_workflow_prompts",
        failure_message="Unable to load workflow prompt helpers",
    )
