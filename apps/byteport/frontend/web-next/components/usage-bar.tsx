'use client';

import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UsageBarProps {
  title: string;
  description?: string;
  current: number;
  limit: number;
  unit?: string;
  showPercentage?: boolean;
  warningThreshold?: number;
  dangerThreshold?: number;
}

export function UsageBar({
  title,
  description,
  current,
  limit,
  unit = '',
  showPercentage = true,
  warningThreshold = 80,
  dangerThreshold = 95
}: UsageBarProps) {
  const percentage = (current / limit) * 100;
  const isWarning = percentage >= warningThreshold && percentage < dangerThreshold;
  const isDanger = percentage >= dangerThreshold;

  const getProgressColor = () => {
    if (isDanger) return 'bg-destructive';
    if (isWarning) return 'bg-yellow-500';
    return 'bg-primary';
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            {description && (
              <CardDescription className="text-xs">{description}</CardDescription>
            )}
          </div>
          {(isWarning || isDanger) && (
            <AlertTriangle
              className={cn(
                'h-4 w-4',
                isDanger ? 'text-destructive' : 'text-yellow-500'
              )}
            />
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Progress
            value={Math.min(percentage, 100)}
            className="h-2"
            indicatorClassName={getProgressColor()}
          />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {current.toLocaleString()} {unit} / {limit.toLocaleString()} {unit}
            </span>
            {showPercentage && (
              <span className={cn(isDanger && 'text-destructive', isWarning && 'text-yellow-500')}>
                {percentage.toFixed(1)}%
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
