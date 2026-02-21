# {{project_name}}

{{project_description}}

## Getting Started

```bash
# Install dependencies
{% if language == "python" -%}
uv sync
{% elif language == "typescript" -%}
pnpm install
{% elif language == "go" -%}
go mod download
{% endif -%}

# Run development server
{% if language == "python" -%}
uv run python -m app
{% elif language == "typescript" -%}
pnpm dev
{% elif language == "go" -%}
go run main.go
{% endif -%}
```

## Documentation

- [API Reference](./api/)
- [Guides](./guides/)
- [Governance Matrix](./governance/POLYGLOT_RUNTIME_DECISION_MATRIX.md)
- [Changelog](../CHANGELOG.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
