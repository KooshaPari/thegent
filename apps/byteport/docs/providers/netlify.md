# Netlify Provider

## Overview

Byteport deploys to Netlify using the [Netlify API](https://docs.netlify.com/api/get-started/). Supported frameworks include Next.js (via Netlify adapter), Gatsby, SvelteKit, Nuxt, and static sites.

## Credential Setup

1. Go to **Settings > Credentials > Netlify** in the Byteport dashboard.
2. Generate a Netlify personal access token at [app.netlify.com/user/applications](https://app.netlify.com/user/applications).
3. Paste the token and click **Save**.

## Supported Operations

| Operation | Description |
|-----------|-------------|
| Deploy | Creates a new site deployment via Netlify API |
| Status | Polls deploy state: `building` -> `ready` / `error` |
| Delete | Deletes the site from Netlify |
| Logs | Retrieves build log output |

## Framework Detection

- Next.js (requires `@netlify/plugin-nextjs`)
- Gatsby
- SvelteKit (Netlify adapter)
- Nuxt
- Hugo, Eleventy
- Static HTML

## Free Tier Limits

| Resource | Netlify Free Limit |
|----------|-------------------|
| Bandwidth/month | 100 GB |
| Build minutes/month | 300 |
| Sites | Unlimited |
| Serverless functions | 125k requests/month |

## Troubleshooting

**Build exceeds 300 minutes:** Netlify free tier caps build minutes. Optimize build or upgrade plan.

**Deploy fails on Next.js:** Ensure `@netlify/plugin-nextjs` is in `netlify.toml` plugins.
