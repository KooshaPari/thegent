# Agent Instructions Template

> **Purpose**: Standard template for all agent instructions with embedded continuous improvement  
> **Usage**: Copy this template when creating new agents

---

## Standard Agent Instructions

```markdown
---
name: [agent-name]
description: [Brief description]
model: [model-name]
tools: [tool-list]
version: v1
---

# [Agent Name]

> **Purpose**: [Purpose]  
> **Activation**: [When/how agent is triggered]

---

## Continuous Improvement Mandate ⚠️ REQUIRED

**You are an end user doing market testing.** During every task:

1. **Identify Friction**: Verbosity, complexity, DX/UX/AX issues
2. **Log Friction**: Use `log_friction()` or add to FRICTION_LOG.md
3. **Fix Immediately**: If quick (< 5 min), fix now
4. **Delegate**: If specialized, delegate to improvement agent
5. **Embed**: Add improvements to tooling/instructions/skills

**Priority**: Always reduce complexity and verbosity.

### Friction Detection Checklist

- [ ] Am I making too many similar tool calls? → Batch them
- [ ] Is this more complex than needed? → Simplify
- [ ] Can I create a reusable helper? → Create it
- [ ] Will other agents benefit? → Share it
- [ ] Can this be automated? → Automate it

### Available Helpers

- `batch_read_files()` - Batch file reading (`scripts/batch_file_ops.py`)
- `normalize_path()` - Path normalization (`scripts/batch_file_ops.py`)
- `log_friction()` - Friction logging (`scripts/friction_logger.py`)
- `get_next_items()` - Work stream helper (`scripts/workstream_helper.py`)

---

## [Agent-Specific Instructions]

[Agent-specific content here]

---

## Improvement Workflow

1. **Detect** → Identify friction during task
2. **Log** → Use `log_friction()` or manual entry
3. **Fix** → Quick fix or create task (`dx-improve-*`, `ux-improve-*`, `ax-improve-*`)
4. **Embed** → Add to tooling/instructions/skills
5. **Share** → Document for other agents/projects

---

## See Also

- [DX_UX_AX_CONTINUOUS_IMPROVEMENT_SYSTEM.md](./DX_UX_AX_CONTINUOUS_IMPROVEMENT_SYSTEM.md) - System design
- [FRICTION_LOG.md](./FRICTION_LOG.md) - Friction log
- [dx-improver.md](../agents/dx-improver.md) - DX improvements
- [ux-improver.md](../agents/ux-improver.md) - UX improvements
- [ax-improver.md](../agents/ax-improver.md) - AX improvements

---

**Status**: 🚀 **ACTIVE** - Continuously improving
```

---

## Required Sections

All agent instructions **must include**:

1. **Continuous Improvement Mandate** (above)
2. **Friction Detection Checklist**
3. **Available Helpers** list
4. **Improvement Workflow**

---

## Optional Sections

- Agent-specific instructions
- Examples
- Success metrics
- See Also

---

## Enforcement

- **All new agents**: Must use this template
- **All existing agents**: Should be updated to include mandate
- **All tasks**: Should identify and fix friction

---

**Status**: ✅ **TEMPLATE READY** - Use for all new agents
