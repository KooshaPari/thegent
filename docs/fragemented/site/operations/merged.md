# Merged Fragmented Markdown

## Source: site/operations/runbooks.md

# Runbooks

Use these short runbooks for common operational failures.

## Runbook: Broken Shell Integration

1. Regenerate shell config snippet:

```bash
thegent shell-init zsh
```

2. Ensure your shell startup file loads it.
3. Reinstall shims:

```bash
thegent install-shims
thegent doctor
```

## Runbook: Credential/Auth Failure

1. Re-run setup:

```bash
thegent setup
```

2. Re-test with explicit provider:

```bash
thegent run "health check" --provider codex --debug
```

## Runbook: Stuck Background Sessions

1. Inspect sessions:

```bash
thegent ps
```

2. Stop problematic session:

```bash
thegent stop <session_id>
```

3. Restart with a narrower prompt or different provider.

## Runbook: MCP Connectivity Failure

1. Start MCP server:

```bash
thegent serve
```

2. Verify client target host/port.
3. Remove stale resources safely:

```bash
thegent mcp prune
```

---

## Source: site/operations/troubleshooting.md

# Troubleshooting

Use this page when commands fail, sessions hang, or provider routes are unavailable.

## 1) Environment Validation

```bash
thegent doctor
```

Expected checks:

- Python + runtime dependencies
- shell/PATH shim integration
- provider credential presence
- proxy/MCP connectivity (if configured)

## 2) Session Diagnostics

```bash
thegent ps
```

Look for:

- stuck background sessions
- repeated failures with same provider/model
- recent stop reasons or abnormal exits

## 3) Provider Connectivity

If a specific provider fails:

```bash
thegent run "ping" --provider codex --debug
```

Check API key validity and route behavior.

## Symptom Matrix

| Symptom | Likely cause | Action |
|--------|---------------|--------|
| `command not found: thegent` | PATH/shim not loaded | Re-run shell init + `thegent install-shims` |
| Immediate auth failures | Missing/invalid API key | Run `thegent setup` and verify env |
| Session hangs | Provider or network issue | Retry with `--debug`, switch provider |
| MCP clients cannot connect | MCP server not running | Start `thegent serve` |

## Escalation Pattern

1. Capture failing command and exact error text.
2. Re-run with `--debug`.
3. Narrow to one provider/model.
4. Apply the matching [runbook](./runbooks).

---
