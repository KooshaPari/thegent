# thegent Docsite

VitePress-powered documentation for thegent.

## Running Locally

```bash
cd docs/site
bun install
bun run dev
```

Dev server default: `http://localhost:5173`.

## Build and Preview

```bash
cd docs/site
bun run build
bun run preview
```

Build output is written to `docs/public/`.

## Quick Validation

```bash
# from repository root
rg -n "\]\((\./|\.\./|/)" docs/site -g '*.md'

# from docs/site
bun run build
```

## Generate TypeScript API Docs

```bash
./scripts/generate-api-docs-ts.sh
```

Output lands in `docs/site/api/` when source files are available.

## Information Architecture

- `guide/` usage and setup documentation
- `operations/` troubleshooting and runbooks
- `reference/` routing/configuration details
- `api/` generated + curated API pages

## Deployment

The site build in `docs/public/` is served by the docs workflow in `.github/workflows/docs.yml`.
