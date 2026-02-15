# Cursor Agent

## Overview
Delegate focused tasks to Cursor AI's autonomous agent mode for file creation, command execution, and multi-step implementations. Cursor Agent is the most autonomous mode where you assign a task and it completes it directly.

## Inputs
- Task description (natural language)
- Working directory/workspace
- Execution mode (plan, agent, background)
- Model selection (Composer 2.0, Claude Sonnet 4.5, GPT-5)

## Quick start
- Plan mode: `/plan "Design authentication system architecture"`
- Agent mode: Start task in Composer with natural language description
- Background agent: Launch agent on separate branch for parallel work
- Skills: `/[skill-name]` to invoke custom agent skills

## Workflow
1. **Choose execution mode:**
   - `/plan` - Design approach before coding, ask clarifying questions
   - Standard agent - Interactive task execution with Q&A
   - Background agent - Autonomous work in isolated VM on separate branch
2. **Define task scope** using natural language
3. **Set boundaries:**
   - Workspace scope (files/directories accessible)
   - Network access permissions
   - Command execution limits
4. **Agent executes autonomously:**
   - Creates/edits files
   - Runs commands
   - Fixes errors automatically
   - Asks clarifying questions when needed
5. **Review and iterate:**
   - View agent progress in real-time
   - Provide feedback during execution
   - Review PR from background agents

## Modes

### Plan Mode (`/plan` or `--mode=plan`)
- Design approach before implementation
- Agent asks clarifying questions to refine plan
- Review and approve before execution starts
- Best for: Complex features, architectural decisions

### Interactive Agent Mode (default)
- Agent works directly in your workspace
- Can ask questions and wait for responses while continuing other work
- Creates files, runs commands, fixes errors
- Best for: Most development tasks requiring human input

### Background Agent Mode
- Works on separate branch in isolated Ubuntu VM
- Can open PRs for review when complete
- Has internet access and full workspace isolation
- Best for: Long-running tasks, parallel workstreams, exploratory work

## Model Selection
Available via `/model` command:
- **Composer 2.0** (default) - Cursor's ultra-fast coding model
- **Claude Sonnet 4.5** - Advanced reasoning for complex tasks
- **GPT-5** - Alternative for specific use cases

## Agent Skills
Extend capabilities with custom skills defined in SKILL.md files:
- Package domain knowledge, workflows, scripts
- Invoke with `/[skill-name]` in agent input
- Skills can include custom commands and context

## Hooks
Execute custom scripts at key points in agent loop:
- Auto-formatting after edits
- Gating dangerous commands
- Adding commit checkpoints
- Redacting environment secrets

## Configuration
Set rules in `.cursorrules` file for consistent behavior:
- Code style preferences
- Architectural patterns
- Testing requirements
- Security constraints

## Hierarchical Agent Structure
For complex projects, implement multi-tier coordination:
- **Principal Architect** - High-level system design
- **Manager Agents** - Module oversight, task assignment
- **Worker Agents** - Specific coding tasks, implementation

## Browser Control
Agents can interact with browsers for:
- Testing web applications
- Debugging UI issues
- Verifying visual regressions

## Best Practices
- Use plan mode for complex tasks before execution
- Set clear workspace boundaries for security
- Leverage background agents for parallel work
- Define custom skills for repeated workflows
- Use hooks for automated quality gates
- Configure rules for consistent code style
- Review background agent PRs before merging

## Sandboxing
- Supports macOS and Linux environments
- Access scoped to workspace by default
- Configurable network and filesystem restrictions
- Isolated VMs for background agents

## Notes
- Cursor Composer 2.0 includes ultra-fast model and multi-agent orchestration
- Interactive Q&A allows agents to ask questions while continuing work
- Background agents function as AI pair programmers with full autonomy
