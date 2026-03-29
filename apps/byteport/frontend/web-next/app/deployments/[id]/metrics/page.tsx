'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getDeployment, getDeploymentMetrics, streamDeploymentMetrics } from '@/lib/api';
import type { Deployment, Metrics, MetricsQuery, MetricDataPoint } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ChevronLeft,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Cpu,
  MemoryStick,
  Network,
  Activity,
  Clock,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import toast from 'react-hot-toast';

type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d';
type MetricType = 'cpu' | 'memory' | 'network' | 'requests';

interface ChartDataPoint {
  time: string;
  value: number;
}

interface NetworkChartPoint {
  time: string;
  inbound?: number;
  outbound?: number;
}

const TIME_RANGE_MS: Record<TimeRange, number> = {
  '1h': 60 * 60 * 1000,
  '6h': 6 * 60 * 60 * 1000,
  '24h': 24 * 60 * 60 * 1000,
  '7d': 7 * 24 * 60 * 60 * 1000,
  '30d': 30 * 24 * 60 * 60 * 1000,
};

const INTERVAL_LOOKUP: Record<TimeRange, NonNullable<MetricsQuery['interval']>> = {
  '1h': '1m',
  '6h': '5m',
  '24h': '15m',
  '7d': '1h',
  '30d': '1d',
};

function getTimeRangeMs(range: TimeRange): number {
  return TIME_RANGE_MS[range];
}

function getInterval(range: TimeRange): MetricsQuery['interval'] {
  return INTERVAL_LOOKUP[range];
}

function formatChartData(dataPoints: MetricDataPoint[], range: TimeRange): ChartDataPoint[] {
  return dataPoints.map((point) => ({
    time: format(new Date(point.timestamp), range === '1h' ? 'HH:mm' : 'MM/dd HH:mm'),
    value: point.value,
  }));
}

function calculateAverage(dataPoints: MetricDataPoint[]): number {
  if (!dataPoints.length) {
    return 0;
  }
  const sum = dataPoints.reduce((acc, point) => acc + point.value, 0);
  return Number((sum / dataPoints.length).toFixed(2));
}

function calculatePeak(dataPoints: MetricDataPoint[]): number {
  if (!dataPoints.length) {
    return 0;
  }
  const peak = Math.max(...dataPoints.map((point) => point.value));
  return Number(peak.toFixed(2));
}

function calculateTrend(dataPoints: MetricDataPoint[]): number {
  if (dataPoints.length < 2) {
    return 0;
  }

  const sliceSize = Math.min(10, Math.floor(dataPoints.length / 2));
  if (sliceSize === 0) {
    return 0;
  }

  const recent = dataPoints.slice(-sliceSize);
  const older = dataPoints.slice(-sliceSize * 2, -sliceSize);

  if (!older.length) {
    return 0;
  }

  const recentAvg = recent.reduce((acc, point) => acc + point.value, 0) / recent.length;
  const olderAvg = older.reduce((acc, point) => acc + point.value, 0) / older.length;

  if (olderAvg === 0) {
    return 0;
  }

  const trend = ((recentAvg - olderAvg) / olderAvg) * 100;
  return Number(trend.toFixed(1));
}

interface NetworkChartPointInternal extends NetworkChartPoint {
  timestamp: string;
}

function combineNetworkSeries(
  inbound: MetricDataPoint[],
  outbound: MetricDataPoint[],
  range: TimeRange
): NetworkChartPoint[] {
  const map = new Map<string, NetworkChartPointInternal>();

  const addPoint = (point: MetricDataPoint, key: 'inbound' | 'outbound') => {
    const existing = map.get(point.timestamp);
    const label = format(new Date(point.timestamp), range === '1h' ? 'HH:mm' : 'MM/dd HH:mm');

    if (existing) {
      existing[key] = point.value;
      return;
    }

    const initial: NetworkChartPointInternal = {
      timestamp: point.timestamp,
      time: label,
    };
    initial[key] = point.value;
    map.set(point.timestamp, initial);
  };

  inbound.forEach((point) => addPoint(point, 'inbound'));
  outbound.forEach((point) => addPoint(point, 'outbound'));

  return Array.from(map.values())
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .map(({ timestamp: _timestamp, ...rest }) => rest);
}

