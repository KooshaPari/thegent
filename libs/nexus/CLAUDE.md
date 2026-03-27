# Nexus

Service registry and discovery library.

## Purpose

Provides service registration, discovery, health checking, and load balancing for distributed systems.

## Architecture

- Registry stores services and metadata
- Discovery supports name/tag queries
- Built for async Rust using Tokio

## Build

```bash
cargo check
```

## Usage

Add dependency to Cargo.toml and import `nexus::{Registry, Service}`.
