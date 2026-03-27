# CLAUDE.md - auth-ts

## Project Overview

TypeScript OAuth2/OIDC authentication library using hexagonal architecture.

## Layout

- `src/domain/` — token types, claims, errors
- `src/ports/` — TokenProvider, TokenStore, TokenVerifier traits
- `src/adapters/` — MemoryTokenStore, PlaceholderJwtVerifier

## Development Commands

```bash
npm install && npm test && npm run build
```

## Architecture Principles

- **SOLID** — Single Responsibility, Dependency Inversion
- **DRY** — Shared abstractions
- **PoLA** — Descriptive error types

## Build

```bash
npm install
npm test
npm run build
```
