# Supabase Provider

## Overview

Byteport integrates with Supabase using the [Supabase Management API](https://supabase.com/docs/reference/api). Supabase provides PostgreSQL databases, edge functions, storage, and auth.

## Credential Setup

1. Go to **Settings > Credentials > Supabase** in the Byteport dashboard.
2. Find your credentials in the Supabase dashboard under **Project Settings > API**.
3. Enter:
   - **Project URL:** `https://<project-ref>.supabase.co`
   - **Service Role Key:** Found under **API Keys** (keep this secret)
4. Click **Save**.

## Supported Operations

| Operation | Description |
|-----------|-------------|
| Deploy | Deploys edge functions to the Supabase project |
| Status | Checks edge function and database health |
| Delete | Removes deployed edge functions |
| Logs | Retrieves edge function invocation logs |

## Use Cases

Byteport deploys to Supabase primarily for:

- **Edge Functions** — TypeScript/Deno serverless functions
- **Database migrations** — SQL migration files applied via Management API
- **Storage buckets** — Static asset hosting

## Free Tier Limits

| Resource | Supabase Free Limit |
|----------|-------------------|
| Projects | 2 |
| Database | 500 MB |
| Edge function invocations | 500k/month |
| Storage | 1 GB |
| Auth MAU | 50,000 |

## Troubleshooting

**Edge function deploy fails:** Ensure function is in `supabase/functions/<name>/index.ts` format.

**Service key unauthorized:** Double-check you are using the `service_role` key, not the `anon` key.
