---
title: heliosApp
description: SolidJS-powered AI coding interface featured in 20+ awesome-lists.
draft: false
---

**Status**: Active

## Overview

heliosApp is the primary UI for the Phenotype AI coding platform. Built on SolidJS and Bun for a fast, reactive experience, it pairs with heliosCLI for a full AI-augmented coding environment with real-time collaboration support. It has received 20+ awesome-list inclusions across GitHub.

## Tech Stack

- **Frontend**: SolidJS
- **Runtime**: Bun
- **CLI Backend**: heliosCLI (Rust)
- **Ports**: 3000 (primary), 3100 (collaboration server)

## Key Features

- Real-time collaborative editing powered by heliosCLI
- Unified AI provider access (Claude, OpenAI, Gemini) via cliproxyapi
- Hot-reload dev environment with Bun
- Featured in 20+ GitHub awesome-lists
- Extensible plugin surface for Phenotype ecosystem tools

## Quick Start

```bash
# Clone and install
git clone https://github.com/KooshaPari/heliosApp
cd heliosApp
bun install

# Run dev server
bun dev

# Build for production
bun run build
```

## Links

- **GitHub**: [KooshaPari/heliosApp](https://github.com/KooshaPari/heliosApp)
- **Port**: 3000 (primary), 3100 (colab)
- **Related**: [heliosCLI](/projects/helios-cli/)
