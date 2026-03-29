'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ProviderName } from '@/lib/types';

export interface FreeTierLimit {
  provider: ProviderName;
  displayName: string;
  resources: FreeTierResource[];
}

export interface FreeTierResource {
  name: string;
  description: string;
  current: number;
  limit: number;
  unit: string;
  resetPeriod?: string;
}

interface FreeTierUsageProps {
  limits: FreeTierLimit[];
  className?: string;
}

interface ResourceUsageProps {
  resource: FreeTierResource;
}

function ResourceUsage({ resource }: ResourceUsageProps) {
  const percentage = (resource.current / resource.limit) * 100;
  const isAtLimit = percentage >= 100;
  const isWarning = percentage >= 80 && percentage < 100;
  const _isHealthy = percentage < 80;

  const getStatusIcon = () => {
    if (isAtLimit) return <AlertCircle className="h-4 w-4 text-destructive" />;
    if (isWarning) return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    return <CheckCircle2 className="h-4 w-4 text-green-500" />;
  };

  const getStatusColor = () => {
    if (isAtLimit) return 'bg-destructive';
    if (isWarning) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (isAtLimit) return 'Limit Reached';
    if (isWarning) return 'Near Limit';
    return 'Healthy';
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <div>
            <p className="text-sm font-medium">{resource.name}</p>
            <p className="text-xs text-muted-foreground">{resource.description}</p>
          </div>
        </div>
        <Badge
          variant={isAtLimit ? 'destructive' : 'secondary'}
          className={cn(
            'text-xs',
            isWarning && 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20'
          )}
        >
          {getStatusText()}
        </Badge>
      </div>

      <Progress
        value={Math.min(percentage, 100)}
        className="h-2"
        indicatorClassName={getStatusColor()}
      />

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>
          {resource.current.toLocaleString()} / {resource.limit.toLocaleString()} {resource.unit}
        </span>
        <div className="flex items-center gap-2">
          <span className={cn(
            'font-medium',
            isAtLimit && 'text-destructive',
            isWarning && 'text-yellow-600'
          )}>
            {percentage.toFixed(1)}%
          </span>
          {resource.resetPeriod && (
            <span className="text-xs">• Resets {resource.resetPeriod}</span>
          )}
        </div>
      </div>
    </div>
  );
}

export function FreeTierUsage({ limits, className }: FreeTierUsageProps) {
  const totalResources = limits.reduce((sum, limit) => sum + limit.resources.length, 0);
  const resourcesAtLimit = limits.reduce(
    (sum, limit) => sum + limit.resources.filter(r => (r.current / r.limit) >= 1).length,
    0
  );
  const resourcesNearLimit = limits.reduce(
    (sum, limit) => sum + limit.resources.filter(r => {
      const pct = (r.current / r.limit) * 100;
      return pct >= 80 && pct < 100;
    }).length,
    0
  );

  return (
    <div className={cn('space-y-4', className)}>
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Free Tier Status</CardTitle>
              <CardDescription>
                Monitor your usage across provider free tiers
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{totalResources - resourcesAtLimit}</div>
              <p className="text-xs text-muted-foreground">Resources Available</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span className="text-sm text-muted-foreground">Healthy</span>
              </div>
              <p className="text-2xl font-bold">
                {totalResources - resourcesAtLimit - resourcesNearLimit}
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                <span className="text-sm text-muted-foreground">Near Limit</span>
              </div>
              <p className="text-2xl font-bold text-yellow-600">{resourcesNearLimit}</p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-destructive" />
                <span className="text-sm text-muted-foreground">At Limit</span>
              </div>
              <p className="text-2xl font-bold text-destructive">{resourcesAtLimit}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Provider Cards */}
      {limits.map((limit) => (
        <Card key={limit.provider}>
          <CardHeader>
            <CardTitle className="text-base">{limit.displayName}</CardTitle>
            <CardDescription>
              {limit.resources.length} free tier {limit.resources.length === 1 ? 'resource' : 'resources'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {limit.resources.map((resource, idx) => (
              <ResourceUsage key={idx} resource={resource} />
            ))}
          </CardContent>
        </Card>
      ))}

      {limits.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">No free tier limits configured</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
