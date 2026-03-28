---
title: agent-wave
description: Multi-agent orchestration platform for parallel AI workflows.
draft: false
---

**Status**: Active

## Overview

agent-wave is the Phenotype multi-agent orchestration platform. It enables parallel AI workflows with structured coordination, dependency-aware task scheduling, and result aggregation — turning complex multi-step tasks into a managed wave of concurrent agents.

## Tech Stack

- **Language**: TypeScript
- **Runtime**: Bun
- **Port**: 7000
- **Protocol**: JSON-RPC over HTTP + WebSocket for live status

## Key Features

- Dependency-aware parallel agent scheduling (DAG-based)
- Real-time workflow status via WebSocket feed
- Structured result aggregation with per-agent traces
- Integration with heliosCLI and AgilePlus task queues
- Configurable concurrency limits and retry policies

## Quick Start

```bash
# Clone and install
git clone https://github.com/KooshaPari/agent-wave
cd agent-wave
bun install

# Start orchestration server
bun start

# Build for production
bun run build
```

## Links

- **GitHub**: [KooshaPari/agent-wave](https://github.com/KooshaPari/agent-wave)
- **Port**: 7000
