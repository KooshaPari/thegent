# tRPC Context

> Definitive reference for tRPC v10 — end-to-end typesafe TypeScript APIs without code generation.
> Sources: trpc.io/docs/v10, github.com/trpc/trpc (fetched 2026-02-20).
> **Version covered: tRPC v10.45.2 (trace project version)**

---

## What is tRPC

**tRPC** lets you build and consume fully typesafe APIs without schemas or code generation. You define procedures on the server; the TypeScript client gets full autocompletion for inputs, outputs, and errors — enforced at build time.

Key properties:
- **No code generation**: Types flow from server to client via TypeScript inference
- **No schema language**: Define inputs with Zod; types are inferred
- **Procedure types**: `query` (read), `mutation` (write), `subscription` (streaming)
- **Middleware**: Auth, logging, rate limiting in a composable pipeline
- **React integration**: `@trpc/react-query` wraps `@tanstack/react-query` with tRPC types
- **Framework adapters**: Express, Next.js (App/Pages Router), Fastify, Bun

**trace Use Case:** `@trpc/client@^10.45.2`, `@trpc/react-query@^10.45.2`, `@trpc/server@^10.45.2` in trace web app. Used for type-safe API calls between the React frontend and backend.

**Note**: tRPC v11 exists (announced Jan 2025) but trace uses v10. This doc covers v10.

---

## Key Concepts

| Term | Definition |
|------|-----------|
| **Router** | Container for procedures; routers compose into the `AppRouter` |
| **Procedure** | An API endpoint — `query`, `mutation`, or `subscription` |
| **`t` (initTRPC)** | Factory for creating type-safe routers, procedures, and middleware |
| **Context** | Per-request data (user session, DB connection) — flows through all procedures |
| **Middleware** | Function wrapping procedures; used for auth, logging |
| **Input** | Zod schema defining expected request shape |
| **Output** | Optional Zod schema for response validation |
| **`AppRouter`** | Root router type exported from server; imported as type-only on client |
| **Caller** | Server-side tRPC caller (for testing or SSR) |

---

## Installation

```bash
# Server
npm install @trpc/server zod
bun add @trpc/server zod

# Client
npm install @trpc/client

# React Query integration
npm install @trpc/react-query @tanstack/react-query

# Versions in trace:
# @trpc/client@^10.45.2
# @trpc/react-query@^10.45.2
# @trpc/server@^10.45.2
```

---

## Server Setup

### Step 1: Initialize tRPC (`t`)

```typescript
// server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import type { Context } from './context';

const t = initTRPC.context<Context>().create({
    // Optional: transform errors before sending to client
    errorFormatter({ shape, error }) {
        return {
            ...shape,
            data: {
                ...shape.data,
                zodError: error.cause instanceof ZodError
                    ? error.cause.flatten()
                    : null,
            },
        };
    },
});

// Export building blocks
export const router = t.router;
export const publicProcedure = t.procedure;
export const middleware = t.middleware;
```

### Step 2: Define Context

```typescript
// server/context.ts
import type { CreateNextContextOptions } from '@trpc/server/adapters/next';

export interface Context {
    user: { id: string; email: string } | null;
    db: DatabaseClient;
}

// Context factory — called once per request
export async function createContext({ req, res }: CreateNextContextOptions): Promise<Context> {
    const user = await getUserFromSession(req);
    return {
        user,
        db: getDatabase(),
    };
}
```

### Step 3: Create Middleware

```typescript
// Auth middleware
const isAuthed = middleware(({ ctx, next }) => {
    if (!ctx.user) {
        throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Not authenticated' });
    }
    return next({
        ctx: {
            ...ctx,
            user: ctx.user,  // Narrow type: user is non-null after this middleware
        },
    });
});

// Protected procedure (requires auth)
export const protectedProcedure = publicProcedure.use(isAuthed);

// Logging middleware
const logger = middleware(async ({ path, type, next }) => {
    const start = Date.now();
    const result = await next();
    const ms = Date.now() - start;
    console.log(`${type} ${path} took ${ms}ms`);
    return result;
});

export const loggedProcedure = publicProcedure.use(logger);
```

### Step 4: Define Procedures

