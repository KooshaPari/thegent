'use client';

import * as React from 'react';
import { MetricsChart, MultiMetricsChart } from './metrics-chart';
import { useSSE } from '@/lib/hooks/use-sse';
import type { Metrics, MetricDataPoint } from '@/lib/types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, Wifi, WifiOff, Activity } from 'lucide-react';
import { cn, formatBytes } from '@/lib/utils';
import { getDeploymentApiBaseUrl } from '@/lib/config';

export interface RealtimeMetricsDashboardProps extends React.HTMLAttributes<HTMLDivElement> {
  deploymentId: string | null;
  refreshInterval?: number;
  maxDataPoints?: number;
  showCombinedChart?: boolean;
}

/**
 * Real-time Metrics Dashboard Component
 *
 * Streams and displays real-time metrics from a deployment via SSE
 *
 * @example
 * ```tsx
 * <RealtimeMetricsDashboard
 *   deploymentId="deploy-123"
 *   maxDataPoints={50}
 *   showCombinedChart={true}
 * />
 * ```
 */
export function RealtimeMetricsDashboard({
  deploymentId,
  refreshInterval: _refreshInterval = 5000,
  maxDataPoints = 50,
  showCombinedChart = false,
  className,
  ...props
}: RealtimeMetricsDashboardProps) {
  const [cpuData, setCpuData] = React.useState<MetricDataPoint[]>([]);
  const [memoryData, setMemoryData] = React.useState<MetricDataPoint[]>([]);
  const [networkInData, setNetworkInData] = React.useState<MetricDataPoint[]>([]);
  const [networkOutData, setNetworkOutData] = React.useState<MetricDataPoint[]>([]);
  const [requestCountData, setRequestCountData] = React.useState<MetricDataPoint[]>([]);
  const [errorRateData, setErrorRateData] = React.useState<MetricDataPoint[]>([]);

  const handleMetrics = React.useCallback(
    (metrics: Metrics) => {
      const limitDataPoints = (data: MetricDataPoint[]) => {
        if (data.length > maxDataPoints) {
          return data.slice(-maxDataPoints);
        }
        return data;
      };

      const appendSeries = (
        series: MetricDataPoint[] | undefined,
        setter: React.Dispatch<React.SetStateAction<MetricDataPoint[]>>
      ) => {
        if (!series?.length) {
          return;
        }
        setter((prev) => limitDataPoints([...prev, ...series]));
      };

      appendSeries(metrics.cpu_usage, setCpuData);
      appendSeries(metrics.memory_usage, setMemoryData);
      appendSeries(metrics.network_in, setNetworkInData);
      appendSeries(metrics.network_out, setNetworkOutData);
      appendSeries(metrics.request_count, setRequestCountData);
      appendSeries(metrics.error_rate, setErrorRateData);
    },
    [maxDataPoints]
  );

  const baseUrl = getDeploymentApiBaseUrl();
  const url = deploymentId
    ? `${baseUrl}/deployments/${deploymentId}/metrics/stream`
    : '';

  const { state, reconnect } = useSSE(url, {
    onMessage: handleMetrics,
    enabled: !!deploymentId,
    reconnect: true,
    maxRetries: 5,
  });

  const clearMetrics = React.useCallback(() => {
    setCpuData([]);
    setMemoryData([]);
    setNetworkInData([]);
    setNetworkOutData([]);
    setRequestCountData([]);
    setErrorRateData([]);
  }, []);

  const getConnectionStatus = () => {
    if (state.isConnecting) {
      return {
        label: 'Connecting...',
        variant: 'secondary' as const,
        icon: <RefreshCw className="h-3 w-3 animate-spin" />,
      };
    }
    if (state.error) {
      return {
        label: `Error (Attempt ${state.retryCount})`,
        variant: 'destructive' as const,
        icon: <WifiOff className="h-3 w-3" />,
      };
    }
    if (state.isConnected) {
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

  // Calculate current values (latest data point)
  const currentCpu = cpuData.length > 0 ? cpuData[cpuData.length - 1].value : 0;
  const currentMemory = memoryData.length > 0 ? memoryData[memoryData.length - 1].value : 0;
  const currentNetworkIn = networkInData.length > 0 ? networkInData[networkInData.length - 1].value : 0;
  const currentNetworkOut = networkOutData.length > 0 ? networkOutData[networkOutData.length - 1].value : 0;

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
          <Badge variant={status.variant} className="gap-1.5">
            {status.icon}
            {status.label}
          </Badge>
          <span className="text-xs text-muted-foreground">
            {cpuData.length} data point{cpuData.length !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {state.error && (
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
            onClick={clearMetrics}
            disabled={cpuData.length === 0}
          >
            Clear Data
          </Button>
        </div>
      </div>

      {/* Current Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>CPU Usage</CardDescription>
            <CardTitle className="text-2xl">{currentCpu.toFixed(1)}%</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Memory Usage</CardDescription>
            <CardTitle className="text-2xl">{formatBytes(currentMemory)}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Network In</CardDescription>
            <CardTitle className="text-2xl">{formatBytes(currentNetworkIn)}/s</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Network Out</CardDescription>
            <CardTitle className="text-2xl">{formatBytes(currentNetworkOut)}/s</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Combined Chart */}
      {showCombinedChart && (
        <MultiMetricsChart
          title="All Metrics"
          description="Real-time overview of all metrics"
          datasets={[
            { label: 'CPU %', data: cpuData, color: '#3b82f6' },
            {
              label: 'Memory MB',
              data: memoryData.map((d) => ({
                timestamp: d.timestamp,
                value: d.value / (1024 * 1024), // Convert to MB
              })),
              color: '#10b981',
            },
          ]}
          height={350}
        />
      )}

      {/* Individual Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <MetricsChart
          title="CPU Usage"
          description="Percentage of CPU utilized"
          data={cpuData}
          color="#3b82f6"
          valueFormatter={(value) => `${value.toFixed(1)}%`}
          type="area"
        />

        <MetricsChart
          title="Memory Usage"
          description="Memory consumption"
          data={memoryData}
          color="#10b981"
          valueFormatter={formatBytes}
          type="area"
        />

        <MetricsChart
          title="Network In"
          description="Incoming network traffic"
          data={networkInData}
          color="#8b5cf6"
          valueFormatter={(value) => `${formatBytes(value)}/s`}
          type="line"
        />

        <MetricsChart
          title="Network Out"
          description="Outgoing network traffic"
          data={networkOutData}
          color="#f59e0b"
          valueFormatter={(value) => `${formatBytes(value)}/s`}
          type="line"
        />

        {requestCountData.length > 0 && (
          <MetricsChart
            title="Request Count"
            description="Number of requests per interval"
            data={requestCountData}
            color="#ec4899"
            valueFormatter={(value) => value.toFixed(0)}
            type="line"
          />
        )}

        {errorRateData.length > 0 && (
          <MetricsChart
            title="Error Rate"
            description="Percentage of failed requests"
            data={errorRateData}
            color="#ef4444"
            valueFormatter={(value) => `${value.toFixed(2)}%`}
            type="line"
          />
        )}
      </div>

      {/* Info Message */}
      {!state.isConnected && !state.isConnecting && cpuData.length === 0 && (
        <div className="text-center p-4 text-sm text-muted-foreground flex items-center justify-center gap-2">
          <Activity className="h-4 w-4" />
          Waiting for metrics from deployment...
        </div>
      )}
    </div>
  );
}