export default function DeploymentMetricsPage() {
  const params = useParams();
  const id = params.id as string;

  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>('1h');
  const [activeMetric, setActiveMetric] = useState<MetricType>('cpu');
  const [isStreaming, setIsStreaming] = useState(false);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  const loadDeploymentData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const deploymentData = await getDeployment(id);
      setDeployment(deploymentData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load deployment';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadMetrics = useCallback(async () => {
    try {
      const now = new Date();
      const startTime = new Date(now.getTime() - getTimeRangeMs(timeRange)).toISOString();
      const endTime = now.toISOString();

      const query: MetricsQuery = {
        deployment_id: id,
        start_time: startTime,
        end_time: endTime,
        interval: getInterval(timeRange),
      };

      const metricsData = await getDeploymentMetrics(id, query);
      setMetrics(metricsData);
    } catch (err) {
      console.error('Failed to load metrics:', err);
      toast.error('Failed to load metrics');
    }
  }, [id, timeRange]);

  useEffect(() => {
    void loadDeploymentData();
  }, [loadDeploymentData]);

  useEffect(() => {
    void loadMetrics();
  }, [loadMetrics]);

  const startStreaming = useCallback(() => {
    if (isStreaming || eventSource) return;

    try {
      setIsStreaming(true);
      const es = streamDeploymentMetrics(
        id,
        (metricsUpdate) => {
          setMetrics(metricsUpdate);
        },
        (error) => {
          console.error('Metrics streaming error:', error);
          setIsStreaming(false);
        }
      );

      setEventSource(es);
    } catch (err) {
      console.error('Failed to start metrics streaming:', err);
      setIsStreaming(false);
    }
  }, [id, isStreaming, eventSource]);

  const stopStreaming = useCallback(() => {
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
      setIsStreaming(false);
    }
  }, [eventSource]);

  useEffect(() => {
    if (timeRange === '1h') {
      startStreaming();
    } else {
      stopStreaming();
    }

    return () => {
      stopStreaming();
    };
  }, [timeRange, startStreaming, stopStreaming]);

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
            <span className="text-gray-600">Loading metrics...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !deployment) {
    return (
      <div className="container mx-auto p-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error loading metrics</p>
                <p className="text-sm text-red-700 mt-1">{error || 'Deployment not found'}</p>
                <div className="flex gap-2 mt-4">
                  <Link href={`/deployments/${id}`}>
                    <Button variant="outline" size="sm">
                      Back to Deployment
                    </Button>
                  </Link>
                  <Button onClick={loadDeploymentData} variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const cpuData = formatChartData(metrics?.cpu_usage ?? [], timeRange);
  const memoryData = formatChartData(metrics?.memory_usage ?? [], timeRange);
  const networkChartData = combineNetworkSeries(
    metrics?.network_in ?? [],
    metrics?.network_out ?? [],
    timeRange
  );
  const requestData = formatChartData(metrics?.request_count ?? [], timeRange);
  const responseTimeData = formatChartData(metrics?.response_time ?? [], timeRange);
  const hasNetworkData = networkChartData.length > 0;
  const cpuTrend = calculateTrend(metrics?.cpu_usage ?? []);
  const memoryTrend = calculateTrend(metrics?.memory_usage ?? []);
  const totalRequests = (metrics?.request_count ?? []).reduce<number>((sum, point) => sum + point.value, 0);

  return (
    <div className="container mx-auto p-8 space-y-6">
      {/* Header */}
      <div>
        <Link
          href={`/deployments/${id}`}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center gap-1 mb-4"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Deployment
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Performance Metrics</h1>
            <p className="text-gray-600">{deployment.name}</p>
          </div>

          <div className="flex items-center gap-2">
            {isStreaming && (
              <Badge className="bg-green-100 text-green-800">
                <div className="w-2 h-2 bg-green-600 rounded-full mr-2 animate-pulse" />
                Live
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Time Range Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-gray-600" />
              <span className="font-medium">Time Range:</span>
            </div>
            <div className="flex gap-2">
              {(['1h', '6h', '24h', '7d', '30d'] as const).map((range) => (
                <Button
                  key={range}
                  variant={timeRange === range ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeRange(range)}
                >
                  {range}
                </Button>
              ))}
              <Button variant="outline" size="sm" onClick={loadMetrics}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Cpu className="w-4 h-4" />
              CPU Usage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {calculateAverage(metrics?.cpu_usage ?? [])}%
            </div>
            <div className="flex items-center gap-2 mt-2 text-sm">
              <span className="text-gray-600">Peak: {calculatePeak(metrics?.cpu_usage ?? [])}%</span>
              {cpuTrend > 0 ? (
                <TrendingUp className="w-4 h-4 text-red-500" />
              ) : (
                <TrendingDown className="w-4 h-4 text-green-500" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <MemoryStick className="w-4 h-4" />
              Memory Usage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {calculateAverage(metrics?.memory_usage ?? [])} MB
            </div>
            <div className="flex items-center gap-2 mt-2 text-sm">
              <span className="text-gray-600">Peak: {calculatePeak(metrics?.memory_usage ?? [])} MB</span>
              {memoryTrend > 0 ? (
                <TrendingUp className="w-4 h-4 text-red-500" />
              ) : (
                <TrendingDown className="w-4 h-4 text-green-500" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Network className="w-4 h-4" />
              Network I/O
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {calculateAverage([
                ...(metrics?.network_in ?? []),
                ...(metrics?.network_out ?? [])
              ])} KB/s
            </div>
            <div className="text-sm text-gray-600 mt-2">
              In: {calculateAverage(metrics?.network_in ?? [])} KB/s
              <br />
              Out: {calculateAverage(metrics?.network_out ?? [])} KB/s
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalRequests}
            </div>
            <div className="text-sm text-gray-600 mt-2">
              Avg Response: {calculateAverage(metrics?.response_time ?? [])} ms
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Metric Selector */}
      <div className="flex gap-2 overflow-x-auto">
        {[
          { key: 'cpu' as const, label: 'CPU', icon: Cpu },
          { key: 'memory' as const, label: 'Memory', icon: MemoryStick },
          { key: 'network' as const, label: 'Network', icon: Network },
          { key: 'requests' as const, label: 'Requests', icon: Activity },
        ].map(({ key, label, icon: Icon }) => (
          <Button
            key={key}
            variant={activeMetric === key ? 'default' : 'outline'}
            size="sm"
            onClick={() => setActiveMetric(key)}
          >
            <Icon className="w-4 h-4 mr-2" />
            {label}
          </Button>
        ))}
      </div>

      {/* Charts */}
      {activeMetric === 'cpu' && cpuData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>CPU Usage Over Time</CardTitle>
            <CardDescription>Percentage of CPU capacity used</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={cpuData}>
                <defs>
                  <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'CPU %', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#cpuGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {activeMetric === 'memory' && memoryData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Memory Usage Over Time</CardTitle>
            <CardDescription>Memory consumption in megabytes</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={memoryData}>
                <defs>
                  <linearGradient id="memGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'Memory (MB)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#10b981"
                  fillOpacity={1}
                  fill="url(#memGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {activeMetric === 'network' && hasNetworkData && (
        <Card>
          <CardHeader>
            <CardTitle>Network Traffic Over Time</CardTitle>
            <CardDescription>Inbound and outbound network traffic in KB/s</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={networkChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis label={{ value: 'KB/s', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="inbound"
                  stroke="#8b5cf6"
                  name="Inbound"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="outbound"
                  stroke="#f59e0b"
                  name="Outbound"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {activeMetric === 'requests' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {requestData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Request Count</CardTitle>
                <CardDescription>Number of requests over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={requestData}>
                    <defs>
                      <linearGradient id="reqGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#6366f1"
                      fillOpacity={1}
                      fill="url(#reqGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {responseTimeData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Response Time</CardTitle>
                <CardDescription>Average response time in milliseconds</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={responseTimeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis label={{ value: 'ms', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#ef4444"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* No Data State */}
      {!metrics || (
        metrics.cpu_usage?.length === 0 &&
        metrics.memory_usage?.length === 0 &&
        metrics.network_in?.length === 0
      ) && (
        <Card>
          <CardContent className="py-12 text-center">
            <Activity className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium mb-2">No metrics available</h3>
            <p className="text-gray-600 mb-6">
              Metrics data is not yet available for this deployment
            </p>
            <Button onClick={loadMetrics} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