```typescript
// server/routers/jobs.ts
import { z } from 'zod';
import { router, publicProcedure, protectedProcedure } from '../trpc';

export const jobsRouter = router({
    // Query: read operation
    getJob: publicProcedure
        .input(z.object({ jobId: z.string() }))
        .query(async ({ input, ctx }) => {
            const job = await ctx.db.jobs.findById(input.jobId);
            if (!job) {
                throw new TRPCError({ code: 'NOT_FOUND', message: 'Job not found' });
            }
            return job;
        }),

    // Query: list with filters
    listJobs: protectedProcedure
        .input(z.object({
            status: z.enum(['pending', 'running', 'completed', 'failed']).optional(),
            limit: z.number().min(1).max(100).default(20),
            cursor: z.string().optional(),
        }))
        .query(async ({ input, ctx }) => {
            const jobs = await ctx.db.jobs.findMany({
                where: { userId: ctx.user.id, status: input.status },
                take: input.limit + 1,
                cursor: input.cursor ? { id: input.cursor } : undefined,
            });

            const hasMore = jobs.length > input.limit;
            return {
                jobs: jobs.slice(0, input.limit),
                nextCursor: hasMore ? jobs[input.limit - 1].id : null,
            };
        }),

    // Mutation: write operation
    createJob: protectedProcedure
        .input(z.object({
            name: z.string().min(1).max(200),
            config: z.record(z.unknown()),
        }))
        .mutation(async ({ input, ctx }) => {
            return ctx.db.jobs.create({
                data: {
                    ...input,
                    userId: ctx.user.id,
                    status: 'pending',
                },
            });
        }),

    // Mutation: update
    cancelJob: protectedProcedure
        .input(z.object({ jobId: z.string() }))
        .mutation(async ({ input, ctx }) => {
            const job = await ctx.db.jobs.findById(input.jobId);
            if (!job || job.userId !== ctx.user.id) {
                throw new TRPCError({ code: 'FORBIDDEN' });
            }
            return ctx.db.jobs.update({
                where: { id: input.jobId },
                data: { status: 'cancelled' },
            });
        }),
});
```

### Step 5: Merge Routers

```typescript
// server/routers/_app.ts
import { router } from '../trpc';
import { jobsRouter } from './jobs';
import { usersRouter } from './users';
import { agentsRouter } from './agents';

export const appRouter = router({
    jobs: jobsRouter,
    users: usersRouter,
    agents: agentsRouter,
});

// Export type for client
export type AppRouter = typeof appRouter;
```

---

## Server Adapters

### Next.js App Router

```typescript
// app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { appRouter } from '@/server/routers/_app';
import { createContext } from '@/server/context';

const handler = (req: Request) =>
    fetchRequestHandler({
        endpoint: '/api/trpc',
        req,
        router: appRouter,
        createContext: () => createContext({ req }),
    });

export { handler as GET, handler as POST };
```

### Express / Node.js

```typescript
import express from 'express';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { appRouter } from './routers/_app';
import { createContext } from './context';

const app = express();
app.use('/api/trpc', createExpressMiddleware({
    router: appRouter,
    createContext,
}));
```

---

## Client Setup

### Vanilla TypeScript Client

```typescript
// client/trpc.ts
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client';
import type { AppRouter } from '../server/routers/_app';

export const trpc = createTRPCProxyClient<AppRouter>({
    links: [
        httpBatchLink({
            url: 'http://localhost:3000/api/trpc',
            // Add auth headers
            headers() {
                return {
                    authorization: `Bearer ${getToken()}`,
                };
            },
        }),
    ],
});

// Usage (fully typed!)
const job = await trpc.jobs.getJob.query({ jobId: 'job_123' });
// job is inferred as: { id: string; name: string; status: string; ... }

const created = await trpc.jobs.createJob.mutate({
    name: 'Process dataset',
    config: { timeout: 30 },
});

// Cursor pagination
let cursor: string | null = null;
const result = await trpc.jobs.listJobs.query({ status: 'running', cursor: cursor ?? undefined });
cursor = result.nextCursor;
```

---

## React Query Integration (`@trpc/react-query`)

### Provider Setup

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createTRPCReact, httpBatchLink } from '@trpc/react-query';
import type { AppRouter } from '../server/routers/_app';
import { useState } from 'react';

export const trpc = createTRPCReact<AppRouter>();

