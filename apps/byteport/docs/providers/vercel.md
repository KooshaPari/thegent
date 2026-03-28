# Vercel Provider

## Overview

Byteport deploys to Vercel using the [Vercel REST API](https://vercel.com/docs/rest-api). Supported application types include Next.js, React, Vue, SvelteKit, and static sites.

## Credential Setup

1. Go to **Settings > Credentials > Vercel** in the Byteport dashboard.
2. Generate a Vercel API token at [vercel.com/account/tokens](https://vercel.com/account/tokens).
3. Paste the token and click **Save**.

Byteport validates the token against the Vercel API before saving.

## Supported Operations

| Operation | Description |
|-----------|-------------|
| Deploy | Creates a new deployment from a Git repository or file archive |
| Status | Polls deployment state: `BUILDING` -> `READY` / `ERROR` |
| Delete | Removes the deployment from Vercel |
| Logs | Streams build logs in real time |

## Framework Detection

Byteport auto-detects Vercel-compatible frameworks:

- Next.js (detects `next.config.*`)
- React (Vite or CRA)
- Vue, Nuxt
- SvelteKit
- Static HTML

## Environment Variables

Per-project environment variables are forwarded to Vercel at deploy time as deployment environment variables.

## Free Tier Limits

| Resource | Vercel Hobby Limit |
|----------|-------------------|
| Deployments/day | 100 |
| Bandwidth/month | 100 GB |
| Serverless functions | 100 GB-hours/month |
| Custom domains | 50 |

## Troubleshooting

**Deployment fails with 403:** Token permissions are insufficient. Regenerate with full access.

**Build timeout:** Increase build timeout in Vercel project settings. Byteport passes the default 300s timeout.
