# config-ts

TypeScript **configuration management** with **Zod** validation, hexagonal ports (`ConfigSource`), and adapters for file and environment sources.

## Layout

| Path | Role |
|------|------|
| `src/domain/` | Config domain model |
| `src/ports/` | `ConfigSource` port |
| `src/adapters/` | File + env adapters |

## Installation

```bash
npm install
npm test
npm run build
```
