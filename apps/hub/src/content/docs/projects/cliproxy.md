---
title: cliproxyapi++
description: Unified AI provider proxy with hot-swappable credentials and audit logging.
draft: false
---

**Status**: Active

## Overview

cliproxyapi++ is a unified proxy layer for AI provider tokens and CLI tool access. Written in Go for performance and portability, it supports Claude, OpenAI, and Gemini with hot-swappable credentials, rate-limit management, and audit logging — decoupling API keys from individual tools.

## Tech Stack

- **Language**: Go
- **Port**: 5000
- **Storage**: Local credential store (encrypted)

## Key Features

- Unified proxy for Claude, OpenAI, and Gemini
- Hot-swappable credentials without restarting dependent services
- Per-request audit logging for compliance and debugging
- Rate-limit tracking and backpressure across providers
- 8 GitHub stars

## Quick Start

```bash
# Clone and build
git clone https://github.com/KooshaPari/cliproxyapi-plusplus
cd cliproxyapi-plusplus
go build -o cliproxy ./cmd/cliproxy

# Start proxy
./cliproxy serve

# Configure a provider
./cliproxy config set --provider claude --key $ANTHROPIC_API_KEY
```

## Links

- **GitHub**: [KooshaPari/cliproxyapi-plusplus](https://github.com/KooshaPari/cliproxyapi-plusplus)
- **Port**: 5000
