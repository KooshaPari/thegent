/**
 * Dashboard Header Component
 * 
 * This is a layout component for dashboard pages that provides a consistent
 * header with title, subtitle, and optional action buttons.
 * 
 * @deprecated Consider migrating to PageHeader from @/components/page-header
 */

import * as React from 'react';
import { cn } from '@/lib/utils';

interface DashboardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function DashboardHeader({
  title,
  subtitle,
  action,
  className,
  ...props
}: DashboardHeaderProps) {
  return (
    <div
      className={cn(
        'border-b border-dark-surfaceVariant bg-dark-surfaceContainerLow px-6 py-6',
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-dark-onSurface">{title}</h1>
          {subtitle && (
            <p className="mt-1 text-sm text-dark-onSurfaceVariant">{subtitle}</p>
          )}
        </div>
        {action && <div className="ml-4 flex items-center gap-2">{action}</div>}
      </div>
    </div>
  );
}
