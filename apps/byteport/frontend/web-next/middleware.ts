import { authkitMiddleware } from '@workos-inc/authkit-nextjs';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Route redirects mapping (legacy -> canonical)
const ROUTE_REDIRECTS: Record<string, string> = {
  '/home/settings': '/settings',
  '/home/settings/profile': '/settings/profile',
  '/home/settings/integrations': '/settings/integrations',
  '/home/projects': '/projects',
  '/home/projects/new': '/projects/new',
  '/home/instances': '/deployments',
  '/home/monitor': '/monitoring',
  '/home': '/dashboard',
};

const authMiddleware = authkitMiddleware();

export default async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check for exact matches first
  if (ROUTE_REDIRECTS[pathname]) {
    const url = request.nextUrl.clone();
    url.pathname = ROUTE_REDIRECTS[pathname];
    return NextResponse.redirect(url, 301); // Permanent redirect
  }
  
  // Check for prefix matches (e.g., /home/settings/* -> /settings/*)
  for (const [oldPath, newPath] of Object.entries(ROUTE_REDIRECTS)) {
    if (pathname.startsWith(oldPath + '/')) {
      const url = request.nextUrl.clone();
      url.pathname = pathname.replace(oldPath, newPath);
      return NextResponse.redirect(url, 301);
    }
  }
  
  // No redirect needed - apply authkit middleware
  // @ts-ignore - authkit middleware typing
  return authMiddleware(request);
}

// Match against pages that require auth
// Exclude static assets and KInfra routes
export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|kinfra|__status__|__action__|__logs__|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'
  ]
};
