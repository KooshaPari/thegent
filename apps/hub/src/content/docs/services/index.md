---
title: Service Registry
description: All Phenotype services and their endpoints.
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
