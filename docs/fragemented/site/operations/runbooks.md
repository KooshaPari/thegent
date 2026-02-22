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
