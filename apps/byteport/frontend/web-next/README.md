# Byteport Next.js Frontend

This directory contains the new Next.js + TypeScript implementation of the Byteport control plane UI. It replaces the previous SvelteKit + Tauri experience and is designed to align with the broader multi-language SDK initiative.

## Key features

- **Next.js 14 App Router** with React 18 and server actions enabled.
- **Tailwind CSS** powered design tokens that mirror the existing dark UI palette.
- **Auth context** that fetches the `/authenticate` endpoint, normalises user data, and exposes `refresh`/`setUser` helpers.
- **WorkOS AuthKit** login flow wired to shared Zen credentials with callback handling at `/auth/callback`.
- **Dashboard surfaces** for projects, instances, monitoring KPIs, and account settings using shared layout components.

## Getting started

```bash
# install dependencies
pnpm install

# run the dev server
pnpm dev
```


Copy `.env.example` to `.env.local` and set:

```
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
NEXT_PUBLIC_AUTHKIT_DOMAIN=https://significant-vessel-93-staging.authkit.app
NEXT_PUBLIC_AUTHKIT_CLIENT_ID=<workos client id>
NEXT_PUBLIC_AUTHKIT_REDIRECT_URI=http://localhost:3000/auth/callback
NEXT_PUBLIC_AUTHKIT_SCOPES=openid profile email offline_access
NEXT_PUBLIC_AUTHKIT_AUDIENCE=https://zen.kooshapari.com
```

Authentication flows mirror the Zen MCP AuthKit setup; reuse the same WorkOS credentials.

## Next steps
- Integrate the backend WorkOS callback endpoint and persist the returned session in the Go API.
- Expand the dashboard with resource drill-down pages and deployment activity feeds.
- Integrate shared SDK components as they ship (Go orchestrator, Python CLI, KInfra bindings).
- Wire CI to lint/build this app alongside the backend services.
