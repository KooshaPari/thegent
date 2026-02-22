# ANTE: Preferences

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Configuration

Preferences
Configuration
Preferences
Settings file, environment variables, and directory structure
​

Settings file
Ante stores user preferences in ~/.ante/settings.json:

Copy

Ask AI
{
  "model": "claude-sonnet-4-5-20250514",
  "provider": "anthropic",
  "theme": "default",
  "policy": "default",
  "has_completed_onboarding": true
}

Field
Description
model
Default model name
provider
Default API provider
theme
TUI color theme
policy
Default permission policy (default or yolo)
has_completed_onboarding
Whether the onboarding flow has been completed
Settings can be overridden per-session via CLI flags.
​

Environment variables
Variable
Description
ANTHROPIC_API_KEY
API key for Anthropic (Claude)
OPENAI_API_KEY
API key for OpenAI
ANTE_HOME
Override the home config directory (default: ~/.ante)
ANTE_DISABLE_STREAMING
Disable streaming responses in TUI mode
​

Directory structure
​

User-level (~/.ante/)

Copy

Ask AI
~/.ante/
├── settings.json      # User preferences
├── skills/            # User-level skills
└── agents/            # User-level sub-agents

​

Project-level (.ante/)

Copy

Ask AI
.ante/
└── skills/            # Project-specific skills

​

Claude.ai compatibility (.claude/)

Copy

Ask AI
.claude/
└── projects/
    └── `<path>`/
        └── memory/
            └── MEMORY.md   # Auto-memory for this project

​

Temporary files

Copy

Ask AI
/tmp/ante/`<project-hash>`/   # Temp files scoped per project

​

Precedence
Configuration is resolved in this order (later overrides earlier):
Built-in defaults
~/.ante/settings.json
CLI flags (--model, --provider, etc.)

Previous
Adding a 3rd Party Provider

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.
