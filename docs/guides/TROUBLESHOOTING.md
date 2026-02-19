# Troubleshooting Guide

This guide provides solutions for common issues encountered while using thegent on different platforms.

---

## 1. Quick Verification

If you encounter issues, always start by running the diagnostic tool:

```bash
thegent doctor
```

This will check your configuration, paths, and provider connectivity.

---

## 2. Common Issues by Platform

| Issue | macOS | Linux | Windows |
|-------|-------|-------|---------|
| **Command not found** | Check `~/.local/bin` in PATH | Check `~/.local/bin` in PATH | Check `%LOCALAPPDATA%\thegent\bin` in PATH |
| **Permission denied** | `chmod 755 ~/Library/Application\ Support/thegent` | `chmod 755 ~/.config/thegent` | Run PowerShell as Administrator |
| **Provider not configured** | `thegent cliproxy login <provider>` | `thegent cliproxy login <provider>` | `thegent cliproxy login <provider>` |
| **MCP server not reachable** | `thegent serve` | `thegent serve` | `thegent serve` (check firewall) |
| **WSL2 not available** | N/A | N/A | `wsl --install` |
| **PowerShell not found** | N/A | N/A | `winget install Microsoft.PowerShell` |

---

## 3. Platform-Specific Gotchas

### macOS
- **Case-insensitive filesystem:** thegent handles path resolution to avoid collisions on default macOS volumes. If you use a case-sensitive volume, ensure your paths match exactly.
- **SIP (System Integrity Protection):** thegent avoids modifying system directories and stays within user-writable paths (e.g., `~/Library/Application Support/thegent`).

### Linux
- **Multiple Python versions:** Ensure you are using the correct Python version. Check with `python3 --version`.
- **SELinux/AppArmor:** If you encounter unexpected permission errors even with correct file permissions, check your security policies.

### Windows
- **Long paths:** Windows has a 260-character path limit by default. If you encounter "Path too long" errors, enable long path support via Group Policy or Registry.
- **Antivirus interference:** Some antivirus software may slow down thegent's execution or block its background processes. Consider adding exclusions for the thegent installation directory.
- **WSL2 path mixing:** When using thegent in WSL2, use `wslpath` to convert between Windows and Unix-style paths.

---

## 4. Provider & OAuth Troubleshooting

### OAuth Failures
**Symptom:** The browser opens, you log in, but the token is not stored or the CLI doesn't recognize it.

**Solutions:**
1. Check token storage: `cat ~/.cli-proxy-api/tokens/*.json`
2. Run with verbose logging: `thegent cliproxy login <provider> --verbose`
3. Check proxy logs: `tail -f ~/.cli-proxy-api/logs/*.log`

### Token Expiry
**Symptom:** You receive "Token expired" or "Unauthorized" errors after a period of use.

**Solutions:**
1. Refresh all tokens: `thegent cliproxy tokens refresh`
2. Check token status: `thegent cliproxy tokens status`
3. Manual re-login: `thegent cliproxy login <provider>`

### API Key Issues (MiniMax, NIM)
**Symptom:** "Invalid API key" error message.

**Solutions:**
1. Re-enter the key: `thegent cliproxy login minimax --force`
2. Verify key in config: `cat ~/.cli-proxy-api/config.toml | grep -A5 minimax`

---

## 5. MCP Server Issues

### Connectivity
If your client (Cursor, Claude Code) cannot find thegent tools:
1. Ensure the server is running: `thegent ps`
2. Restart the server: `thegent cliproxy restart`
3. Check the port: Default is `8317`. Ensure no other service is using it.

---

## 6. Shell Issues (Development)

### Fork Exhaustion
**Symptom**: `Resource temporarily unavailable` errors, can't spawn new processes.

**Solution**:
```bash
# Kill hanging processes
pkill -9 -f "thegent"
pkill -9 -f "python.*thegent"

# Or run the cleanup script
bash scripts/fix_shell_corruption.sh
```

### Shell Corruption
**Symptom**: Commands not found, PATH errors, broken prompts.

**Solution**:
```bash
# Restore from backup
bash scripts/fix_shell_corruption.sh --restore
```

---

## 7. Performance Issues

### Slow Hook Execution
**Symptom**: Hooks take seconds to run.

**Solution**:
```bash
# Clear hook cache
rm -rf ~/.thegent/cache/hooks/*

# Verify Rust tools are installed
which hook-dispatcher
```

---

## 8. Debug Commands

### Enable Debug Mode
```bash
# Run with debug output
thegent --debug serve
thegent --debug run "task"

# Enable hook debug
export THGENT_HOOK_DEBUG=1
```

### View Logs
```bash
# Tail all logs
thegent logs --tail 100

# File system logs
tail -f ~/.thegent/logs/*.log
```

---

## 9. Getting Help

If your issue persists:
1. Check the logs: `thegent logs --tail 100`
2. Open an issue on [GitHub](https://github.com/kooshapari/thegent/issues) with the output of `thegent doctor`.
