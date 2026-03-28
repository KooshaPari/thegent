# thegent-agents

Agent runner and orchestration sub-package for thegent.

## Overview

`thegent-agents` encapsulates:

- Agent persona definitions and runner strategy pattern
- Agent lifecycle and state management
- Hook dispatch for agent events (pre-run, post-run, failure)
- Agent isolation and execution context

## Installation

```bash
pip install thegent-agents
```

## Usage

```python
from thegent_agents import AgentRunner

# Run an agent
runner = AgentRunner(persona="researcher")
result = await runner.run("Task description")
```

## Architecture

During the split transition (Track 4.2-4.3), this package integrates with the monolith's agent module. The full split (T4.4) will make this fully independent.

## Testing

```bash
pytest tests/
```

## Dependencies

- `thegent-core>=0.1.0` - Core models and contracts
- `pydantic>=2.0.0` - Data validation
