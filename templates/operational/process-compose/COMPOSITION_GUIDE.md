# Process-Compose Template Composition Guide

This guide explains how to use the canonical process-compose templates to build deployment configurations across kush projects.

## Quick Start

1. **Choose your project type** from the table below
2. **Copy the recommended base files** to your project
3. **Customize** environment variables and service-specific settings
4. **Test** with `process-compose -f process-compose.yaml up`

## Template Files

| File | Purpose | Project Types |
|------|---------|--------------|
| `process-compose.base.yaml` | Canonical base structure, conventions, reference docs | All |
| `process-compose.mcp.yml` | MCP server, proxy, control plane, worker pool | thegent, morph, serena |
| `process-compose.backend.yml` | FastAPI, workers, schedulers, migrations | trace, civ backends |
| `process-compose.metrics.yml` | Prometheus, Grafana, Jaeger, Loki, exporters | All (observability optional) |

## Project Types & Composition Strategies

### 1. MCP Server Projects (thegent, morph, serena)

**What it is:** Python FastMCP server with bundled CLI proxy, governance control plane, worker pool.

**Files to use:**
- `process-compose.base.yaml` (start here)
- `process-compose.mcp.yml` (append or include)
- `process-compose.metrics.yml` (optional: for observability)

**How to compose:**

```bash
# Copy base as your project file
cp process-compose.base.yaml /path/to/project/process-compose.yaml

# Append MCP services to processes section
cat process-compose.mcp.yml >> /path/to/project/process-compose.yaml

# Optional: append metrics services
cat process-compose.metrics.yml >> /path/to/project/process-compose.yaml
```

**Customize:**
- Ports: Update `THGENT_MCP_PORT`, `THGENT_CLIPROXY_PORT`, `THGENT_CONTROL_PLANE_PORT`
- Worker pool: Set `THGENT_WORKER_POOL_SIZE` (default: 4)
- MCP mounts: Enable tool mounts by setting `THGENT_MCP_MOUNT_*=1`

**Example:**
```yaml
version: "0.5"
log_location: .process-compose/process-compose.log

environment:
  - PYTHONUNBUFFERED=1
  - THGENT_MCP_PORT=3847
  - THGENT_CLIPROXY_PORT=8317
  - THGENT_WORKER_POOL_SIZE=4

processes:
  # Include all services from process-compose.mcp.yml (server, control-plane, worker-pool, serena)
  server: { ... }
  control-plane: { ... }
  worker-pool: { ... }
  serena: { ... }
```

### 2. Python Backend Projects (trace, civ, etc.)

**What it is:** Multi-tier backend stack: infrastructure (Postgres, Redis), FastAPI HTTP API, async workers, optional gRPC.

**Files to use:**
- `process-compose.base.yaml` (start here)
- `process-compose.backend.yml` (append or include for app services)
- `process-compose.metrics.yml` (optional: for observability)
- Custom infrastructure services (manually add Postgres, Redis, etc. from base patterns)

**How to compose:**

```bash
# Copy base
cp process-compose.base.yaml /path/to/project/process-compose.yaml

# In the processes section, add infrastructure (Layer 1):
# - postgres (with pg_isready probe)
# - redis (with redis-cli ping probe)
# - neo4j, nats, temporal, etc. (as needed)

# Append backend services (Layer 3):
cat process-compose.backend.yml >> /path/to/project/process-compose.yaml
```

**Customize:**
- API port: Set `PORT=8000` (or your chosen port)
- Workers: Set `WORKERS=4` and `TASK_TIMEOUT=300`
- Database: Set `DATABASE_URL`, `REDIS_URL`, `NATS_URL`
- Migrations: Enable or disable the `migrations` service based on your ORM

**Example:**
```yaml
version: "0.5"
log_location: .process-compose/process-compose.log

environment:
  - PYTHONUNBUFFERED=1
  - DEBUG=false

processes:
  # Layer 1: Infrastructure
  postgres:
    command: "bash scripts/shell/postgres-if-not-running.sh"
    # ...

  redis:
    command: "bash scripts/shell/redis-if-not-running.sh"
    # ...

  # Layer 3: Application (from process-compose.backend.yml)
  api:
    command: |
      python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      postgres:
        condition: process_healthy
      redis:
        condition: process_healthy
    # ...

  worker:
    command: |
      python -m celery -A app.celery_app worker --loglevel=info
    depends_on:
      redis:
        condition: process_healthy
    # ...
```

### 3. Multi-Service Stack (trace, civ with full observability)

**What it is:** Complex full stack: infrastructure → orchestration → backend → gateway → observability.

**Files to use:**
- `process-compose.base.yaml` (foundation)
- `process-compose.backend.yml` (application layer)
- `process-compose.metrics.yml` (observability layer)
- Custom services for infrastructure and orchestration

**How to compose:**

```bash
# Start with base
cp process-compose.base.yaml /path/to/project/process-compose.yaml

# Add infrastructure (Layer 1): postgres, redis, nats, temporal, jaeger, vault, minio, etc.
# Add orchestration (Layer 2): temporal, prometheus, loki, promtail
# Add application (Layer 3): api, workers, frontend, python-backend, go-backend
# Add gateway (Layer 5): caddy, grafana
```

**Dependency flow:**
```
Infrastructure (postgres, redis, nats, temporal)
    ↓
Observability (prometheus, jaeger, loki, promtail)
    ↓
Application (api, workers, gRPC)
    ↓
Gateway (caddy, grafana)
```

## Port Assignment Conventions

Use these standard ports to avoid conflicts:

