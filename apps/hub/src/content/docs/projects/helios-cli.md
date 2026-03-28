---
title: heliosCLI
description: Multi-runtime AI coding CLI with Rust core and TypeScript integrations.
draft: false
---

**Status**: Active

## Overview

heliosCLI is the primary AI coding CLI for the Phenotype ecosystem. Built with a Rust core for performance and reliability, it exposes TypeScript integrations that allow tool authors to extend it. It provides unified access to Codex, Claude, and Gemini behind a single CLI surface.

## Tech Stack

- **Core**: Rust
- **Integrations**: TypeScript
- **Build**: Cargo + Bun
- **Port**: 6000 (daemon mode)

## Key Features

- Unified CLI surface for Claude, OpenAI Codex, and Gemini
- Rust core for low-latency streaming and process management
- TypeScript plugin API for ecosystem integrations
- Daemon mode for persistent session state (port 6000)
- Powers real-time collaboration in heliosApp

## Quick Start

```bash
# Clone and build
git clone https://github.com/KooshaPari/heliosCLI
cd heliosCLI
cargo build --release

# Run CLI
./target/release/helios --help

# Run in daemon mode
./target/release/helios daemon
```

## Links

- **GitHub**: [KooshaPari/heliosCLI](https://github.com/KooshaPari/heliosCLI)
- **Port**: 6000 (daemon)
- **Related**: [heliosApp](/projects/helios-app/)
