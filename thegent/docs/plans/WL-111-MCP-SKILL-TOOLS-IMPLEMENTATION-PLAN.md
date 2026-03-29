# WL-111 Implementation Plan: `thegent_activate_skill` MCP Tool

## Status
- `blocked` (depends on `WL-101`)

## Unblock Condition
- `WL-101` skill discovery + activation APIs merged and stable.

## Goal
- Expose skill discovery and activation as MCP tools with fail-loud behavior.

## Scope
- MCP tools:
  - `thegent_list_skills() -> list[SkillMeta]`
  - `thegent_activate_skill(skill_name: str) -> SkillContent`
- Agent runner integration for next-turn instruction injection.

## Planned File Touches
- `src/thegent/mcp/server/` (tool registration + handlers)
- `src/thegent/skills/discovery.py`
- `src/thegent/agents/base.py`
- `tests/mcp/`
- `tests/test_unit_skills.py`

## Execution Steps
1. Define MCP tool schemas for list/activate payloads.
2. Register tools in MCP server startup path.
3. Bridge tool handlers to skill discovery + activation backend.
4. Inject activated skill content into subsequent turn system prompt path.
5. Add explicit errors for missing skill, malformed manifest, and duplicate names.

## Validation Commands
- `uv run pytest -q tests/mcp/test_acl.py`
- `uv run pytest -q tests/mcp/test_gateway.py`
- `uv run pytest -q tests/test_unit_skills.py`
- `python -m py_compile src/thegent/skills/discovery.py`

## Acceptance Criteria
- `thegent_list_skills` returns deterministic metadata list.
- `thegent_activate_skill` returns exact skill body and influences next turn.
- Missing skill returns structured MCP error (non-silent failure).

## Wave-2 Do-Next Slice (Implementation-Ready)

### Deliverable
- Land MCP tool schema/registration contract tests with backend mocked behind strict interface.

### Files for First Slice
- `src/thegent/mcp/server/tools_skills.py` (new)
- `tests/mcp/test_tools_skills_contract.py` (new)

### Concrete Tasks
1. Define request/response schemas for list and activate tool payloads.
2. Register both tools at MCP server startup behind dedicated module.
3. Add handler signatures that require a `SkillBackend` protocol (no direct discovery calls in this slice).
4. Validate error envelope shape for missing skill and invalid input.

### Focused Validation
- `uv run pytest -q tests/mcp/test_tools_skills_contract.py`
- `python -m py_compile src/thegent/mcp/server/tools_skills.py`

### Unblock Handoff
- Once `WL-101` discovery API is stable, bind `SkillBackend` to real implementation and add integration tests for prompt injection effects.
