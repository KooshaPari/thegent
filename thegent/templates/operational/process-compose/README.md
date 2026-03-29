# Canonical Process-Compose Templates

This directory contains standardized, composable process-compose templates for kush projects. Eliminates scattered, inconsistent process-compose.yaml files across 11+ projects.

## What's Here

| File | Size | Purpose |
|------|------|---------|
| **process-compose.base.yaml** | 9.1K | Foundation: logging, shell, environment, layers 1–5, conventions, reference docs |
| **process-compose.mcp.yml** | 6.0K | MCP server, CLI proxy, control plane, worker pool (thegent, morph, serena) |
| **process-compose.backend.yml** | 7.3K | FastAPI API, workers, scheduler, gRPC, migrations (trace, civ backends) |
| **process-compose.metrics.yml** | 11K | Prometheus, Grafana, Jaeger, Loki, exporters (observability stack) |
| **COMPOSITION_GUIDE.md** | 10K | How to use: compose strategies, port conventions, probe patterns, troubleshooting |
| **README.md** (this file) | — | Quick reference |

## Quick Start

### 1. Start with Base
Every project starts here:
```bash
cp process-compose.base.yaml /path/to/project/process-compose.yaml
```

### 2. Add Layers (from other templates)

**MCP server project?** (thegent, morph, serena)
```bash
# Append MCP services to processes section
cat process-compose.mcp.yml >> /path/to/project/process-compose.yaml
```

**Python backend?** (trace, civ)
```bash
# Append API, workers, migrations
cat process-compose.backend.yml >> /path/to/project/process-compose.yaml
```

**Want observability?** (optional for all)
```bash
# Append Prometheus, Grafana, Jaeger, Loki
cat process-compose.metrics.yml >> /path/to/project/process-compose.yaml
```

### 3. Customize
- Ports: Update environment variables
- Infrastructure: Add postgres, redis, kafka, etc. (patterns in base.yaml)
- Services: Override or extend services in your main file

### 4. Test
```bash
process-compose -f process-compose.yaml up
```

## Project Type → Composition Map

| Project | Type | Files to Use |
|---------|------|--------------|
| **thegent** | MCP server | base + mcp |
| **morph** | MCP server | base + mcp |
| **serena** | MCP server | base + mcp |
| **trace** | Multi-tier backend | base + backend + metrics |
| **civ** | Multi-tier backend | base + backend + metrics |

## Key Conventions

### Logging
- **Global log:** `.process-compose/process-compose.log`
- **Per-service logs:** `.process-compose/logs/<service>.log`
- **Standard format:** JSON for machine-readability

### Restart Policy
```yaml
availability:
  restart: on_failure      # Always restart on crash
  max_restarts: 5          # Max 5 restart attempts
  backoff_seconds: 2       # Wait 2s between restarts
```

### Health Probes
```yaml
# HTTP (APIs, web services)
readiness_probe:
  http_get:
    host: localhost
    port: 8000
    path: /health
  initial_delay_seconds: 5
  period_seconds: 10
  failure_threshold: 3

# Exec (databases, gRPC, custom checks)
readiness_probe:
  exec:
    command: "pg_isready -h localhost -p 5432"
  initial_delay_seconds: 2
  period_seconds: 5
```

### Port Assignments
- **Infrastructure:** 5432 (postgres), 6379 (redis), 7233 (temporal)
- **Application:** 8000–8099 (python), 8100–8199 (go), 9000–9099 (grpc)
- **Observability:** 9090 (prometheus), 3000 (grafana), 16686 (jaeger)
- **Gateway:** 80, 443 (caddy)

## Architecture Layers (base.yaml)

1. **Infrastructure:** Databases, caches, message queues (postgres, redis, kafka)
2. **Orchestration:** Workflow engines, schedulers (temporal, airflow)
3. **Application:** APIs, workers, gRPC services
4. **Observability:** Metrics, tracing, logs (prometheus, grafana, jaeger, loki)
5. **Gateway:** Reverse proxies, load balancers (caddy)

## Extending Templates

### Add a Custom Service
Create in your main `process-compose.yaml`:

```yaml
my-service:
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
  log_location: .process-compose/logs/my-service.log
  environment:
    - "SERVICE_PORT=8765"
```

### Override a Template Service
Redefine in your main file:

```yaml
prometheus:
  environment:
    - "RETENTION=7d"  # Different retention
```

## Troubleshooting

**Service won't start?**
```bash
process-compose logs --follow <service-name>
lsof -i :<port>  # Check port conflicts
```

**Health probe failing?**
- Increase `initial_delay_seconds`
- Test manually: `curl http://localhost:8000/health`
- Check logs

**Port conflict?**
```bash
kill -9 <pid>
# or use a different port
```

## Documentation

- **COMPOSITION_GUIDE.md:** Detailed guide with examples for each project type
- **process-compose.base.yaml:** Extensive inline comments and reference sections
- **Individual templates:** Each `.yml` file has comments explaining services

## References

- Process-compose repo: https://github.com/F1bonacc1/process-compose
- Process-compose docs: https://www.process-compose.dev/
