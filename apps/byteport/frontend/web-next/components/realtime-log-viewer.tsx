'use client';

import * as React from 'react';
import { LogViewer } from './log-viewer';
import { useLogStream as useLogStreamSSE } from '@/lib/hooks/use-log-stream';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface RealtimeLogViewerProps extends React.HTMLAttributes<HTMLDivElement> {
  deploymentId: string | null;
  autoScroll?: boolean;
  showLineNumbers?: boolean;
  terminalMode?: boolean;
  maxLogs?: number;
}

/**
 * Real-time Log Viewer Component
 *
 * Streams logs from a deployment via SSE and displays them in real-time
 *
 * @example
 * ```tsx
 * <RealtimeLogViewer
 *   deploymentId="deploy-123"
 *   autoScroll={true}
 *   terminalMode={true}
 * />
 * ```
 */
export function RealtimeLogViewer({
  deploymentId,
  autoScroll = true,
  showLineNumbers = true,
  terminalMode = true,
  maxLogs = 1000,
  className,
  ...props
}: RealtimeLogViewerProps) {
  const {
    logs,
    isConnected,
    isConnecting,
    error,
    retryCount,
    clearLogs,
    reconnect,
  } = useLogStreamSSE({
    deploymentId,
    enabled: !!deploymentId,
    maxLogs,
    onLog: (log) => {
      // Optional: Add custom log handling here
      console.debug('New log:', log);
    },
    onError: (error) => {
      console.error('Log stream error:', error);
    },
  });

  const getConnectionStatus = () => {
    if (isConnecting) {
      return {
        label: 'Connecting...',
        variant: 'secondary' as const,
        icon: <RefreshCw className="h-3 w-3 animate-spin" />,
      };
    }
    if (error) {
      return {
        label: `Error (Attempt ${retryCount})`,
        variant: 'destructive' as const,
        icon: <WifiOff className="h-3 w-3" />,
      };
    }
    if (isConnected) {
      return {
        label: 'Live',
        variant: 'success' as const,
        icon: <Wifi className="h-3 w-3" />,
      };
    }
    return {
      label: 'Disconnected',
      variant: 'secondary' as const,
      icon: <WifiOff className="h-3 w-3" />,
    };
  };

  const status = getConnectionStatus();

  if (!deploymentId) {
    return (
      <div className="flex items-center justify-center p-8 text-sm text-muted-foreground border rounded-lg">
        No deployment selected
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)} {...props}>
      {/* Connection Status Bar */}
      <div className="flex items-center justify-between gap-4 p-3 bg-muted/50 rounded-lg">
        <div className="flex items-center gap-2">
          <Badge
            variant={status.variant}
            className="gap-1.5"
          >
            {status.icon}
            {status.label}
          </Badge>
          {isConnected && (
            <span className="text-xs text-muted-foreground">
              {logs.length} log{logs.length !== 1 ? 's' : ''}
              {logs.length >= maxLogs && ` (showing last ${maxLogs})`}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {error && (
            <Button
              variant="outline"
              size="sm"
              onClick={reconnect}
              className="gap-1.5"
            >
              <RefreshCw className="h-3 w-3" />
              Retry Connection
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={clearLogs}
            disabled={logs.length === 0}
          >
            Clear Logs
          </Button>
        </div>
      </div>

      {/* Log Viewer */}
      <LogViewer
        logs={logs}
        autoScroll={autoScroll}
        showLineNumbers={showLineNumbers}
        terminalMode={terminalMode}
      />

      {/* Info Message */}
      {!isConnected && !isConnecting && logs.length === 0 && (
        <div className="text-center p-4 text-sm text-muted-foreground">
          Waiting for logs from deployment...
        </div>
      )}
    </div>
  );
}
