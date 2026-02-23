# CLI Reference - November 2025

Complete reference for atomsAgent CLI commands.

## Server Commands

### Start Development Server
```bash
atoms-agent server run --reload
```
Starts FastAPI server with auto-reload on file changes. Serves API, docs, and MCP on localhost:8000.

**Options:**
- `--reload` - Auto-reload on file changes (default: true)
- `--host` - Host to bind to (default: 127.0.0.1)
- `--port` - Port to listen on (default: 8000)

### Start Production Server
```bash
atoms-agent server run --host 0.0.0.0 --port 8080
```

## Documentation Commands

### Access Documentation via Wiki
Documentation is automatically served at `/wiki` when running the API server:

```bash
atoms-agent server run --reload
# Then visit: http://localhost:8000/wiki
```

**Wiki Endpoints:**
- `GET /wiki/` - Wiki index (README.md)
- `GET /wiki/{path}` - Wiki page (e.g., `/wiki/guides/CLI_REFERENCE`)
- `GET /wiki/raw/{path}` - Raw markdown file

### Serve Documentation Locally (Standalone)
```bash
atoms-agent docs serve
```
Serves documentation on http://127.0.0.1:8001 (standalone HTTP server)

**Options:**
- `--port` - Port to serve on (default: 8001)
- `--host` - Host to bind to (default: 127.0.0.1)
- `--reload` - Auto-reload on changes (default: true)

### Build Static Documentation
```bash
atoms-agent docs build
```
Builds static HTML documentation.

**Options:**
- `--output` - Output directory (default: docs/build)

### List Documentation Files
```bash
atoms-agent docs list-docs
```
Lists all documentation files in docs/ directory.

## Cloud Run Commands

### Deploy to Google Cloud Run
```bash
atoms-agent cloud-run deploy \
  --project my-project \
  --region us-central1 \
  --service atomsagent
```

**Options:**
- `--project` - GCP Project ID (required)
- `--region` - Cloud Run region (default: us-central1)
- `--service` - Service name (default: atomsagent)
- `--memory` - Memory allocation (default: 2Gi)
- `--cpu` - CPU allocation (default: 2)
- `--max-instances` - Max instances (default: 100)
- `--min-instances` - Min instances (default: 1)
- `--allow-unauthenticated` - Allow unauthenticated access (default: true)

### View Cloud Run Logs
```bash
atoms-agent cloud-run logs --service atomsagent --region us-central1
```

**Options:**
- `--service` - Service name (default: atomsagent)
- `--region` - Cloud Run region (default: us-central1)
- `--limit` - Number of log lines (default: 50)
- `--follow` - Follow logs in real-time

### Describe Cloud Run Service
```bash
atoms-agent cloud-run describe --service atomsagent --region us-central1
```

### Set Up Cloud Run Secrets
```bash
atoms-agent cloud-run setup-secrets --project my-project
```
Interactively creates secrets in Google Secret Manager.

## Testing Commands

### Run All Tests
```bash
atoms-agent test
```

**Options:**
- `--cov` - Generate coverage report
- `--verbose` - Verbose output

### Run Specific Test File
```bash
atoms-agent test tests/unit/test_auth.py
```

## MCP Commands

### List MCP Servers
```bash
atoms-agent mcp list --org <org-id>
```

### Create MCP Server
```bash
atoms-agent mcp create --org <org-id> --name "My MCP" --url "https://..."
```

### Update MCP Server
```bash
atoms-agent mcp update --id <server-id> --enabled false
```

### Delete MCP Server
```bash
atoms-agent mcp delete --id <server-id>
```

## Vertex AI Commands

### List Available Models
```bash
atoms-agent vertex models
```

## Supabase Commands

### Generate Database Models
```bash
atoms-agent supabase generate-models
```

## Prompt Commands

### Show Merged Prompts
```bash
atoms-agent prompt show --org <org-id> --user <user-id>
```

## Global Options

All commands support:
- `--help` - Show help message
- `--version` - Show version

## Examples

### Local Development Setup
```bash
# Start server with docs and MCP
atoms-agent server run --reload

# In another terminal, serve docs separately
atoms-agent docs serve

# Run tests
atoms-agent test --cov
```

### Production Deployment
```bash
# Set up secrets
atoms-agent cloud-run setup-secrets --project my-project

# Deploy to Cloud Run
atoms-agent cloud-run deploy \
  --project my-project \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2

# View logs
atoms-agent cloud-run logs --follow
```

## Troubleshooting

### Command not found
```bash
# Reinstall CLI
uv pip install -e ".[dev]"
```

### Permission denied
```bash
# Ensure gcloud is configured
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Port already in use
```bash
# Use different port
atoms-agent server run --port 9000
atoms-agent docs serve --port 9001
```

