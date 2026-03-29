'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface SettingCardProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
  icon?: ReactNode;
  footer?: ReactNode;
}

export function SettingCard({
  title,
  description,
  children,
  className,
  icon,
  footer
}: SettingCardProps) {
  return (
    <Card className={cn('', className)}>
      <CardHeader>
        <div className="flex items-start gap-4">
          {icon && <div className="mt-1">{icon}</div>}
          <div className="flex-1 space-y-1">
            <CardTitle className="text-base">{title}</CardTitle>
            {description && (
              <CardDescription className="text-sm">{description}</CardDescription>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {children}
        {footer && <div className="pt-4 border-t">{footer}</div>}
      </CardContent>
    </Card>
  );
}
