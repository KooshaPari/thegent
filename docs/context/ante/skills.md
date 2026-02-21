# ANTE: Skills

> Extracted from Ante docs. Fetched 2026-02-20

Ante home page

Search...



Navigation

Extensibility

Skills
Extensibility
Skills
Give Ante new capabilities with Agent Skills — the open format for portable agent expertise
Skills are folders of instructions, scripts, and resources that extend Ante’s capabilities. They follow the open Agent Skills format, making them portable across compatible agent products.
​

Creating a skill
A skill is a directory containing a SKILL.md file:

Copy

Ask AI
commit/
└── SKILL.md

SKILL.md uses YAML frontmatter followed by Markdown instructions:

Copy

Ask AI
---
name: commit
description: Create a git commit with a descriptive message following conventional commit format.
---

Look at the current git diff and create a commit with a clear,
descriptive message that follows conventional commit format.
Use `git add` to stage relevant files first.

​

Example: review skill with tools and references

Copy

Ask AI
review/
├── SKILL.md
└── references/
    └── checklist.md


Copy

Ask AI
---
name: review
description: Review code changes for bugs, security issues, and style. Use when the user asks for a code review.
allowed-tools:
  - Read
  - Glob
  - Grep
---

Review the code at $ARGUMENTS for:
- Bugs and logic errors
- Security vulnerabilities
- Style and idiom issues
- Missing error handling

See [checklist](references/checklist.md) for the full review checklist.

Provide a summary with specific line references.

​

Skill directories
Directory
Scope
~/.ante/skills/
User-level (available in all projects)
agents/skills/
Project-level (available in this project)
.ante/skills/
Project-level (available in this project)
.claude/skills/
Project-level (available in this project)
​

SKILL.md frontmatter
Every SKILL.md must start with a YAML frontmatter block delimited by ---. The block can be empty, but the delimiters are required.
Field
Required
Default
Description
name
No
Parent directory name
Identifier for the skill. If omitted, the skill directory name is used.
description
No
First paragraph of body
What this skill does and when to use it. If omitted, extracted from the first paragraph of the Markdown body.
argument-hint
No
—
Hint text shown to the user for expected arguments (e.g. `<path>`).
user-invocable
No
true
Whether the skill can be invoked by the user via slash command. Set to false for skills intended only for model invocation.
disable-model-invocation
No
false
When true, prevents the model from invoking this skill automatically.
allowed-tools
No
—
YAML list of pre-approved tools the skill can use (e.g. Read, Grep, Bash(git diff -- *)).
metadata
No
—
Arbitrary key-value pairs for additional metadata.
​

Optional directories
Skills can include additional resources alongside SKILL.md:

Copy

Ask AI
my-skill/
├── SKILL.md           # Required — instructions
├── scripts/           # Executable code the agent can run
├── references/        # Additional docs loaded on demand
└── assets/            # Templates, schemas, data files

scripts/ — Self-contained scripts (Python, Bash, etc.) the agent can execute
references/ — Detailed documentation loaded only when needed, keeping the main instructions lean
assets/ — Static resources like templates, schemas, or lookup tables
​

How skills are discovered
Skills are discovered from multiple directories in precedence order. Later directories override earlier ones if they share a skill name:
System-level (built-in skills)
~/.ante/skills/ (user-level)
agents/skills/ (project-level)
.ante/skills/ (project-level)
.claude/skills/ (project-level)
A project-level skill overrides a user-level skill of the same name. If multiple project-level directories contain a skill with the same name, the one discovered last wins.
​

Using skills
Invoke a skill during a session with the slash syntax:

Copy

Ask AI
/commit

Or with arguments:

Copy

Ask AI
/review src/core/session.rs

The $ARGUMENTS placeholder in the skill instructions will be replaced with whatever you pass after the skill name.
​

Learn more
The Agent Skills format is an open standard supported by multiple agent products. See the full specification for details on naming conventions, progressive disclosure, and validation.

Previous
Sub-Agents

Next

Powered by



Assistant



Responses are generated using AI and may contain mistakes.




