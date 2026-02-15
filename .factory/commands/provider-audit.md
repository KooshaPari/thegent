---
description: Audit provider configuration and credentials for zen-mcp-server
argument-hint: <provider-or-feature>
---

Audit `$ARGUMENTS` to ensure provider readiness:

- Inventory relevant files (`providers/`, `conf/`, `docs/providers/`).
- Verify required environment variables and secrets (reference `.env.template`).
- Check rate limits, model versions, and fallback chains (OpenRouter vs local).
- Recommend smoke tests (`python -m pytest tests/providers/...`, simulator scenarios).
- Flag security considerations (secret rotation, logging redaction).

Reply with:

Summary: <headline>
Checklist:
- <item> — <status + evidence>
Risks:
- <risk> — <mitigation or ✅ None>
Follow-up:
- <owner> — <action> — <due date>
