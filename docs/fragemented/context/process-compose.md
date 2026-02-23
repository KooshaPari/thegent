# Process Compose: Service Orchestration Reference

> Definitive reference for process-compose as used in thegent. Process Compose is a YAML-based process orchestrator (alternative to goreman/overmind) with built-in TUI, health checks, process dependencies, and REST API.
>
> Last updated: 2026-02-20. Source: thegent/process-compose.yaml configuration and official process-compose documentation.

---

## What is Process Compose

Process Compose is a lightweight, YAML-driven process orchestrator written in Go. It manages the lifecycle of multiple processes as a unified system, with native support for:

- **Process definitions** - Command, arguments, working directory
- **Process dependencies** - Explicit ordering: "B waits for A to be ready"
- **Health checks** - HTTP probes, exec probes, port availability
- **TUI monitoring** - Real-time terminal UI showing process status
- **REST API** - Programmatic control (start/stop/status)
- **Log aggregation** - Unified logs with per-process filtering
- **Environment management** - Shared environment, per-process overrides

**Why Process Compose for thegent**: Replaces manual shell scripts and systemd/supervisor for local dev. Simpler than Docker Compose (no containers), more feature-rich than foreman (Go instead of Ruby, better error handling).

---

## Installation

```bash
# macOS (Homebrew)
brew install process-compose

# Linux / Download
curl -L https://github.com/F1bonacc1/process-compose/releases/download/v[VERSION]/process-compose_[VERSION]_linux_amd64.tar.gz \
  | tar xz
```

**Verify installation:**
```bash
process-compose --version
```

---

## Core Concepts

### Processes

A process is a unit of work: an executable command with configuration.

```yaml
processes:
  server:
    command: python3
    args:
      - -m
      - thegent.main
      - serve
    working_dir: .
```

### Process Lifecycle

```
stopped → starting → running → (health checks) → healthy/unhealthy → stopping → stopped
```

### Readiness Probes

Process Compose waits for readiness before considering a process "ready" for dependents.

**HTTP probe (most common):**
```yaml
readiness_probe:
  http_get:
    host: 127.0.0.1
    port: 8000
    path: /health
  initial_delay_seconds: 2
  period_seconds: 10
  timeout_seconds: 5
  success_threshold: 1
  failure_threshold: 3
```

Process is "ready" when HTTP GET `/health` returns 2xx status.

**Exec probe (run a command):**
```yaml
readiness_probe:
  exec:
    command: sh
    args: ["-c", "test -f /tmp/ready.flag"]
  initial_delay_seconds: 1
  period_seconds: 5
```

Process is "ready" when command exits 0.

**TCP port probe:**
```yaml
readiness_probe:
  tcp_socket:
    host: 127.0.0.1
    port: 5432
  initial_delay_seconds: 2
```

Process is "ready" when port accepts connection.

### Restart Policies

Define behavior when a process exits.

```yaml
availability:
  restart: on_failure      # Restart if exit code != 0
  max_restarts: 10         # Max restart attempts
  backoff_seconds: 1       # Wait before restart
```

**Restart modes:**
- `no` - Never restart
- `always` - Always restart, even if exit code 0
- `on_failure` - Restart only if non-zero exit code
- `on_failure_with_backoff` - Exponential backoff on restart

### Process Dependencies

Control startup order; Process Compose waits for dependencies to be "ready".

```yaml
processes:
  db:
    command: postgres
    readiness_probe: ...

  api:
    command: node app.js
    depends_on:
      db:
        condition: process_healthy  # or process_started
    readiness_probe: ...
```

Process Compose guarantees: DB passes health check before API starts.

---

## thegent Configuration (process-compose.yaml)

### Overview Structure

```yaml
version: "0.5"
log_location: .process-compose/process-compose.log
log_level: info

environment:
  - PYTHONUNBUFFERED=1
  - PYTHONPATH=src
  - THGENT_MCP_HOST=127.0.0.1
  - THGENT_MCP_PORT=3847
  - ... (service-specific env vars)

processes:
  server:
    # MCP server (daemon)
  control-plane:
    # Control plane (governance engine)
  serena:
    # Optional: Serena integration (code search/navigation)
```

