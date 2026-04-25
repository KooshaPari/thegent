# thegent

> Meta-Agent Framework for Autonomous System Orchestration

thegent (The Agent) is a sophisticated meta-agent framework that enables autonomous system orchestration, multi-agent collaboration, and intelligent task decomposition.

## Philosophy

**"The agent that manages agents"**

- **Autonomy**: Self-directed execution with minimal human intervention
- **Reflection**: Continuous self-improvement through execution feedback
- **Collaboration**: Seamless multi-agent coordination
- **Adaptation**: Dynamic reconfiguration based on context

## Core Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| **Task Decomposition** | Break complex tasks into manageable sub-tasks | Stable |
| **Agent Selection** | Choose optimal agent for each sub-task | Stable |
| **Context Management** | Maintain and share context across agents | Stable |
| **Plan Execution** | Execute plans with rollback on failure | Stable |
| **Reflection** | Learn from execution outcomes | Beta |
| **Self-Modification** | Update own behavior based on feedback | Alpha |

## Architecture

```
thegent Architecture:
- Meta-Controller: High-level orchestration
- Planner: Task decomposition and planning
- Executor: Plan execution and monitoring
- Reflector: Post-execution analysis
- Learner: Pattern extraction and adaptation
- Communicator: Inter-agent messaging
```

## Agent Types

| Type | Role | Capabilities |
|------|------|--------------|
| **orchestrator** | Meta-agent coordination | Planning, delegation, monitoring |
| **executor** | Task execution | Tools, API calls, code execution |
| **advisor** | Consultation and review | Analysis, recommendations |
| **memory** | Context and knowledge | Retrieval, summarization |

## Quick Start

```python
from thegent import MetaAgent

# Create meta-agent
meta = MetaAgent()

# Execute complex task
result = await meta.execute("""
Build a microservice that:
1. Accepts webhook events
2. Processes them asynchronously
3. Stores results in PostgreSQL
4. Exposes a REST API
""")

# The meta-agent automatically:
# - Decomposes into sub-tasks
# - Selects appropriate agents
# - Coordinates execution
# - Handles errors and retries
```

## Configuration

```yaml
# ~/.config/thegent/config.yaml
version: "1.0"

meta_agent:
  max_agents: 10
  planning_depth: 3
  reflection_enabled: true
  
  agents:
    - type: orchestrator
      count: 1
      priority: high
      
    - type: executor
      count: 5
      priority: normal
      tools: [bash, python, docker]
      
    - type: advisor
      count: 2
      priority: low

communication:
  protocol: message_bus
  bus_type: redis
  timeout: 30s

learning:
  enabled: true
  storage: postgresql
  retention: 90d
```

## References

- AutoGen: https://microsoft.github.io/autogen/
- CrewAI: https://www.crewai.io/
- LangChain: https://langchain.com/
- Semantic Kernel: https://learn.microsoft.com/en-us/semantic-kernel/
