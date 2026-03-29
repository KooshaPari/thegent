# Phase 3: Frontend Consolidation - PROGRESS REPORT

**Status:** 50% Complete (3 of 6 sub-phases done)  
**Date:** 2025-10-12

---

## Completed Sub-Phases ✅

### 3.1: Remove Duplicate Sidebar Components ✅
**Commit:** `5e401961`

**Actions Taken:**
- ❌ Deleted `components/layout/Sidebar.tsx` (simpler, basic navigation)
- ✅ Kept `components/sidebar.tsx` (feature-rich with tooltips, collapse, better UX)
- Updated `components/layout/AppShell.tsx` to import from `../sidebar`

**Benefits:**
- Single sidebar component with consistent behavior
- Better UX with tooltips and collapse functionality
- Reduced maintenance burden

---

### 3.2: Remove Duplicate Header Components ✅
**Commit:** `5e401961`

**Actions Taken:**
- ❌ Deleted `components/layout/Header.tsx` (basic title/subtitle header)
- ✅ Kept `components/header.tsx` (full-featured with search, notifications, user menu)

**Benefits:**
- Comprehensive header with all necessary features
- Command palette integration (Cmd+K)
- Notifications system ready
- User dropdown menu

---

### 3.3: Consolidate Auth State Management ✅
**Commit:** `5e401961`

**Actions Taken:**
- Removed `user` and `setUser` from `lib/store.ts` (Zustand)
- Made `context/auth-context.tsx` the **single source of truth** for authentication
- All auth state now flows through React Context

**Before:**
```typescript
// Two sources of auth state!
const user = useAppStore((state) => state.user);  // Zustand
const { user } = useAuth();  // Context
```

**After:**
```typescript
// Single source of truth
const { user, status, refresh, logout } = useAuth();  // Context only
```

**Benefits:**
- No more state synchronization issues
- Clearer data flow
- Follows React best practices
- Easier to debug

---

## Remaining Sub-Phases ⏳

### 3.4: Fix Route Duplication ⏳

**Problem Identified:**
```
Duplicate Routes:
- /home vs /dashboard
- /home/settings vs /settings
- /home/instances vs /instances
- /home/monitor vs /monitor
- /home/projects/new vs /projects/new
```

**Recommended Actions:**
1. Choose canonical routes (prefer shorter paths)
   - `/dashboard` (not `/home`)
   - `/settings` (not `/home/settings`)
   - `/instances` (not `/home/instances`)
   
2. Update all navigation links in:
   - `components/sidebar.tsx` navigation items
   - `components/layout/AppShell.tsx` breadcrumbs
   - All `Link` components throughout the app

3. Add redirects for old routes:
   ```typescript
   // In Next.js middleware or layout
   if (pathname.startsWith('/home/')) {
     redirect(pathname.replace('/home/', '/'));
   }
   ```

4. Update tests to use canonical routes

**Estimated Effort:** 2-3 hours

---

### 3.5: Implement React Query for Data Fetching ⏳

**Current State:**
- Custom hooks in `lib/hooks/` using `useEffect` + `useState`
- No caching, stale data management, or optimistic updates
- Examples:
  - `use-deployments.ts`
  - `use-hosts.ts`
  - `use-providers.ts`
  - `use-metrics.ts`
  - `use-logs.ts`

**Recommended Implementation:**

**Step 1: Install React Query**
```bash
cd frontend/web-next
pnpm add @tanstack/react-query @tanstack/react-query-devtools
```

**Step 2: Create Query Client Provider**
```typescript
// lib/providers/query-provider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

**Step 3: Update Root Layout**
```typescript
// app/layout.tsx
import { QueryProvider } from '@/lib/providers/query-provider';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <AuthProvider>
          <QueryProvider>
            {children}
          </QueryProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
```

**Step 4: Create Query Functions**
```typescript
// lib/queries/deployments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as api from '@/lib/api';

export const deploymentKeys = {
  all: ['deployments'] as const,
  lists: () => [...deploymentKeys.all, 'list'] as const,
  list: (filters: string) => [...deploymentKeys.lists(), { filters }] as const,
  details: () => [...deploymentKeys.all, 'detail'] as const,
  detail: (id: string) => [...deploymentKeys.details(), id] as const,
};

export function useDeployments() {
  return useQuery({
    queryKey: deploymentKeys.lists(),
    queryFn: api.fetchDeployments,
  });
}

export function useDeployment(id: string) {
  return useQuery({
    queryKey: deploymentKeys.detail(id),
    queryFn: () => api.fetchDeployment(id),
    enabled: !!id,
  });
}

export function useCreateDeployment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: api.createDeployment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deploymentKeys.lists() });
    },
  });
}

