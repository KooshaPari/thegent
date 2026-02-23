# API

The API section is the index for generated and hand-authored API docs.

## Current Surface

- CLI-first operations for agent execution and governance
- MCP tools/resources exposed through `thegent serve`
- Optional generated TypeScript reference (when present)

## Generate TypeScript API Docs

From repository root:

```bash
./scripts/generate-api-docs-ts.sh
```

Generated pages (if source files are detected) are written under `docs/site/api/`.

## Practical Next Steps

- Add module-specific API pages as generated docs become available.
- Cross-link API entries to [Reference](/reference/) pages for operational context.
