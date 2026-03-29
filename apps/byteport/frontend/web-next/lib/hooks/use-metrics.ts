'use client';

import { useState, useEffect, useCallback } from 'react';
import { useDeploymentStore } from '../stores';
import type { Metrics, MetricsQuery } from '../types';
import { REFRESH_INTERVALS } from '../constants';
import { useMetricsStream } from './use-realtime';

interface UseMetricsOptions {
  stream?: boolean;
  autoFetch?: boolean;
  interval?: number;
  query?: MetricsQuery;
}

export function useMetrics(deploymentId: string | null, options: UseMetricsOptions = {}) {
  const {
    stream = false,
    autoFetch = true,
    interval = REFRESH_INTERVALS.METRICS,
  } = options;

  const { metrics: storeMetrics, fetchMetrics } = useDeploymentStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentMetrics, setCurrentMetrics] = useState<Metrics | null>(null);

  // Get metrics from store
  const storedMetrics = deploymentId ? storeMetrics[deploymentId] || null : null;

  // Auto-fetch metrics on mount
  useEffect(() => {
    if (deploymentId && autoFetch && !stream) {
      setIsLoading(true);
      fetchMetrics(deploymentId)
        .then(() => setIsLoading(false))
        .catch((err) => {
          setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
          setIsLoading(false);
        });
    }
  }, [deploymentId, autoFetch, stream, fetchMetrics]);

  // Auto-refresh metrics
  useEffect(() => {
    if (!deploymentId || stream || !autoFetch) return;

    const intervalId = setInterval(() => {
      fetchMetrics(deploymentId).catch((err) => {
        console.error('Failed to refresh metrics:', err);
      });
    }, interval);

    return () => clearInterval(intervalId);
  }, [deploymentId, stream, autoFetch, interval, fetchMetrics]);

  // Handle metrics streaming
  const handleNewMetrics = useCallback((metrics: Metrics) => {
    setCurrentMetrics(metrics);
  }, []);

  const handleStreamError = useCallback((error: Event) => {
    setError('Metrics stream error');
    console.error('Metrics stream error:', error);
  }, []);

  useMetricsStream(deploymentId, {
    onMetrics: handleNewMetrics,
    onError: handleStreamError,
    enabled: stream,
  });

  const metrics = stream ? currentMetrics : storedMetrics;

  const refresh = useCallback(async () => {
    if (!deploymentId) return;
    setIsLoading(true);
    setError(null);
    try {
      await fetchMetrics(deploymentId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
    } finally {
      setIsLoading(false);
    }
  }, [deploymentId, fetchMetrics]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    metrics,
    isLoading,
    error,
    refresh,
    clearError,
  };
}

export function useMetricsData(metrics: Metrics | null) {
  const cpuUsage = metrics?.cpu_usage || [];
  const memoryUsage = metrics?.memory_usage || [];
  const networkIn = metrics?.network_in || [];
  const networkOut = metrics?.network_out || [];
  const requestCount = metrics?.request_count || [];
  const errorRate = metrics?.error_rate || [];
  const responseTime = metrics?.response_time || [];

  const latestCpu = cpuUsage[cpuUsage.length - 1]?.value || 0;
  const latestMemory = memoryUsage[memoryUsage.length - 1]?.value || 0;
  const latestNetworkIn = networkIn[networkIn.length - 1]?.value || 0;
  const latestNetworkOut = networkOut[networkOut.length - 1]?.value || 0;
  const latestRequests = requestCount[requestCount.length - 1]?.value || 0;
  const latestErrorRate = errorRate[errorRate.length - 1]?.value || 0;
  const latestResponseTime = responseTime[responseTime.length - 1]?.value || 0;

  const averageCpu =
    cpuUsage.reduce((acc, point) => acc + point.value, 0) / (cpuUsage.length || 1);
  const averageMemory =
    memoryUsage.reduce((acc, point) => acc + point.value, 0) / (memoryUsage.length || 1);
  const averageResponseTime =
    responseTime.reduce((acc, point) => acc + point.value, 0) / (responseTime.length || 1);

  return {
    // Raw data
    cpuUsage,
    memoryUsage,
    networkIn,
    networkOut,
    requestCount,
    errorRate,
    responseTime,
    // Latest values
    latest: {
      cpu: latestCpu,
      memory: latestMemory,
      networkIn: latestNetworkIn,
      networkOut: latestNetworkOut,
      requests: latestRequests,
      errorRate: latestErrorRate,
      responseTime: latestResponseTime,
    },
    // Averages
    averages: {
      cpu: averageCpu,
      memory: averageMemory,
      responseTime: averageResponseTime,
    },
  };
}