export function useTerminateDeployment() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => api.terminateDeployment(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: deploymentKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: deploymentKeys.lists() });
    },
  });
}
```

**Step 5: Migrate Existing Hooks**

**Before** (custom hook with useEffect):
```typescript
// lib/hooks/use-deployments.ts
export function useDeployments() {
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await api.fetchDeployments();
        setDeployments(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return { deployments, loading, error };
}
```

**After** (React Query):
```typescript
// lib/queries/deployments.ts
export function useDeployments() {
  return useQuery({
    queryKey: ['deployments'],
    queryFn: api.fetchDeployments,
  });
}

// Usage
const { data: deployments, isLoading, error } = useDeployments();
```

**Step 6: Update Components**
```typescript
// Before
function DeploymentsPage() {
  const { deployments, loading, error } = useDeployments();
  
  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorState error={error} />;
  
  return <DeploymentList deployments={deployments} />;
}

// After
function DeploymentsPage() {
  const { data: deployments, isLoading, error } = useDeployments();
  
  if (isLoading) return <LoadingSkeleton />;
  if (error) return <ErrorState error={error} />;
  
  return <DeploymentList deployments={deployments} />;
}
```

**Benefits of React Query:**
- ✅ Automatic caching with configurable stale time
- ✅ Background refetching
- ✅ Optimistic updates
- ✅ Query invalidation and refetching
- ✅ Loading and error states built-in
- ✅ DevTools for debugging
- ✅ Request deduplication
- ✅ Pagination and infinite scroll support
- ✅ SSR support (Next.js)

**Hooks to Migrate:**
1. `use-deployments.ts` → `queries/deployments.ts`
2. `use-hosts.ts` → `queries/hosts.ts`
3. `use-providers.ts` → `queries/providers.ts`
4. `use-metrics.ts` → `queries/metrics.ts`
5. `use-logs.ts` → `queries/logs.ts` (consider WebSocket for real-time)
6. `use-deployment-status.ts` → `queries/deployment-status.ts`

**Estimated Effort:** 4-5 hours

---

### 3.6: Remove Legacy store.ts ⏳

**Current State:**
- `lib/store.ts` still contains:
  - Theme state (keep)
  - Projects state (migrate to React Query)
  - Deployments state (migrate to React Query)
  - UI state (sidebar open/close - keep or move to React state)

**Recommended Actions:**

**Step 1: Migrate Projects/Deployments to React Query**
```typescript
// lib/queries/projects.ts
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: api.fetchProjects,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
```

**Step 2: Decide on Theme/UI State**

**Option A:** Keep minimal Zustand store
```typescript
// lib/store.ts
interface UIState {
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'dark',
      setTheme: (theme) => set({ theme }),
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    { name: 'byteport-ui' }
  )
);
```

**Option B:** Move to React Context
```typescript
// context/ui-context.tsx
export function UIProvider({ children }) {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  return (
    <UIContext.Provider value={{ theme, setTheme, sidebarOpen, setSidebarOpen }}>
      {children}
    </UIContext.Provider>
  );
}
```

**Recommendation:** Keep Option A (minimal Zustand for UI state) because:
- UI state doesn't need server synchronization
- Zustand is perfect for client-side UI state
- No need to lift UI state to top-level Context
- Better performance for frequent updates (sidebar toggle)

**Step 3: Remove Server State from Store**
- Delete `projects`, `setProjects`, `addProject`, `updateProject`
- Delete `deployments`, `setDeployments`, `addDeployment`, `updateDeployment`, `removeDeployment`
- Keep only `theme` and `sidebar` state

**Estimated Effort:** 1-2 hours

---

## Summary of Remaining Work

| Sub-Phase | Effort | Status |
|-----------|--------|--------|
| 3.1 Sidebar consolidation | ✅ Complete | Done |
| 3.2 Header consolidation | ✅ Complete | Done |
| 3.3 Auth consolidation | ✅ Complete | Done |
| 3.4 Route fixes | 2-3 hours | ⏳ Pending |
| 3.5 React Query | 4-5 hours | ⏳ Pending |
| 3.6 Clean store.ts | 1-2 hours | ⏳ Pending |

**Total Remaining Effort:** 7-10 hours

---

## Benefits Achieved So Far

✅ **Reduced Code Duplication**
- 2 components removed (Sidebar, Header duplicates)
- ~150 lines of redundant code eliminated

✅ **Single Source of Truth**
- Auth state: `context/auth-context.tsx` only
- No more conflicting state between Zustand and Context

✅ **Clearer Architecture**
- Component hierarchy simplified
- Easier to understand data flow

✅ **Better Maintainability**
- Fewer files to update for auth changes
- Consistent component usage across app

---

## Next Steps (Recommended Priority)

1. **Route Consolidation** (2-3 hours)
   - Quick win, improves navigation consistency
   - Reduces confusion for developers and users

2. **React Query Migration** (4-5 hours)
   - High impact on app performance
   - Better caching and data synchronization
   - Modern best practice

3. **Clean Store** (1-2 hours)
   - Final cleanup after React Query migration
   - Completes the consolidation effort

---

## Testing Recommendations

After completing remaining phases:

1. **Unit Tests**
   - Test React Query hooks with MSW (Mock Service Worker)
   - Test UI state persistence

2. **Integration Tests**
   - Test navigation between canonical routes
   - Test redirects from old routes
   - Test data fetching and caching

3. **E2E Tests**
   - Update Playwright tests to use canonical routes
   - Test full user flows with new architecture

---

## Documentation Updates Needed

- [ ] Update WARP.md with new route structure
- [ ] Document React Query patterns
- [ ] Update component usage guide
- [ ] Add caching strategy documentation
