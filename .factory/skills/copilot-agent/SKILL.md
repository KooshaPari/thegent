# GitHub Copilot CLI Agent (Claude Haiku 4.5 Locked)

## Overview
GitHub Copilot CLI brings AI-powered coding assistance directly to your command line, enabling you to build, debug, and understand code through natural language conversations. Copilot CLI edits files, runs commands, and helps you iterate fast without leaving your terminal.

**Model Lock:** This wrapper is **strictly locked to Claude Haiku 4.5** (`claude-haiku-4-5-20251001`). All model override attempts are logged and ignored to ensure consistency.

## Inputs
- Natural language prompt (task description)
- Working directory context
- Mode selection (interactive, programmatic, autopilot)
- Reasoning level (low, medium, high)

## Quick start
- Interactive mode: `~/.claude/skills/copilot-agent/scripts/run_copilot.sh`
- Programmatic mode: `run_copilot.sh --prompt "implement authentication handler" --mode programmatic`
- Autopilot mode: `run_copilot.sh --prompt "fix all failing tests" --mode autopilot --cd ~/my-project`
- With workspace: `run_copilot.sh --prompt "build API endpoint" --cd /path/to/project`

## Workflow
1. **Verify dependencies:**
   - Check Copilot CLI is installed: `which copilot`
   - Wrapper validates CLI availability before execution
2. **Choose operating mode:**
   - Interactive - Iterative conversation with Copilot (default)
   - Programmatic - Single command execution and exit
   - Autopilot - Agent continues until task complete
3. **Execute with wrapper:**
   - Interactive: `run_copilot.sh`
   - Programmatic: `run_copilot.sh --prompt "..." --mode programmatic`
   - Autopilot: `run_copilot.sh --prompt "..." --mode autopilot --cd <workspace>`
4. **Agent executes:**
   - Edits files directly in your workspace
   - Runs terminal commands
   - Fetches web content for context
   - Manages Git operations
5. **Review and iterate:**
   - View diffs with syntax highlighting
   - Approve/reject changes
   - Provide feedback in conversation

## Model Lock Guarantee
- **Locked Model:** `claude-haiku-4-5-20251001` (Claude Haiku 4.5)
- **Why Haiku:** Fast, efficient, perfect for autonomous agent tasks
- **Override Protection:** All `--model` flags are logged and ignored
- **Validation:** Script prints model on execution start
- **Consistency:** Ensures all subagent runs use same capabilities

## Operating Modes

### Interactive Mode (default)
Start with `copilot` command:
- Prompt Copilot to answer questions or perform tasks
- React to responses in the same session
- Continuous conversation until exit
- Full context retention throughout session

### Programmatic Mode
Use `-p` or `--prompt` flag:
```bash
copilot -p "create REST API endpoint for user authentication"
```
- Single prompt execution
- Exits after task completion
- Useful for scripting and automation

### Autopilot Mode
Press `Shift+Tab` to cycle through modes:
- Agent continues working until task complete
- Minimal human intervention
- Automatic iteration and error fixing
- Best for well-defined, autonomous tasks

## Slash Commands

### Core Commands
- `/model` - Choose from available models (Claude Sonnet 4.5, GPT-5, etc.)
- `/cwd` - Add current working directory to context
- `/add-dir <path>` - Add specific directory to context
- `/fix` - Fix errors in code
- `/generate` - Generate new code
- `/doc` - Add documentation
- `/simplify` - Simplify complex code

### Custom Agents
- `/deploy` - Deploy web application to Cloud Run
- Create custom specialized agents for different tasks
- Automatic delegation to specialized agents for common tasks

## Model Support
Default: **Claude Sonnet 4.5**

Available models via `/model`:
- Claude Sonnet 4.5 (default)
- Claude Sonnet 4
- GPT-5

## Key Features

### Auto-compaction
Automatically compresses conversation history when approaching 95% token limit

### Better Diffs
- Intra-line syntax highlighting showing exact changes
- Integrates with Git's configured pager
- Visual representation of modifications

### Tab Completion
Autocomplete file paths in `/cwd` and `/add-dir` commands

### Model Reasoning
`Ctrl+T` toggles model reasoning visibility for supported models

### Web Fetch Tool
Retrieve content from URLs as markdown:
- Controlled through `~/.copilot/config`
- `allowed_urls` and `denied_urls` patterns
- Fetch documentation, examples, references

## Customization

### Custom Agents
Create specialized versions of Copilot for different tasks:
- Expert frontend engineer following team guidelines
- Backend API specialist with security focus
- DevOps automation expert
- Database optimization specialist

Define agents with specific:
- Knowledge domains
- Coding styles
- Team conventions
- Security policies

### Hooks
Execute custom shell commands at key execution points:
- Pre-commit validation
- Logging and auditing
- Security scanning
- Workflow automation
- Test execution gates

Hook triggers:
- Before file edits
- After command execution
- On session start/end
- Error conditions

## Configuration

### Config File Location
`~/.copilot/config`

### Settings
```yaml
# Model preferences
default_model: "claude-sonnet-4.5"

# Web access control
allowed_urls:
  - "*.github.com"
  - "docs.*.com"
denied_urls:
  - "*internal.company.com"

# Custom agents
agents:
  frontend:
    role: "Expert React/TypeScript developer"
    rules: "Follow team style guide"
  backend:
    role: "Go API specialist"
    rules: "Enforce security best practices"

# Hooks
hooks:
  pre_edit: "./scripts/format-check.sh"
  post_command: "./scripts/audit-log.sh"
```

## Context Management

### Enhanced Context Features (2026)
- Automatic context compression at 95% token limit
- Smart file selection based on relevance
- Directory-level context addition
- Tab completion for path navigation

### Best Practices
- Use `/add-dir` for focused context (specific modules)
- Leverage tab completion to explore workspace
- Let auto-compaction manage history
- Add URLs for external documentation context

## Integration

### Git Integration
- Respects Git configuration
- Uses configured pager for diffs
- Supports commit operations
- Branch management

### IDE Integration
Works alongside:
- GitHub Copilot in VS Code
- JetBrains IDEs
- Other editor extensions

## Best Practices

1. **Start with interactive mode** for exploratory tasks
2. **Use autopilot mode** for well-defined, autonomous work
3. **Create custom agents** for recurring task types
4. **Configure hooks** for automated quality gates
5. **Set URL policies** to control web access
6. **Leverage slash commands** for efficient workflow
7. **Use model reasoning** (Ctrl+T) for debugging agent decisions
8. **Review diffs carefully** before accepting changes

## Security Considerations

- Control web access via `allowed_urls`/`denied_urls`
- Use hooks for security scanning
- Review all file changes before committing
- Configure custom agents with security policies
- Audit logs via post-execution hooks

## Notes

- Copilot CLI uses Claude Sonnet 4.5 by default (as of 2026)
- Enhanced agents and context management released January 2026
- Plan-before-build feature allows review before execution
- Auto-compaction prevents token limit issues
- Hooks enable deep workflow customization
