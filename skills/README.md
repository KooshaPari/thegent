# Skills

This directory contains thegent skills - agent persona definitions that can be auto-discovered and used by the thegent system.

## Skill Format

Each skill is a directory containing:

1. **`SKILL.md`** - The skill definition file (markdown)
2. **`skill.json`** - Metadata in JSON format

### skill.json Schema

```json
{
  "name": "skill-name",
  "description": "Human-readable description of the skill",
  "version": "1.0.0",
  "entrypoint": "thegent"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill identifier (should match directory name) |
| `description` | Yes | Human-readable description |
| `version` | Yes | Semantic version (e.g., "1.0.0") |
| `entrypoint` | Yes | Command or entry point to use |

### SKILL.md

The main skill definition file in markdown format. This contains:

- Agent persona instructions
- Capabilities and constraints
- Usage patterns
- Examples

## Auto-Discovery

The skills system automatically discovers skills from this directory using `src/thegent/skills/discovery.py`.

### Discovery Functions

- `discover_skills()` - Find all skills in the skills/ directory
- `load_skill(skill_name)` - Load a specific skill by name
- `validate_skill(skill_path)` - Validate a skill's structure

## Usage

### CLI Commands

```bash
# List all available skills
thegent skills list

# Show details of a specific skill
thegent skills show <skill-name>

# Validate a skill
thegent skills validate <skill-name>
```

### MCP Tools

```python
# List all skills
thegent_list_skills()

# Get skill details
thegent_get_skill(skill_name="skill-name")

# Run a skill
thegent_run_skill(skill_name="skill-name", context={})

# Validate a skill
thegent_validate_skill(skill_name="skill-name")
```

## Existing Skills

### thegent-skills

- **Description**: Unified orchestration guidance for direct thegent subcommand usage
- **Version**: 2.1.0
- **Entrypoint**: thegent

### sitback-agent

- **Description**: Sitback Agent persona: lightweight orchestrator for dashboard, terminals, and session routing
- **Version**: 1.0.0
- **Entrypoint**: thegent

### agent-browser

- **Description**: Managed Agent Browser workflow for auth journeys and repeatable browser tasks
- **Version**: 1.0.0
- **Entrypoint**: thegent browser

## Adding a New Skill

1. Create a new directory under `skills/` (e.g., `skills/my-new-skill/`)
2. Add `SKILL.md` with the skill definition
3. Add `skill.json` with metadata
4. The skill will be automatically discovered

Example `skill.json`:

```json
{
  "name": "my-new-skill",
  "description": "My new skill for doing X",
  "version": "1.0.0",
  "entrypoint": "thegent"
}
```
