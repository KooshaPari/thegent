---
title: Services
description: Phenotype services — local dev endpoints and consulting/OSS offerings.
draft: false
---

## About Phenotype

Phenotype is an AI-augmented development platform built by [Kooshayar Parinejad](https://kooshapari.com).

**Portfolio**: [kooshapari.com](https://kooshapari.com) / [ramdesigns.xyz](https://ramdesigns.xyz)

**What we offer**:
- Open-source tooling (see [Projects](/projects/))
- Consulting on AI-augmented development workflows, hexagonal architecture, and polyrepo platform engineering

**No ecommerce services are offered.** The old phenotype.us storefront (a Shopify clone) has been retired.
phenotype.us is currently under reconstruction — it will point to this hub site once DNS is re-routed.
See [phenotype.us recovery plan](/governance/phenotype-us-recovery/) for details.

---

## Running Services

| Service | Type | Port | Health Check |
|---------|------|------|--------------|
| heliosApp | Frontend | 3000 | `GET /` |
| heliosApp-colab | Frontend | 3100 | `GET /` |
| AgilePlus | Frontend | 4000 | `GET /` |
| cliproxyapi | API | 5000 | `GET /health` |
| heliosCLI daemon | API | 6000 | `GET /status` |
| agent-wave | API | 7000 | `GET /health` |
| phenotype-hub | Docs | 9000 | `GET /` |

## Shared Infrastructure

| Service | Port | Notes |
|---------|------|-------|
| PostgreSQL | 5432 | Shared DB |
| NATS | 4222 | Message bus |
| Dragonfly | 6379 | Cache (Redis-compatible) |
