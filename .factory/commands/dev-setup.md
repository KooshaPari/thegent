---
description: Bootstrap a fresh development environment for zen-mcp-server
argument-hint: <machine-or-env>
---

Guide setup for `$ARGUMENTS`:

- Clone repo, install Python 3.12+, and create virtualenv (`python -m venv .venv && source .venv/bin/activate`).
- Install deps (`pip install -e .[dev]`) and optional extras (Textual, dashboard).
- Copy `.env.template` → `.env`, populate required secrets, and enable `LOG_LEVEL=DEBUG` for tests.
- Register custom droids and commands (`/commands` reload, copy to `~/.factory/...`).
- Run smoke check: `python -m pytest tests/smoke -xvs` and `python communication_simulator_test.py --list-tests`.

Respond with:

Summary: <headline>
Steps:
- [ ] <action>
Validation:
- <command>: <expected result>
Next:
- <follow-up or ✅ Environment ready>
