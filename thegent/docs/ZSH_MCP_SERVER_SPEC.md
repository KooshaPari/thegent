# Specification: Zsh Context Bridge MCP Server (Z-MCP)

## 1. Objective
To provide AI agents with direct, high-performance access to the internal state of a Zsh shell session using the Model Context Protocol (MCP). This enables agents to understand the user's environment (aliases, local functions, environment variables) without the overhead of forking subshells or scraping text.

## 2. Architecture
The Z-MCP server is a lightweight daemon (implemented in Go or Python) that interacts with a "Shadow Zsh" process. It leverages the `zsh/parameter` and `zsh/stat` modules to introspect the shell's memory directly.

### 2.1 Transport
- **Transport**: stdio (Primary) or HTTP/SSE (Secondary).
- **Format**: JSON-RPC 2.0 (MCP Standard).

### 2.2 Integration
- **Host**: Can be run standalone or integrated into `agentopd` (kagentop backend).
- **Shell Link**: Sourced in `.zshrc` to establish the communication bridge.

## 3. Toolset Definitions

### `zsh_get_aliases`
- **Description**: Returns a map of all defined Zsh aliases in the current session.
- **Output**: `{ [alias_name: string]: string }`

### `zsh_get_functions`
- **Description**: Lists defined functions and optionally retrieves their source code.
- **Arguments**:
  - `include_body`: (boolean) Whether to include the function definition body.
- **Output**: `{ [func_name: string]: { body?: string, defined_in?: string } }`

### `zsh_get_environment`
- **Description**: Returns all exported environment variables.
- **Output**: `{ [var_name: string]: string }`

### `zsh_execute_command`
- **Description**: Executes a command within the Zsh context (applying aliases and functions).
- **Arguments**:
  - `command`: (string) The command to run.
  - `cwd`: (string, optional) Directory to execute in.
- **Output**: `{ stdout: string, stderr: string, exit_code: number }`

### `zsh_get_history`
- **Description**: Retrieves recent command history, integrated with **Atuin** and **DejaVu**.
- **Arguments**:
  - `limit`: (number) Max items to return.
  - `search`: (string, optional) Filter by keyword.
- **Output**: `Array<{ timestamp: number, command: string, duration?: number, directory?: string }>`

## 4. Performance Targets
- **Introspection Latency**: < 5ms (via `zsh/parameter`).
- **Response Size**: Compressed JSON for large function maps.
- **Zero-Fork**: No `fork()` or `exec()` calls for state retrieval.

## 5. Security
- **Sandboxing**: Restrict `execute_command` via the ShareCLI Harness rules.
- **Auth**: Only authorized MCP clients (e.g., `codex`, `kagentop`) can connect.
