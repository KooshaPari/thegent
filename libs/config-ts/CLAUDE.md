# CLAUDE.md - config-ts

## Project Overview

TypeScript configuration management with Zod validation and hexagonal architecture.

## Layout

- `src/domain/` — Config domain model
- `src/ports/` — ConfigSource port
- `src/adapters/` — File + env adapters

## Development Commands

```bash
npm install && npm test && npm run build
```

## Architecture Principles

- **SOLID** — Single Responsibility, Dependency Inversion
- **DRY** — Shared abstractions
- **PoLA** — Descriptive error types
