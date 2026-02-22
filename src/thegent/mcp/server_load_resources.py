"""Resource and tool loader setup for thegent MCP server."""

from pathlib import Path
from typing import Any

from thegent.mcp import server_load_module as _load_server_module_shared
from thegent.mcp.server_tool_loader import (
    load_handoff_queue_tools as _load_handoff_queue_tools,
    load_queue_mutations_tools as _load_queue_mutations_tools,
    load_session_tools as _load_session_tools,
    load_tools_batch4 as _load_tools_batch4,
    load_tools_contract_observe as _load_tools_contract_observe,
    load_tools_coordination as _load_tools_coordination,
    load_tools_dynamic_registry as _load_tools_dynamic_registry,
    load_tools_escalation as _load_tools_escalation,
    load_tools_governance as _load_tools_governance,
    load_tools_locking_planning as _load_tools_locking_planning,
    load_tools_planning as _load_tools_planning,
    load_tools_prompt_and_handoff as _load_tools_prompt_and_handoff,
    load_tools_provider_models as _load_tools_provider_models,
    load_tools_queue as _load_tools_queue,
    load_tools_research as _load_tools_research,
    load_tools_runtime as _load_tools_runtime,
    load_tools_sessions as _load_tools_sessions,
    load_tools_skills as _load_tools_skills,
    load_tools_terminal as _load_tools_terminal,
    load_tools_workstream_governance as _load_tools_workstream_governance,
    load_tools_workstream_lsp as _load_tools_workstream_lsp,
)
from thegent.mcp.server_resources import (
    load_resource_catalog as _load_resource_catalog,
    load_resource_contracts as _load_resource_contracts,
    load_resource_sessions as _load_resource_sessions,
    load_resource_system as _load_resource_system,
    load_resource_workflow as _load_resource_workflow,
    load_resource_workstream as _load_resource_workstream,
    load_workflow_prompts as _load_workflow_prompts,
)


def load_all_resources() -> dict[str, Any]:
    """Load all server resources and tool loaders.

    Returns:
        Dictionary with all loaded resource modules and tools.
    """
    resources = {}

    # Resource loaders
    resources["_server_resource_sessions"] = _load_resource_sessions(_load_server_module_shared)
    resources["_server_resource_catalog"] = _load_resource_catalog(_load_server_module_shared)
    resources["_server_resource_workstream"] = _load_resource_workstream(_load_server_module_shared)
    resources["_server_resource_contracts"] = _load_resource_contracts(_load_server_module_shared)
    resources["_server_resource_system"] = _load_resource_system(_load_server_module_shared)
    resources["_server_resource_workflow"] = _load_resource_workflow(_load_server_module_shared)
    resources["_server_workflow_prompts"] = _load_workflow_prompts(_load_server_module_shared)

    # Tool loaders
    resources["_server_session_tools"] = _load_session_tools(_load_server_module_shared)
    resources["_server_handoff_queue_tools"] = _load_handoff_queue_tools(_load_server_module_shared)
    resources["_server_queue_mutations_tools"] = _load_queue_mutations_tools(
        _load_server_module_shared
    )
    resources["_server_tools_sessions"] = _load_tools_sessions(_load_server_module_shared)
    resources["_server_tools_queue"] = _load_tools_queue(_load_server_module_shared)
    resources["_server_tools_terminal"] = _load_tools_terminal(_load_server_module_shared)
    resources["_server_tools_escalation"] = _load_tools_escalation(_load_server_module_shared)
    resources["_server_tools_governance"] = _load_tools_governance(_load_server_module_shared)
    resources["_server_tools_research"] = _load_tools_research(_load_server_module_shared)
    resources["_server_tools_planning"] = _load_tools_planning(_load_server_module_shared)
    resources["_server_tools_contract_observe"] = _load_tools_contract_observe(
        _load_server_module_shared
    )
    resources["_server_tools_locking_planning"] = _load_tools_locking_planning(
        _load_server_module_shared
    )
    resources["_server_tools_skills"] = _load_tools_skills(_load_server_module_shared)
    resources["_server_tools_coordination"] = _load_tools_coordination(_load_server_module_shared)
    resources["_server_tools_runtime"] = _load_tools_runtime(_load_server_module_shared)
    resources["_server_tools_batch4"] = _load_tools_batch4(_load_server_module_shared)
    resources["_server_tools_workstream_lsp"] = _load_tools_workstream_lsp(_load_server_module_shared)
    resources["_server_tools_workstream_governance"] = _load_tools_workstream_governance(
        _load_server_module_shared
    )
    resources["_server_tools_prompt_and_handoff"] = _load_tools_prompt_and_handoff(
        _load_server_module_shared
    )
    resources["_server_tools_dynamic_registry"] = _load_tools_dynamic_registry(
        _load_server_module_shared
    )
    resources["_server_tools_provider_models"] = _load_tools_provider_models(_load_server_module_shared)

    # Load harness tools
    resources["_server_tools_harness"] = _load_server_module_shared(
        server_file=Path(__file__).parent / "server.py",
        module_filename="tools_harness.py",
        module_import_name="thegent.mcp._server_tools_harness",
        failure_message="Unable to load harness tool helpers",
    )

    return resources
