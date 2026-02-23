# Getting Started

`thegent` is a CLI and runtime for orchestrating agent tasks with operational governance.

## Prerequisites

- Python 3.12+
- Rust toolchain (for native performance components)
- Bun (for this VitePress docsite)

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/bootstrap.sh | sh -s -- install
```

## Initial Setup

```bash
thegent setup
thegent doctor
```

`thegent setup` configures provider credentials. `thegent doctor` verifies runtime health.

## First Successful Run

```bash
thegent run "summarize this repository structure" codex
```

Then inspect session status:

```bash
thegent ps
```

## Daily Workflow Example

```bash
# Find next actionable item
thegent plan do-next

# Execute one foreground task
thegent run "implement the selected item" claude

# Check and select a skill for focused runs
thegent skill list
thegent skill select thegent-skills
thegent run agent "implement with policy skill guidance" --skill thegent-skills

# Run a longer background task
thegent bg "generate implementation notes" gemini
```

## Next Reads

- [Installation](./installation)
- [CLI Reference](./cli-reference)
- [Providers](./providers)
- [Operations Troubleshooting](/operations/troubleshooting)
