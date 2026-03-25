# Extracted Packages

The following code has been extracted from thegent to standalone packages:

## Extracted to Phenotype Products

| Code | New Location | Status |
|------|--------------|--------|
| Agent roles/library | phenotype-agent-core | Extracted |
| Task orchestration | phenotype-task-engine | Extracted |
| Docs engine | phenotype-docs-engine | Extracted |
| Research engine | phenotype-research-engine | Extracted |
| Evaluation | phenotype-evaluation | Extracted |

## Migration

Replace imports from `thegent/src/thegent/{module}` with imports from the new packages:

```python
# Old
from thegent.src.thegent.agents import Agent

# New
from phenotype_agent_core import Agent
```

## Timeline

- v0.2.0: Initial extraction complete
- v0.3.0: Legacy code removed from thegent
- v0.4.0: Full deprecation