export function TRPCProvider({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(() => new QueryClient());
    const [trpcClient] = useState(() =>
        trpc.createClient({
            links: [
                httpBatchLink({
                    url: '/api/trpc',
                    headers() {
                        return { authorization: `Bearer ${getToken()}` };
                    },
                }),
            ],
        })
    );

    return (
        <trpc.Provider client={trpcClient} queryClient={queryClient}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </trpc.Provider>
    );
}
```

### Hooks

```tsx
// components/JobList.tsx
'use client';

import { trpc } from '../providers';

export function JobList() {
    // Query (GET-like)
    const { data, isLoading, error } = trpc.jobs.listJobs.useQuery({
        status: 'running',
        limit: 20,
    });

    // Mutation (POST/PUT/DELETE-like)
    const createJob = trpc.jobs.createJob.useMutation({
        onSuccess: (job) => {
            console.log('Created:', job.id);
            // Invalidate and refetch list
            utils.jobs.listJobs.invalidate();
        },
        onError: (err) => console.error('Error:', err.message),
    });

    const cancelJob = trpc.jobs.cancelJob.useMutation();

    // Utility (invalidation, prefetch, etc.)
    const utils = trpc.useUtils();

    if (isLoading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <ul>
            {data?.jobs.map(job => (
                <li key={job.id}>
                    {job.name}
                    <button onClick={() => cancelJob.mutate({ jobId: job.id })}>
                        Cancel
                    </button>
                </li>
            ))}
            <button onClick={() => createJob.mutate({ name: 'New Job', config: {} })}>
                Create Job
            </button>
        </ul>
    );
}
```

**`useInfiniteQuery` for cursor pagination:**

```tsx
const { data, fetchNextPage, hasNextPage } = trpc.jobs.listJobs.useInfiniteQuery(
    { limit: 20 },
    {
        getNextPageParam: (lastPage) => lastPage.nextCursor,
        initialCursor: undefined,
    }
);
```

---

## Subscriptions (WebSocket)

```typescript
// Server
import { observable } from '@trpc/server/observable';

export const jobsRouter = router({
    onJobUpdated: publicProcedure
        .input(z.object({ jobId: z.string() }))
        .subscription(({ input }) => {
            return observable<JobUpdateEvent>((emit) => {
                // Subscribe to job updates from event bus
                const unsubscribe = eventBus.subscribe(`job.${input.jobId}`, (event) => {
                    emit.next(event);
                });
                // Cleanup
                return () => unsubscribe();
            });
        }),
});

// Client (with websocket link)
import { createWSClient, wsLink } from '@trpc/client';

const wsClient = createWSClient({ url: 'ws://localhost:3000/api/trpc' });
const trpc = createTRPCProxyClient<AppRouter>({
    links: [wsLink({ client: wsClient })],
});

// Subscribe
const subscription = trpc.jobs.onJobUpdated.subscribe(
    { jobId: 'job_123' },
    {
        onData: (event) => console.log('Update:', event),
        onError: (err) => console.error('Sub error:', err),
    }
);

subscription.unsubscribe();
```

---

## Error Handling

tRPC maps errors to HTTP status codes. Use `TRPCError` to throw typed errors:

```typescript
import { TRPCError } from '@trpc/server';

// Throw typed errors in procedures
throw new TRPCError({ code: 'NOT_FOUND', message: 'Job not found' });
throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Login required' });
throw new TRPCError({ code: 'FORBIDDEN', message: 'Access denied' });
throw new TRPCError({ code: 'BAD_REQUEST', message: 'Invalid input' });
throw new TRPCError({
    code: 'INTERNAL_SERVER_ERROR',
    message: 'Something went wrong',
    cause: originalError,
});
```

| tRPC Code | HTTP Status |
|-----------|------------|
| `BAD_REQUEST` | 400 |
| `UNAUTHORIZED` | 401 |
| `FORBIDDEN` | 403 |
| `NOT_FOUND` | 404 |
| `CONFLICT` | 409 |
| `PRECONDITION_FAILED` | 412 |
| `PAYLOAD_TOO_LARGE` | 413 |
| `UNPROCESSABLE_CONTENT` | 422 |
| `TOO_MANY_REQUESTS` | 429 |
| `CLIENT_CLOSED_REQUEST` | 499 |
| `INTERNAL_SERVER_ERROR` | 500 |

**Client error handling:**

```typescript
import { TRPCClientError } from '@trpc/client';

try {
    await trpc.jobs.getJob.query({ jobId: 'missing' });
} catch (err) {
    if (err instanceof TRPCClientError) {
        console.log(err.data?.code);       // 'NOT_FOUND'
        console.log(err.message);          // 'Job not found'
        console.log(err.data?.httpStatus); // 404
    }
}
```

---

## Server-Side Calling (Caller)

Call procedures server-side (for SSR, testing):

```typescript
// Create a caller with a context
const caller = appRouter.createCaller({ user: { id: 'user_123' }, db });

// Call procedures
const job = await caller.jobs.getJob({ jobId: 'job_123' });
const created = await caller.jobs.createJob({ name: 'Test', config: {} });
```

---

## Input Validation

tRPC uses Zod for input validation. Invalid inputs return `BAD_REQUEST` automatically.

```typescript
.input(z.object({
    name: z.string().min(1, "Name required").max(200),
    email: z.string().email(),
    age: z.number().int().positive().optional(),
    tags: z.array(z.string()).max(10).default([]),
    role: z.enum(['admin', 'user', 'viewer']).default('user'),
}))
```

---

## Authentication Pattern

```typescript
// Middleware that reads session from cookie/header
const isAuthed = middleware(async ({ ctx, next }) => {
    if (!ctx.user) {
        throw new TRPCError({ code: 'UNAUTHORIZED' });
    }
    return next({ ctx: { ...ctx, user: ctx.user } });
});

// Role check
const isAdmin = isAuthed.unstable_pipe(({ ctx, next }) => {
    if (ctx.user.role !== 'admin') {
        throw new TRPCError({ code: 'FORBIDDEN', message: 'Admin required' });
    }
    return next({ ctx });
});

export const adminProcedure = publicProcedure.use(isAdmin);
```

---

## thegent / trace Integration

- **trace web app**: `@trpc/client`, `@trpc/react-query`, `@trpc/server` at v10.45.2
- **Pattern**: `@trpc/react-query` wrapping `@tanstack/react-query` for UI state; type-safe API between Next.js/Vite frontend and Go/Python backends (via adapter or proxy)
- **Router file**: Check `trace/frontend/apps/web/src/` for `trpc.ts` or `api.ts`
- **Note**: tRPC is TypeScript-only; Go/Python backends are accessed via REST/gRPC, not tRPC directly

---

## Known Issues / Gotchas

1. **Type-only import**: Import `AppRouter` as `import type { AppRouter }` — never import the runtime at the client; it imports server-only code.
2. **Batching**: `httpBatchLink` batches multiple queries into one HTTP request. If one fails, all fail (by default). Use `httpLink` to disable batching.
3. **Input required**: Every procedure needs an `.input()` call if it takes arguments. No `.input()` means the procedure accepts no arguments.
4. **Server-side only**: tRPC server cannot run in browser. Router file must not be imported on the client side (only the type).
5. **Subscriptions need WebSocket**: `subscription` procedures require `wsLink` on the client; `httpBatchLink` doesn't support subscriptions.
6. **v10 vs v11**: tRPC v11 exists but trace uses v10. The builder pattern (`t.procedure.input().query()`) is the same; v11 adds streaming improvements.
7. **Zod required**: tRPC v10 input validation requires Zod; alternatives (Yup, custom) require a custom `transformer`.

---

## Sources & References

- **tRPC v10 Docs**: https://trpc.io/docs/v10 (fetched 2026-02-20)
- **GitHub**: https://github.com/trpc/trpc (fetched 2026-02-20)
- **tRPC v10 Client Setup**: https://trpc.io/docs/v10/client/vanilla/setup (fetched 2026-02-20)
- **npm `@trpc/server`**: https://www.npmjs.com/package/@trpc/server (v10.45.2, fetched 2026-02-20)
- **tRPC v11 (migration guide)**: https://trpc.io/docs/migrate-from-v10-to-v11 (fetched 2026-02-20)
- **Last Verified**: 2026-02-20

---

## Quick Reference

| Item | Value |
|------|-------|
| Server package | `@trpc/server@^10.45.2` |
| Client package | `@trpc/client@^10.45.2` |
| React package | `@trpc/react-query@^10.45.2` |
| Input validation | Zod (required) |
| HTTP batching | `httpBatchLink` (default) |
| WebSocket | `wsLink` + `createWSClient` |

### Procedure Builder Cheat Sheet

```typescript
// Public query
publicProcedure.input(z.object({...})).query(({ input, ctx }) => { ... })

// Public mutation
publicProcedure.input(z.object({...})).mutation(({ input, ctx }) => { ... })

// Protected query (with middleware)
protectedProcedure.input(z.object({...})).query(({ input, ctx }) => {
    // ctx.user is non-null here
})

// No input
publicProcedure.query(({ ctx }) => { ... })

// Throw typed errors
throw new TRPCError({ code: 'NOT_FOUND' })
throw new TRPCError({ code: 'UNAUTHORIZED' })
throw new TRPCError({ code: 'FORBIDDEN' })
```

### React Hook Cheat Sheet

```typescript
// Read
const { data, isLoading, error } = trpc.router.procedure.useQuery(input);

// Write
const mutation = trpc.router.procedure.useMutation({ onSuccess, onError });
mutation.mutate(input);

// Infinite scroll
const { data, fetchNextPage } = trpc.router.procedure.useInfiniteQuery(
    input,
    { getNextPageParam: (page) => page.nextCursor }
);

// Invalidate cache
const utils = trpc.useUtils();
await utils.router.procedure.invalidate();
```
