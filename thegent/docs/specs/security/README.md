# Security & Compliance Specification

## Overview

Security primitives, encryption, secrets management, and compliance.

## Components

### Cryptography

| Primitive | Implementation |
|-----------|----------------|
| Signing | Ed25519/X25519 |
| Encryption | ChaCha20-Poly1305 |
| Hashing | BLAKE3 |

### Secret Management

| Store | Backend |
|---------|---------|
| API keys | Environment |
| Tokens | Encrypted files |
| Credentials | Platform keyring |

### Compliance

| Standard | Coverage |
|----------|-----------|
| SOC2 | Audit logging |
| HIPAA | Encryption |
| GDPR | Data minimization |

## Threat Model

| Vector | Mitigation |
|--------|-------------|
| Key exfiltration | Encrypted storage |
| Privilege escalation | RBAC |
| Data breach | Encryption at rest |
| Supply chain | Dependency scanning |
