# Railway Provider

## Overview

Byteport deploys to Railway using the [Railway GraphQL API](https://docs.railway.app/reference/public-api). Railway excels at backend services, databases, and full-stack apps with persistent state.

## Credential Setup

1. Go to **Settings > Credentials > Railway** in the Byteport dashboard.
2. Generate an API token at [railway.app/account/tokens](https://railway.app/account/tokens).
3. Paste the token and click **Save**.

## Supported Operations

| Operation | Description |
|-----------|-------------|
| Deploy | Creates a new Railway service from a Git repo or Docker image |
| Status | Polls deployment status via GraphQL subscriptions |
| Delete | Removes the service from the Railway project |
| Logs | Streams container logs |

## Framework Detection

Railway supports any Dockerfile-based or Nixpack-detected project:

- Go (detects `go.mod`)
- Python (detects `requirements.txt`, `pyproject.toml`)
- Node.js (detects `package.json`)
- Rust (detects `Cargo.toml`)
- Docker (detects `Dockerfile`)

## Environment Variables

Per-project environment variables are injected as Railway service variables at deploy time.

## Free Tier Limits

| Resource | Railway Trial Limit |
|----------|-------------------|
| Credit/month | $5 (trial) |
| RAM | 512 MB |
| vCPU | 0.5 vCPU |
| Egress | 100 GB/month |

## Troubleshooting

**Service fails to start:** Check Railway logs. Ensure `PORT` environment variable is respected by the application.

**Out of trial credits:** Railway requires a paid plan after trial credit is exhausted.
