# auth-ts

TypeScript **OAuth2 / OIDC** authentication patterns using hexagonal layout: domain types, ports, and swappable adapters (memory token store, JWT provider).

## Layout

| Area | Role |
|------|------|
| `domain/` | Token types, claims, errors |
| `ports/` | `TokenProvider`, `TokenStore`, `TokenVerifier` |
| `adapters/` | `MemoryTokenStore`, `PlaceholderJwtVerifier` |

## Installation

```bash
npm install
npm test
npm run build
```

## Architecture

See `adr/ADR-001-architecture.md`.
