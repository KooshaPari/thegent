# workflow_prompts API Reference

> **Source**: `src/thegent/mcp/server/workflow_prompts.py`

Workflow resource/prompt registrations for MCP server.

---

## register_workflow_gardening_resource

---

## register_workflow_prompts

---

## resource_workflow_gardening

Gardening workflow: converge to empty backlog and complete green.

---

## resource_workflow_triggers

Workflow instructions: idea→research→spec, quality green, next item. Injected on UserPromptSubmit.

---

## thegent_bg_task_prompt_impl

---

## thegent_create_wbs_prompt_impl

---

## thegent_run_agent_prompt_impl

---

## thegent_workflow_gardening

Instructions for gardening: check gov traceability, tests, plan items; dispatch; converge to empty backlog and complete green.

Use when user says "garden", "converge", "empty backlog", "complete green".

---

## thegent_workflow_idea

```python
thegent_workflow_idea(idea: str)
```

Instructions for idea/task prompts: dump research, create specs, add work items.

Use when user gives research/explore/build/implement/design/create/feature prompts.

---

## thegent_workflow_next_item

Instructions to find and execute the next work item from the unified stream.

Use when user says "find the next thing to do", "what next", "pick next".

---

## thegent_workflow_quality_green

Instructions to run full quality pipeline until green.

Use when user says "get task quality green", "quality green", "make quality pass".

---

