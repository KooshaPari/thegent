'use client';

import * as React from 'react';
import { useDeploymentStatus } from '@/lib/hooks/use-deployment-status';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { RefreshCw, CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeploymentStatus } from '@/lib/types';
import { deploymentToasts } from '@/lib/toast';

export interface DeploymentMonitorProps extends React.HTMLAttributes<HTMLDivElement> {
  deploymentId: string | null;
  deploymentName?: string;
  showToasts?: boolean;
}

/**
 * Deployment Monitor Component
 *
 * Monitors deployment status in real-time via SSE and displays progress
 *
 * @example
 * ```tsx
 * <DeploymentMonitor
 *   deploymentId="deploy-123"
 *   deploymentName="My App"
 *   showToasts={true}
 * />
 * ```
 */
export function DeploymentMonitor({
  deploymentId,
  deploymentName = 'Deployment',
  showToasts = true,
  className,
  ...props
}: DeploymentMonitorProps) {
  const toastIdRef = React.useRef<string | undefined>(undefined);
  const previousStatusRef = React.useRef<DeploymentStatus | null>(null);

  const { status, isConnected, error, reconnect } = useDeploymentStatus({
    deploymentId,
    onStatusChange: (statusUpdate) => {
      if (!showToasts) return;

      const currentStatus = statusUpdate.status;
      const previousStatus = previousStatusRef.current;

      // Only show toast if status actually changed
      if (currentStatus === previousStatus) return;

      // Update toast based on status
      if (currentStatus === 'building') {
        toastIdRef.current = deploymentToasts.building(deploymentName);
      } else if (currentStatus === 'deploying') {
        deploymentToasts.statusChange(deploymentName, 'deploying', toastIdRef.current);
      } else if (currentStatus === 'running') {
        deploymentToasts.completed(deploymentName, statusUpdate.message);
        toastIdRef.current = undefined;
      } else if (currentStatus === 'failed') {
        deploymentToasts.failed(deploymentName, statusUpdate.message);
        toastIdRef.current = undefined;
      } else if (currentStatus === 'terminated') {
        deploymentToasts.terminated(deploymentName);
        toastIdRef.current = undefined;
      }

      previousStatusRef.current = currentStatus;
    },
  });

  const getStatusConfig = (deploymentStatus: DeploymentStatus) => {
    const configs: Record<
      DeploymentStatus,
      {
        label: string;
        variant: 'default' | 'secondary' | 'destructive' | 'success';
        icon: React.ReactNode;
        color: string;
      }
    > = {
      pending: {
        label: 'Pending',
        variant: 'secondary',
        icon: <Clock className="h-4 w-4" />,
        color: 'text-gray-500',
      },
      building: {
        label: 'Building',
        variant: 'default',
        icon: <Loader2 className="h-4 w-4 animate-spin" />,
        color: 'text-blue-500',
      },
      deploying: {
        label: 'Deploying',
        variant: 'default',
        icon: <Loader2 className="h-4 w-4 animate-spin" />,
        color: 'text-purple-500',
      },
      running: {
        label: 'Running',
        variant: 'success',
        icon: <CheckCircle className="h-4 w-4" />,
        color: 'text-green-500',
      },
      failed: {
        label: 'Failed',
        variant: 'destructive',
        icon: <XCircle className="h-4 w-4" />,
        color: 'text-red-500',
      },
      terminated: {
        label: 'Terminated',
        variant: 'secondary',
        icon: <XCircle className="h-4 w-4" />,
        color: 'text-gray-500',
      },
    };

    return configs[deploymentStatus] || configs.pending;
  };

  if (!deploymentId) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Deployment Monitor</CardTitle>
          <CardDescription>No deployment selected</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const statusConfig = status ? getStatusConfig(status.status) : null;

  return (
    <Card className={cn('', className)} {...props}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl">{deploymentName}</CardTitle>
            <CardDescription>
              {isConnected ? 'Live monitoring' : 'Connecting...'}
            </CardDescription>
          </div>
          {statusConfig && (
            <Badge variant={statusConfig.variant} className="gap-1.5">
              {statusConfig.icon}
              {statusConfig.label}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress Bar */}
        {status && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-medium">{status.progress}%</span>
            </div>
            <Progress value={status.progress} className="h-2" />
          </div>
        )}

        {/* Status Message */}
        {status?.message && (
          <div className="rounded-lg bg-muted p-3">
            <p className="text-sm font-mono text-muted-foreground">
              {status.message}
            </p>
          </div>
        )}

        {/* Last Updated */}
        {status && (
          <div className="text-xs text-muted-foreground">
            Last updated: {new Date(status.updated_at).toLocaleString()}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="space-y-2">
            <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
              Connection error. Retrying...
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={reconnect}
              className="w-full gap-1.5"
            >
              <RefreshCw className="h-3 w-3" />
              Retry Connection
            </Button>
          </div>
        )}

        {/* No Data State */}
        {!status && !error && isConnected && (
          <div className="text-center text-sm text-muted-foreground py-4">
            Waiting for deployment status...
          </div>
        )}
      </CardContent>
    </Card>
  );
}
