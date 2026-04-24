# thegent Specification

> Dotfiles manager, platform bootstrap tool, and polyglot development hub

## Overview

thegent is the single entry point for bootstrapping developer machines, managing AI agent workflows, orchestrating multi-agent swarms, and enforcing governance across the Phenotype ecosystem.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         thegent                                   │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │   Dotfiles  │ │   Platform   │ │   Agent     │          │
│  │   Manager   │ │   Bootstrap  │ │   Orchestr. │          │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘          │
│         └────────────────┼────────────────┘                     │
│                          │                                       │
│  ┌──────────────┐ ┌──────┴───────┐ ┌──────────────┐          │
│  │  Templates  │ │  Governance  │ │  Swarm      │          │
│  │             │ │              │ │  Manager    │          │
│  └─────────────┘ └──────────────┘ └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

| Component | Description |
|-----------|-------------|
| Dotfiles Manager | Symlink-based dotfile management |
| Platform Bootstrap | Machine setup automation |
| Agent Orchestration | Multi-agent workflow coordination |
| Templates | 10+ language stack scaffolding |
| Governance | Policy enforcement across ecosystem |
| Swarm Manager | Multi-agent collective management |

## Rust Crates

| Crate | Description |
|-------|-------------|
| thegent-core | Core CLI and orchestration |
| thegent-shm | Shared memory IPC |
| thegent-metrics | Telemetry and monitoring |
| thegent-cache | Distributed caching |
| thegent-sharecli | CLI sharing across machines |
| thegent-mesh | Network mesh for agent communication |