### Infrastructure
| Service | Port |
|---------|------|
| Postgres | 5432 |
| Redis | 6379 |
| Neo4j (Bolt) | 7687 |
| Neo4j (HTTP) | 7474 |
| Nats | 4222 (client), 8222 (HTTP) |
| Kafka | 9092 |

### Orchestration
| Service | Port |
|---------|------|
| Temporal gRPC | 7233 |
| Temporal UI | 8233 |

### Application
| Service | Port |
|---------|------|
| Python API | 8000–8099 |
| Go Backend | 8100–8199 |
| gRPC | 9000–9099 |
| Frontend (Vite) | 5173 |

### Observability
| Service | Port |
|---------|------|
| Prometheus | 9090 |
| Grafana | 3000 |
| Jaeger UI | 16686 |
| Loki | 3100 |
| Node Exporter | 9100 |
| Postgres Exporter | 9187 |
| Redis Exporter | 9121 |
| AlertManager | 9093 |

### Gateway
| Service | Port |
|---------|------|
| Caddy | 80, 443, 4000 (management) |

## Health Probe Patterns

### HTTP Probes (Most Common)
For REST APIs, use HTTP GET to `/health` endpoint:

```yaml
readiness_probe:
  http_get:
    host: localhost
    port: 8000
    path: /health
  initial_delay_seconds: 5
  period_seconds: 10
  timeout_seconds: 5
  success_threshold: 1
  failure_threshold: 3
```

### Exec Probes (Databases, gRPC, Custom Checks)

**PostgreSQL:**
```yaml
readiness_probe:
  exec:
    command: "pg_isready -h localhost -p 5432 -U username"
```

**Redis:**
```yaml
readiness_probe:
  exec:
    command: "redis-cli -h localhost -p 6379 ping"
```

**gRPC (port check):**
```yaml
readiness_probe:
  exec:
    command: "nc -z localhost 9092"
```

**Service running check:**
```yaml
readiness_probe:
  exec:
    command: sh
    args: ["-c", "ps aux | grep '[s]ervice-name' || exit 1"]
```

## Restart Policy Patterns

### Always Restart (Typical)
For resilient background services:

```yaml
availability:
  restart: on_failure
  max_restarts: 5
  backoff_seconds: 2
```

### No Restart (One-Time Tasks)
For migrations, seeds, or validators:

```yaml
availability:
  restart: no
```

### Aggressive Retry (Critical Services)
For infrastructure that must stay up:

```yaml
availability:
  restart: on_failure
  max_restarts: 10
  backoff_seconds: 1
```

## Dependency Patterns

### Wait for Service to Be Healthy
```yaml
depends_on:
  postgres:
    condition: process_healthy
  redis:
    condition: process_healthy
```

### Start After Service (Don't Wait)
```yaml
depends_on:
  some-service:
    condition: process_started
```

## Environment Variable Patterns

### Global Variables (Applied to All Services)
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_FORMAT=json
  - DEBUG=false
```

### Service-Specific Variables (Appended to Global)
```yaml
api:
  environment:
    - "PORT=8000"
    - "WORKERS=4"
    - "DEBUG=${DEBUG:-false}"  # Use global or default to false
```

## Extending & Customizing Templates

### Add a Custom Service

1. Choose the appropriate layer (1–5 based on base.yaml)
2. Follow the standard format: command, working_dir, availability, readiness_probe, log_location, environment
3. Add dependencies if needed
4. Document the service purpose and configuration

**Example:**
```yaml
my-custom-service:
  command: "python my_service.py"
  working_dir: .
  availability:
    restart: on_failure
    max_restarts: 5
    backoff_seconds: 2
  readiness_probe:
    http_get:
      host: localhost
      port: 8765
      path: /health
    initial_delay_seconds: 5
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
  log_location: .process-compose/logs/my-custom-service.log
  environment:
    - "SERVICE_PORT=8765"
    - "DEBUG=false"
```

### Override a Template Service

To customize a service from a template file, redefine it in your main `process-compose.yaml`:

```yaml
# This overrides the Prometheus service from process-compose.metrics.yml
prometheus:
  command: |
    prometheus \
      --config.file=custom-prometheus.yml \
      --storage.tsdb.path=.prometheus-custom \
      --web.enable-lifecycle
  environment:
    - "RETENTION=7d"  # Override retention
```

### Conditional Service Inclusion

Use shell wrappers or `if`-based commands to conditionally start services:

```yaml
optional-service:
  command: |
    if [ "${ENABLE_OPTIONAL_SERVICE:-0}" = "1" ]; then
      exec python optional_service.py
    else
      exec sleep infinity
    fi
```

## Troubleshooting

### Service won't start
1. Check logs: `process-compose logs --follow <service-name>`
2. Verify port availability: `lsof -i :<port>`
3. Check dependencies are healthy: `process-compose process list`

### Health probe failing
1. Test manually: `curl http://localhost:<port>/health` (HTTP) or `nc -z localhost <port>` (exec)
2. Increase `initial_delay_seconds` if service takes time to start
3. Check logs for errors

### Port conflicts
1. Use `lsof -i :<port>` to find what's using the port
2. Kill the process: `kill -9 <pid>` or use `process-compose process stop`
3. Change the port in environment variables and re-start

## References

- Base template: `process-compose.base.yaml` (extensive reference comments)
- MCP services: `process-compose.mcp.yml` (MCP server + ecosystem)
- Backend services: `process-compose.backend.yml` (FastAPI + workers)
- Observability: `process-compose.metrics.yml` (Prometheus, Grafana, Jaeger, Loki)
- Official process-compose docs: https://github.com/F1bonacc1/process-compose
