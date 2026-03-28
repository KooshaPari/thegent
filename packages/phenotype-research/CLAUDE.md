# Phenotype Research Engine

## Overview

Phenotype research and investigation engine - capabilities for deep code research and analysis.

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
- **Domain**: Research entities, findings, investigations
- **Application**: Research workflows, analysis pipelines
- **Ports**: Inbound and outbound interfaces
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
