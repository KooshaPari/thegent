'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';
import { Fragment } from 'react';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: 'Home', href: '/' }];

  let currentPath = '';
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    const isLast = index === segments.length - 1;

    // Format the label
    const label = segment
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');

    breadcrumbs.push({
      label,
      href: isLast ? undefined : currentPath
    });
  });

  return breadcrumbs;
}

export function Breadcrumbs() {
  const pathname = usePathname();
  const breadcrumbs = generateBreadcrumbs(pathname || '/');

  // Don't show breadcrumbs on home page
  if (pathname === '/' || pathname === '/home') {
    return null;
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm">
      {breadcrumbs.map((crumb, index) => (
        <Fragment key={crumb.label}>
          {index > 0 && (
            <ChevronRight className="h-4 w-4 text-dark-secondary" />
          )}
          {crumb.href ? (
            <Link
              href={crumb.href}
              className="flex items-center gap-1 text-dark-onSurfaceVariant transition hover:text-dark-primary"
            >
              {index === 0 && <Home className="h-4 w-4" />}
              <span>{crumb.label}</span>
            </Link>
          ) : (
            <span className="font-medium text-dark-onSurface">{crumb.label}</span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}
