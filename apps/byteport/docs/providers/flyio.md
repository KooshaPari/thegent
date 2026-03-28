# Fly.io Provider

## Overview

Byteport deploys to Fly.io using the [Fly.io Machines API](https://fly.io/docs/machines/api/). Fly.io is ideal for containerized workloads with global distribution and persistent volumes.

## Credential Setup

1. Go to **Settings > Credentials > Fly.io** in the Byteport dashboard.
2. Generate an API token via the Fly CLI: `fly auth token` or at [fly.io/user/personal_access_tokens](https://fly.io/user/personal_access_tokens).
3. Paste the token and click **Save**.

## Supported Operations

| Operation | Description |
|-----------|-------------|
| Deploy | Creates a Fly app and deploys via Machines API |
| Status | Polls machine state: `created` -> `started` / `stopped` |
| Delete | Destroys the Fly app and all machines |
| Logs | Retrieves machine logs via Fly Machines API |

## Framework Detection

Fly.io deploys any Dockerfile-based application. Byteport generates a `fly.toml` based on detected framework:

- Go (generates minimal Dockerfile if not present)
- Python (FastAPI, Flask, Django)
- Node.js
- Rust
- Any existing Dockerfile

## Free Tier Limits

| Resource | Fly.io Free Allowance |
|----------|----------------------|
| shared-cpu-1x VMs | 3 (always on) |
| RAM | 256 MB per VM |
| Volumes | 3 GB total |
| Outbound bandwidth | 100 GB/month |

## Troubleshooting

**App fails health check:** Ensure your application listens on the port specified in `fly.toml` (default: `8080`).

**Out of free machines:** Fly.io free tier allows 3 shared VMs. Scale down or delete unused apps.