### thegent Processes

#### 1. server (MCP Server)

Core daemon: LLM routing, tool execution, session management.

```yaml
server:
  command: python3
  args:
    - -m
    - thegent.main
    - serve
    - --host=127.0.0.1
    - --port=3847
  working_dir: .
  availability:
    restart: on_failure
    max_restarts: 10
    backoff_seconds: 1
  readiness_probe:
    http_get:
      host: 127.0.0.1
      port: 3847
      path: /health
    initial_delay_seconds: 2
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  log_location: .process-compose/logs/server.log
  log_length: 5000
```

**Readiness check**: HTTP GET `/health` returns 200 ↔ MCP server ready for RPC calls.

**Typical lifecycle**:
1. Process starts
2. Python imports thegent modules (may take 2-3s on first run)
3. Server binds to 127.0.0.1:3847
4. Health check HTTP GET succeeds
5. Process marked "ready"
6. Control-plane can now connect

**Logs**: `.process-compose/logs/server.log` (last 5000 lines)

#### 2. control-plane (Governance Engine)

Separate daemon managing policies, hooks, approvals.

```yaml
control-plane:
  command: python3
  args:
    - -m
    - thegent.main
    - control-plane
    - serve
    - --port=3849
  working_dir: .
  availability:
    restart: on_failure
    max_restarts: 10
    backoff_seconds: 1
  readiness_probe:
    http_get:
      host: 127.0.0.1
      port: 3849
      path: /health
    initial_delay_seconds: 2
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  log_location: .process-compose/logs/control-plane.log
```

**Readiness check**: Similar to server; HTTP `/health` on port 3849.

**Design note**: Separate from server for isolation and independent scaling (future).

#### 3. serena (Optional: Code Search)

Serena provides code search/navigation via MCP. Disabled by default.

```yaml
serena:
  command: sh
  args:
    - -c
    - |
      if [ "${THGENT_MCP_MOUNT_SERENA:-0}" = "1" ]; then
        exec uvx --from 'git+https://github.com/oraios/serena' \
          serena start-mcp-server --transport sse --port 3848 \
          --context ide --project-from-cwd --open-web-dashboard false
      else
        exec sleep infinity  # Prevents restart loops when disabled
      fi
  availability:
    restart: on_failure
    max_restarts: 5
    backoff_seconds: 2
  readiness_probe:
    exec:
      command: sh
      args: ["-c", "test \"${THGENT_MCP_MOUNT_SERENA:-0}\" != 1 || nc -z 127.0.0.1 3848"]
    initial_delay_seconds: 5
    period_seconds: 10
  log_location: .process-compose/logs/serena.log
```

**Design note**: Serena is optional; `if [ ... ] = "1"` gate allows disabling without restart loops.

