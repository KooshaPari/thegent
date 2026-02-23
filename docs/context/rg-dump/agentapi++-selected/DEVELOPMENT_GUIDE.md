# Development Guide

Complete guide for developing atomsAgent locally.

## Environment Setup

### Prerequisites
- Python 3.11+ (3.13 compatible)
- uv or pip
- Git
- Google Cloud credentials (for Vertex AI)

### Installation

```bash
# Clone repository
git clone https://github.com/KooshaPari/agentapi.git
cd agentapi

# Install dependencies
uv pip install -e ".[dev]"

# Verify installation
atoms-agent --help
```

### Configuration

```bash
# Copy secrets template
cp config/secrets.example.yml config/secrets.yml

# Edit with your credentials
# - ATOMS_SECRET_AUTHKIT_JWKS_URL
# - ATOMS_SECRET_SUPABASE_URL
# - ATOMS_SECRET_SUPABASE_KEY
# - ATOMS_SECRET_VERTEX_PROJECT_ID
# - ATOMS_SECRET_VERTEX_LOCATION
```

## Development Workflow

### Running Tests

```bash
# All tests with coverage
uv run pytest tests/ -v --cov

# Specific test file
uv run pytest tests/unit/test_auth.py -v

# Parallel execution
uv run pytest tests/ -n auto

# Watch mode
uv run pytest-watch tests/
```

### Code Quality

```bash
# Lint with Ruff
uv run ruff check src/

# Format code
uv run ruff format src/

# Type check
uv run mypy src/atomsAgent --strict

# All checks
uv run ruff check src/ && uv run mypy src/atomsAgent --strict
```

### Running Server

```bash
# Development server with reload
atoms-agent server run --reload

# Production-like server
atoms-agent server run --host 0.0.0.0 --port 8000

# Direct uvicorn
uv run uvicorn atomsAgent.main:app --reload
```

## Architecture

### Directory Structure

```
src/atomsAgent/
├── api/              # FastAPI routes
├── auth/             # Authentication & permissions
├── cache/            # Caching services
├── cli/              # CLI commands
├── db/               # Database layer
├── mcp/              # MCP integration
├── services/         # Business logic
├── settings/         # Configuration
└── main.py           # FastAPI app factory
```

### Key Modules

- **auth/permission_cache.py** - Permission caching (4-5x faster)
- **services/claude_client.py** - Vertex AI Claude wrapper
- **services/prompts.py** - Multi-level prompt orchestration
- **db/repositories/** - Data access layer

## Performance Optimization

### Permission Caching
- 5-minute TTL cache
- 4-5x faster permission checks
- 80% database query reduction

### Query Optimization
- Use asyncio.gather() for parallel queries
- Implement query batching
- Add database indexes

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock external services
- Use pytest fixtures

### Integration Tests
- Test API routes
- Test service interactions
- Use test database

### Coverage Target
- Aim for >80% coverage
- Focus on critical paths
- Use `--cov` flag

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use Python Debugger
```python
import pdb; pdb.set_trace()
```

### Check Logs
```bash
# View application logs
tail -f logs/app.log
```

## Common Issues

### Import Errors
- Ensure `uv pip install -e ".[dev]"` completed
- Check Python version: `python --version`
- Verify PYTHONPATH includes src/

### Database Connection
- Check Supabase credentials in config/secrets.yml
- Verify network connectivity
- Check database URL format

### Vertex AI Errors
- Verify Google Cloud credentials
- Check project ID and location
- Ensure Vertex AI API enabled

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and test: `uv run pytest tests/`
3. Lint and format: `uv run ruff check src/ && uv run ruff format src/`
4. Type check: `uv run mypy src/atomsAgent --strict`
5. Commit with clear message
6. Push and create pull request

## Resources

- [Architecture](../architecture/ARCHITECTURE.md)
- [API Reference](../api/API_REFERENCE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
- [Performance Tuning](./PERFORMANCE_TUNING.md)

