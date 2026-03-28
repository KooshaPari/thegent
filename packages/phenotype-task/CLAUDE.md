# Phenotype Task Engine

## Overview

Phenotype task orchestration engine - manages task planning, execution, and lifecycle.

## Quick Start

```bash
# Install dependencies
npm install

# Build
npm run build

# Test
npm run test
```

## Architecture

Based on hexagonal architecture with the following layers:
- **Domain**: Task entities, value objects, domain events
- **Application**: Use cases, command handlers
- **Ports**: Inbound (driving) and outbound (driven) interfaces
- **Adapters**: Infrastructure implementations

## Commands

| Command | Description |
|---------|-------------|
| `npm run build` | Compile TypeScript |
| `npm run test` | Run tests with Vitest |
| `npm run lint` | Lint with ESLint |
| `npm run typecheck` | Type check without emitting |

## Dependencies

- TypeScript
- Vitest (testing)
- ESLint

## Notes

- This is a Phenotype-domain package (stays in `packages/`)
- Version: 0.1.0
