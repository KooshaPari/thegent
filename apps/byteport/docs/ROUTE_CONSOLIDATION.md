# Route Consolidation - Migration Guide

**Date**: 2024
**Status**: ✅ Completed
**Phase**: 3.4 - Frontend Consolidation

## Overview

This document details the route consolidation work completed as part of Phase 3 frontend refactoring. The goal was to eliminate duplicate routes and establish canonical URLs for all frontend pages.

## Changes Summary

### Route Redirects Implemented

All legacy `/home/*` routes now permanently redirect (301) to their canonical equivalents:

| Legacy Route | Canonical Route | Status |
|--------------|-----------------|---------|
| `/home` | `/dashboard` | ✅ Redirected |
| `/home/settings` | `/settings` | ✅ Redirected |
| `/home/settings/profile` | `/settings/profile` | ✅ Redirected |
| `/home/settings/integrations` | `/settings/integrations` | ✅ Redirected |
| `/home/projects` | `/projects` | ✅ Redirected |
| `/home/projects/new` | `/projects/new` | ✅ Redirected |
| `/home/instances` | `/deployments` | ✅ Redirected |
| `/home/monitor` | `/monitoring` | ✅ Redirected |

### Implementation Details

#### 1. **Middleware Redirects** (`middleware.ts`)
- Enhanced Next.js middleware to intercept legacy route requests
- Implemented 301 permanent redirects for SEO and client caching
- Supports both exact path matches and prefix-based redirects
- Runs before authentication middleware to ensure all users benefit

```typescript
const ROUTE_REDIRECTS: Record<string, string> = {
  '/home/settings': '/settings',
  '/home/settings/profile': '/settings/profile',
  // ... more mappings
};
```

#### 2. **Component Link Updates**

Updated all internal links to use canonical routes:

- **`components/user-nav.tsx`**: Profile and Settings dropdown links
- **`app/(dashboard)/dashboard/page.tsx`**: Quick action buttons (Monitor, Integrations)
- **`app/(dashboard)/home/page.tsx`**: "New deployment" button
- **`app/(dashboard)/home/settings/page.tsx`**: Settings quick links

#### 3. **Legacy Routes Preserved**

The actual `/home/*` page files are still present for backward compatibility:
- `/app/(dashboard)/home/page.tsx`
- `/app/(dashboard)/home/settings/page.tsx`
- `/app/(dashboard)/home/settings/profile/page.tsx`
- `/app/(dashboard)/home/settings/integrations/page.tsx`
- `/app/(dashboard)/home/projects/new/page.tsx`
- `/app/(dashboard)/home/instances/page.tsx`
- `/app/(dashboard)/home/monitor/page.tsx`

**Recommendation**: These can be safely deleted in a future cleanup phase once telemetry confirms no direct access attempts.

## Benefits

### 1. **SEO & Accessibility**
- Single canonical URL per resource eliminates duplicate content issues
- Clearer, more intuitive URL structure for users
- 301 redirects preserve link equity and search rankings

### 2. **Development & Maintenance**
- Reduced cognitive load - one path to remember
- Easier to reason about routing logic
- Simpler navigation testing and debugging

### 3. **User Experience**
- Consistent bookmarking behavior
- More predictable URLs that match navigation hierarchy
- Eliminates confusion from multiple paths to same content

## Testing

### Manual Testing Checklist

- [x] Navigate to `/home` → redirects to `/dashboard`
- [x] Navigate to `/home/settings` → redirects to `/settings`
- [x] Navigate to `/home/settings/profile` → redirects to `/settings/profile`
- [x] User navigation dropdown links to `/settings/*`
- [x] Dashboard quick actions link to canonical routes
- [x] All existing functionality preserved after redirect

### Automated Testing (Recommended)

Add E2E tests to verify redirect behavior:

```typescript
// Example test case
test('legacy /home routes redirect to canonical URLs', async () => {
  const response = await fetch('/home/settings');
  expect(response.status).toBe(301);
  expect(response.headers.get('location')).toBe('/settings');
});
```

## Migration Guide for Developers

### For New Features
Always use canonical routes when adding links or navigation:

```tsx
// ✅ Good
<Link href="/settings/profile">Profile</Link>
<Link href="/deployments">Deployments</Link>

// ❌ Avoid
<Link href="/home/settings/profile">Profile</Link>
<Link href="/home/instances">Deployments</Link>
```

### For External Integrations
If you have external systems linking to BytePort:
- Update links to use canonical URLs when possible
- Legacy URLs will continue to work via redirects
- Plan migration timeline based on your system's update frequency

### For API Clients
API endpoints are unaffected - this is purely a frontend routing change.

## Future Work

### Phase 3.5: Cleanup Legacy Files (Optional)
Once confident all traffic uses canonical routes:
1. Add telemetry/logging for `/home/*` access attempts
2. Monitor for 30-90 days
3. Delete unused legacy page files
4. Remove redirect mappings from middleware

### Phase 3.6: React Query Migration
Continue with server state management improvements:
- Replace custom API hooks with React Query
- Centralize data fetching patterns
- Implement optimistic updates and cache invalidation

## References

- **Related Documentation**: 
  - `PHASE_3_CONSOLIDATION_PLAN.md` - Overall consolidation strategy
  - `REFACTORING_SUMMARY.md` - Complete refactoring overview
  
- **Modified Files**:
  - `frontend/web-next/middleware.ts`
  - `frontend/web-next/components/user-nav.tsx`
  - `frontend/web-next/app/(dashboard)/dashboard/page.tsx`
  - `frontend/web-next/app/(dashboard)/home/page.tsx`
  - `frontend/web-next/app/(dashboard)/home/settings/page.tsx`

## Rollback Procedure

If issues arise, rollback is straightforward:

1. **Remove redirect middleware**:
   ```typescript
   // In middleware.ts, remove customMiddleware and restore original
   export default authkitMiddleware({ /* ... */ });
   ```

2. **Revert component link changes**:
   ```bash
   git revert <commit-hash>
   ```

3. **Deploy**:
   Both old and new routes will work (since page files still exist)

## Questions & Support

For questions about this migration or to report issues:
- Check `WARP.md` for architecture overview
- Review `PHASE_3_CONSOLIDATION_PLAN.md` for context
- File issues with `[Routes]` tag in project tracker
