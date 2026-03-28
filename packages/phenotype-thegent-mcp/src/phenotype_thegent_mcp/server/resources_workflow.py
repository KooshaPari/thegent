"""Workflow resource/prompt handlers for MCP server."""

from __future__ import annotations


WORKFLOW_TRIGGERS_TEXT = """# Workflow Triggers

## Idea/Task Prompts
When user gives idea/task prompts (research, explore, build, implement, design, create, feature, investigate):
1. Dump research to docs/research/ (or docs/guides/)
2. Create or update specs in docs/docset/
3. Add work items to unified work stream (docs/reference/, contracts/, docs/plans/)
4. Enables: spam ideas → open new chat → ask "find the next thing to do"

## Quality Green
When user says "get task quality green", "quality green", "make quality pass", "fix quality":
- Run: task quality-a-r (full pipeline; on fail pipes to agent until green)
- Or: task quality:dag (DAG only)

## Next Item
When user says "find the next thing to do", "what next", "pick next", "next task":
1. Read from docs/reference/, docs/docset/, contracts/, docs/plans/
2. Check PLAN_STATUS.md, FR_TRACKER.md, or project tracker
3. Pick highest-priority in-progress or pending item
4. Execute that item

## Gardening (Converge to Empty Backlog + Green)
When user says "garden", "converge", "empty backlog", "complete green", "check gov traceability":
1. thegent govern go health (8 dimensions)
2. task quality; FR traceability; spec-verifier
3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
4. thegent govern escalate list --past-sla
5. Dispatch: phenotype_thegent_run/phenotype_thegent_bg for each failing dimension or pending item
6. task quality-a-r until green
7. thegent govern go cycle (AgilePlus)
8. Repeat until backlog empty and all green
"""

WORKFLOW_GARDENING_TEXT = """# Gardening Workflow (Converge to Empty Backlog + Green)

1. thegent govern go health (8 dimensions)
2. task quality; FR traceability; spec-verifier
3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
4. thegent govern escalate list --past-sla
5. Dispatch: phenotype_thegent_run/phenotype_thegent_bg for each failing dimension or pending item
6. task quality-a-r until green
7. thegent govern go cycle (AgilePlus)
8. Repeat until backlog empty and all green
"""


def resource_workflow_triggers_impl() -> str:
    return WORKFLOW_TRIGGERS_TEXT


def phenotype_thegent_workflow_idea_impl(idea: str) -> str:
    return f"""Idea/task: {idea}

Workflow:
1. Dump research to docs/research/ (or docs/guides/)
2. Create or update specs in docs/docset/
3. Add work items to unified work stream (docs/reference/, contracts/, docs/plans/)
4. This enables: spam ideas here → open new chat → ask "find the next thing to do"
"""


def phenotype_thegent_workflow_quality_green_impl() -> str:
    return """Run: task quality-a-r
(Full quality pipeline; on fail pipes to agent and reloads until green)
Or: task quality:dag (DAG only, no agent loop)
"""


def phenotype_thegent_workflow_next_item_impl() -> str:
    return """1. Read from unified work stream: docs/reference/, docs/docset/, contracts/, docs/plans/
2. Check docs/reference/PLAN_STATUS.md, docs/reference/FR_TRACKER.md, or project tracker
3. Pick the highest-priority in-progress or pending item
4. Execute that item
"""


def resource_workflow_gardening_impl() -> str:
    return WORKFLOW_GARDENING_TEXT


def phenotype_thegent_workflow_gardening_impl() -> str:
    return """Gardening workflow — converge to empty backlog + complete green:

1. thegent govern go health (8 dimensions)
2. task quality; FR traceability; spec-verifier
3. Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
4. thegent govern escalate list --past-sla
5. Dispatch: phenotype_thegent_run/phenotype_thegent_bg for each failing dimension or pending item
6. task quality-a-r until green
7. thegent govern go cycle (AgilePlus)
8. Repeat until backlog empty and all green
"""
