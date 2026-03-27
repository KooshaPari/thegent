# CLAUDE.md — cipher

## Overview

`cipher` is a simple, safe cryptography library for Rust providing encryption, hashing, signatures, and key derivation primitives.

## Package

- **Name**: `cipher`
- **Repository**: `https://github.com/phenotype-dev/cipher`
- **Language**: Rust
- **Edition**: 2021

## Architecture

Hexagonal/clean architecture — domain types are separated from I/O adapters. The `core` module is the domain boundary.

## Dependencies

- `aes-gcm`, `chacha20poly1305` — symmetric encryption
- `sha2`, `blake2` — hashing
- `ed25519-dalek` — signatures
- `rand` — random number generation
- `thiserror` — error handling

## Build & Test

```bash
cargo test
cargo clippy
```

## Key Types

- `core` module — domain functionality (expand with `Encryptor`, `Decryptor`, `Hasher`, `Signer` traits)

## Conventions

- Follows Rust coding standards per `governance/standards/rust.md`
- MIT licensed
- No Phenotype-domain coupling — pure utility crate

## Phase 6 Status

- Source: `phenotype-cipher/`
- Canonical location: `libs/cipher/`
- Status: Extracted and renamed