**When disabled** (`THGENT_MCP_MOUNT_SERENA=0`): Process runs `sleep infinity` (does nothing, doesn't restart).

**When enabled** (`THGENT_MCP_MOUNT_SERENA=1`): Starts MCP server on port 3848.

---

## Environment Variables

Global environment vars (inherited by all processes) configured at top level:

```yaml
environment:
  - PYTHONUNBUFFERED=1           # Disable Python output buffering
  - PYTHONPATH=src               # Add src/ to Python import path
  - THGENT_MCP_HOST=127.0.0.1    # MCP server bind address
  - THGENT_MCP_PORT=3847         # MCP server port
  - THGENT_CLIPROXY_PORT=8317    # CLI proxy (for HTTP requests)
  - THGENT_CLIPROXY_ADAPTER=1    # Enable adapter mode
  - THGENT_CONTROL_PLANE_PORT=3849
  - THGENT_CONTROL_PLANE_URL=http://127.0.0.1:3849
  - THGENT_BUNDLE_PROXY=1        # MCP server spawns CLI proxy internally
  - THGENT_RELOAD=${THGENT_RELOAD:-0}  # Hot reload (0=disabled)
  - THGENT_MCP_MOUNT_PLAYWRIGHT=0      # Disable Playwright MCP tool
  - THGENT_MCP_MOUNT_SERENA=0          # Disable Serena integration
  - THGENT_MCP_MOUNT_OCTOCODE=0        # Disable Octocode integration
  - THGENT_SERENA_URL=http://127.0.0.1:3848/mcp
```

**Override at runtime:**
```bash
THGENT_MCP_MOUNT_SERENA=1 process-compose up
```

---

## Common Commands

### Start All Processes

```bash
process-compose up
```

**Output:**
```
✓ server        | Started, waiting for readiness...
✓ control-plane | Started, waiting for readiness...
✓ serena        | Sleeping (disabled)

All processes ready
Ctrl+C to stop
```

Press Ctrl+C to stop all processes.

### Stop All Processes

```bash
process-compose down
```

### View Logs

**All processes:**
```bash
process-compose logs
```

**Specific process:**
```bash
process-compose logs server
```

**Follow (tail) mode:**
```bash
process-compose logs --follow server
```

**Filter by time:**
```bash
process-compose logs --since 5m server
```

### Check Process Status

```bash
process-compose ps
```

**Output:**
```
NAME           PID     STATUS      DURATION
server         1234    running     12:34
control-plane  1235    running     12:30
serena         1236    sleeping    12:34
```

### Restart a Process

```bash
process-compose restart server
```

### Kill a Process (Manual Restart)

```bash
process-compose kill server
```

Process Compose will restart per `availability.restart` policy.

### Reload Configuration

```bash
process-compose reload
```

Applies changes to `process-compose.yaml` without full shutdown (requires `THGENT_RELOAD=1`).

---

## REST API

Process Compose exposes a REST API (by default on port 5000) for programmatic control.

### Endpoints

#### GET /processes

List all processes with status.

```bash
curl http://localhost:5000/processes
```

**Response:**
```json
{
  "processes": [
    {
      "name": "server",
      "pid": 1234,
      "status": "running",
      "uptime_seconds": 754,
      "restart_count": 0
    },
    {
      "name": "control-plane",
      "pid": 1235,
      "status": "running",
      "uptime_seconds": 730,
      "restart_count": 0
    }
  ]
}
```

#### POST /processes/{name}/stop

Stop a process by name.

```bash
curl -X POST http://localhost:5000/processes/server/stop
```

#### POST /processes/{name}/start

Start a stopped process.

```bash
curl -X POST http://localhost:5000/processes/server/start
```

#### POST /processes/{name}/restart

Restart a process.

```bash
curl -X POST http://localhost:5000/processes/server/restart
```

#### GET /processes/{name}/logs

Fetch logs for a process.

```bash
curl "http://localhost:5000/processes/server/logs?lines=100"
```

**Query params:**
- `lines=N` - Last N lines
- `follow=true` - Stream logs (EventStream)

### Example: Health Check Integration

```bash
# Check if MCP server is healthy
curl -f http://localhost:5000/processes/server/logs?lines=1 && \
  echo "Server is healthy" || \
  echo "Server is unhealthy"
```

---

## TUI Interface

When running `process-compose up`, a terminal UI appears.

**Features:**

- **Process list pane** - Shows all processes, status, PID, uptime
- **Log pane** - Real-time logs for selected process
- **Navigation:**
  - Arrow keys: Select process
  - Enter: View detailed logs
  - L: View logs only
  - Ctrl+C: Shutdown all

**Keyboard shortcuts:**
| Key | Action |
|-----|--------|
| ↑/↓ | Select process |
| ← / → | Switch panes |
| L | Log view |
| S | Status view |
| R | Restart selected |
| K | Kill selected |
| Ctrl+C | Shutdown all |

---

## Health Checks: Deep Dive

### HTTP Probe Behavior

```yaml
readiness_probe:
  http_get:
    host: 127.0.0.1
    port: 8000
    path: /health
  initial_delay_seconds: 2      # Wait 2s after process start
  period_seconds: 10            # Check every 10s
  timeout_seconds: 5            # Fail if no response in 5s
  success_threshold: 1          # 1 success → "ready"
  failure_threshold: 3          # 3 failures → "unhealthy"
```

**Timeline:**
```
T=0s: Process starts
T=2s: First health check attempt
      GET http://127.0.0.1:8000/health
      ✓ Returns 200 → success_threshold--
      → ready (success_threshold = 1)

T=12s: Second health check (period = 10s)
       ✓ Returns 200 → still ready

T=25s: Third health check
       ✗ Returns 503 or timeout → failure_threshold--
       ✗ Returns 503 again → failure_threshold--
       ✗ Returns 503 again → failure_threshold = 0
       → unhealthy, trigger restart policy
```

### Exec Probe Behavior

```yaml
readiness_probe:
  exec:
    command: sh
    args: ["-c", "test -f /tmp/ready && [ $(cat /tmp/ready) = 'yes' ]"]
```

Process is "ready" when the command exits 0.

**Common patterns:**
```bash
# Check for file existence
test -f /tmp/server.ready

# Check for port listening
nc -z 127.0.0.1 8000

# Conditional based on env var
[ "${ENABLED:-0}" = "1" ]
```

### Failed Probe Handling

When a probe fails repeatedly:

```
failure_threshold = 3
Attempt 1: FAIL (failures = 1)
Attempt 2: FAIL (failures = 2)
Attempt 3: FAIL (failures = 3 → threshold reached)
  → Process marked unhealthy
  → Restart policy triggered
  → availability.restart = on_failure
  → Process killed and restarted
```

---

## Dependency Management

### Process Dependencies with Conditions

```yaml
processes:
  db:
    command: postgres
    readiness_probe: ...

  api:
    command: node app.js
    depends_on:
      db:
        condition: process_healthy
```

**Conditions:**
- `process_healthy` - Wait for readiness probe to pass
- `process_started` - Wait for process to just start (no health check)

**Typical use:**
```yaml
api:
  depends_on:
    db:
      condition: process_healthy  # DB must be ready
    cache:
      condition: process_started  # Cache can be starting
```

### Dependency Chain Behavior

```
Start order:
1. db (no deps)
2. api depends_on: db → waits for db to be healthy
3. worker depends_on: api → waits for api to be healthy

Startup sequence:
db starts → db healthy ✓
api starts → api healthy ✓
worker starts → ready

Shutdown sequence (reverse):
worker stopped
api stopped
db stopped
```

---

## Log Management

### Log Locations

```
.process-compose/process-compose.log   # Overall log
.process-compose/logs/
  ├─ server.log
  ├─ control-plane.log
  └─ serena.log
```

### Log Configuration

```yaml
log_location: .process-compose/process-compose.log
log_level: info                # debug, info, warning, error

processes:
  server:
    log_location: .process-compose/logs/server.log
    log_length: 5000           # Keep last 5000 lines
```

### Viewing Logs

**CLI:**
```bash
process-compose logs server
process-compose logs --follow server      # tail -f
process-compose logs --since 5m server    # Last 5 minutes
process-compose logs --lines 100 server   # Last 100 lines
```

**REST API:**
```bash
curl http://localhost:5000/processes/server/logs?lines=50
curl "http://localhost:5000/processes/server/logs?lines=50&follow=true"
```

---

## Practical Examples

### Example 1: Check if thegent is Ready

```bash
#!/bin/bash

# Wait for server to be healthy
timeout 30 bash -c '
  until curl -f http://127.0.0.1:3847/health 2>/dev/null; do
    echo "Waiting for server..."
    sleep 1
  done
'

if [ $? -eq 0 ]; then
  echo "thegent is ready"
else
  echo "thegent failed to start"
  exit 1
fi
```

### Example 2: Enable Serena at Runtime

```bash
# Restart with Serena enabled
THGENT_MCP_MOUNT_SERENA=1 process-compose restart serena
```

### Example 3: Monitor Process Health

```bash
#!/bin/bash

while true; do
  response=$(curl -s http://localhost:5000/processes)
  unhealthy=$(echo "$response" | jq '.processes[] | select(.status != "running")')

  if [ -n "$unhealthy" ]; then
    echo "Unhealthy processes detected:"
    echo "$unhealthy" | jq .
  fi

  sleep 30
done
```

### Example 4: Collect Logs Before Shutdown

```bash
#!/bin/bash

# Save logs before shutdown
mkdir -p logs-backup
process-compose logs server > logs-backup/server.log
process-compose logs control-plane > logs-backup/control-plane.log

# Shutdown
process-compose down
```

---

## Troubleshooting

### Process Keeps Restarting

**Symptom**: Process restarts every few seconds

**Check**: Health probe configuration

```bash
# View logs
process-compose logs server

# Check if health endpoint is responding
curl http://127.0.0.1:3847/health -v
```

**Common causes:**
- Health check endpoint not implemented
- Health check timeout too short
- Application startup takes longer than `initial_delay_seconds`

**Fix**:
```yaml
readiness_probe:
  http_get: ...
  initial_delay_seconds: 5  # Increase initial delay
  timeout_seconds: 10       # Increase timeout
  period_seconds: 15        # Space out checks
```

### Process Never Becomes "Ready"

**Symptom**: Process starts but "ready" status never achieved

**Cause**: Health check failing

```bash
# Manually test health check
curl -v http://127.0.0.1:3847/health

# View logs for errors
process-compose logs --follow server
```

**Check**:
1. Is process actually listening on the configured port?
2. Does health endpoint exist?
3. Is firewall blocking access?

### Multiple Processes Failing

**Symptom**: Multiple processes keep restarting

**Check dependency chain**:
```yaml
# If A depends_on B, but B fails:
# A will wait forever, then fail
```

**Fix**: Check logs for the first failing process.

```bash
process-compose logs control-plane
```

### Logs Are Truncated

**Symptom**: Can't see historical logs; only recent logs available

**Cause**: `log_length` limit reached; old lines deleted

**View current limit**:
```yaml
processes:
  server:
    log_length: 5000   # Keep max 5000 lines
```

**Increase if needed**:
```yaml
    log_length: 50000  # Keep more history
```

---

## Best Practices

### 1. Always Set Readiness Probes

Never omit readiness probes. Without them, Process Compose can't determine when a process is "ready," leading to race conditions.

```yaml
readiness_probe:
  http_get:
    host: 127.0.0.1
    port: 8000
    path: /health
  initial_delay_seconds: 2
```

### 2. Use Realistic Timeouts

Health check timeouts should match actual response times:

```yaml
timeout_seconds: 5        # Reasonable for local services
failure_threshold: 3      # Allow 3 transient failures
```

### 3. Version Your Configuration

Track `process-compose.yaml` in git; review changes carefully.

```bash
git diff process-compose.yaml
```

### 4. Logs Are Your Debugging Tool

Always check logs when troubleshooting:

```bash
process-compose logs --follow server
```

### 5. Use Environment Variables for Configuration

Avoid hardcoding; use env vars for extensibility:

```yaml
environment:
  - THGENT_MCP_PORT=${THGENT_MCP_PORT:-3847}
  - THGENT_LOG_LEVEL=${THGENT_LOG_LEVEL:-info}
```

### 6. Test Startup & Shutdown

Ensure graceful shutdown:

```bash
process-compose up
# ... verify services are running
process-compose down
# ... verify clean shutdown (no zombie processes)
```

---

## Integration with thegent

### Starting thegent Services

```bash
# From project root
process-compose -f process-compose.yaml up

# Or via thegent CLI (recommended)
thegent mcp up
```

### Stopping thegent Services

```bash
process-compose down

# Or via thegent CLI
thegent mcp down
```

### Enabling Optional Tools

```bash
# Enable Serena at startup
THGENT_MCP_MOUNT_SERENA=1 process-compose up

# Or restart just Serena
THGENT_MCP_MOUNT_SERENA=1 process-compose restart serena
```

### Checking Service Health

```bash
# CLI
process-compose ps

# REST API
curl http://localhost:5000/processes

# Manual health check
curl http://127.0.0.1:3847/health
curl http://127.0.0.1:3849/health
```

---

## Sources

- **Process Compose GitHub**: https://github.com/F1bonacc1/process-compose
- **Process Compose Documentation**: https://f1bonacc1.github.io/process-compose/
- **thegent process-compose.yaml**: `/thegent/process-compose.yaml`
- **thegent Service Architecture**: `AGENTS.md`, `ADR*.md`

---

*Reference valid as of 2026-02-20. Process Compose v1.8.0+*
