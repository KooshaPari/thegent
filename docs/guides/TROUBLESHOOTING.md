# thegent Troubleshooting Guide

Common issues and solutions for developing and running `thegent`.

## 1. Environment Issues

### `command not found: task`
Install Go Task: `brew install go-task`.

### `direnv` not loading
Ensure `direnv` is installed and hooked into your shell. Run `direnv allow` in the project root.

### Python version mismatch
`thegent` requires Python 3.12+. Use `uv venv --python 3.12` to create a compatible environment.

## 2. CLIProxyAPIPlus Proxy

### Proxy fails to start
Check if the port (default 8317) is already in use: `lsof -i :8317`.
Ensure the binary is in your PATH or `THGENT_CLIPROXY_BINARY` is set correctly in `.env`.

### Authentication Failures
Run `thegent login <provider>` to re-authenticate. Tokens are stored in `~/.cli-proxy-api`.

## 3. MCP Issues

### Cursor cannot connect to MCP
1.  Ensure the server is running: `task dev`.
2.  Verify the health endpoint: `curl http://127.0.0.1:3847/health`.
3.  Check `.cursor/mcp.json` for correct URL.

## 4. Quality Gate Failures

### DX Audit Failures (Module Size)
If `scripts/dx-audit.sh` fails due to module size, you **must** refactor and decompose the large file. See `WARP.md` for decomposition patterns.

### Architectural Boundary Violation
If `tach check` fails, you have introduced an illegal import. Refer to `docs/ARCHITECTURE_LAYERS.md` for the allowed dependency graph.
