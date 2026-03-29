'use client';

import { useEffect, useRef, useCallback } from 'react';
import type { LogEntry, DeploymentStatusUpdate, Metrics } from '../types';
import * as api from '../api';

interface UseLogStreamOptions {
  onLog?: (log: LogEntry) => void;
  onError?: (error: Event) => void;
  enabled?: boolean;
}

export function useLogStream(deploymentId: string | null, options: UseLogStreamOptions = {}) {
  const { onLog, onError, enabled = true } = options;
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!deploymentId || !enabled) return;

    const eventSource = api.streamDeploymentLogs(
      deploymentId,
      (log) => {
        onLog?.(log);
      },
      (error) => {
        console.error('Log stream error:', error);
        onError?.(error);
      }
    );

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [deploymentId, enabled, onLog, onError]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  const reconnect = useCallback(() => {
    if (!deploymentId) return;

    disconnect();

    const eventSource = api.streamDeploymentLogs(
      deploymentId,
      (log) => {
        onLog?.(log);
      },
      (error) => {
        console.error('Log stream error:', error);
        onError?.(error);
      }
    );

    eventSourceRef.current = eventSource;
  }, [deploymentId, onLog, onError, disconnect]);

  return { disconnect, reconnect };
}

interface UseStatusStreamOptions {
  onStatusUpdate?: (status: DeploymentStatusUpdate) => void;
  onError?: (error: Event) => void;
  enabled?: boolean;
}

export function useStatusStream(deploymentId: string | null, options: UseStatusStreamOptions = {}) {
  const { onStatusUpdate, onError, enabled = true } = options;
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!deploymentId || !enabled) return;

    const eventSource = api.streamDeploymentStatus(
      deploymentId,
      (status) => {
        onStatusUpdate?.(status);
      },
      (error) => {
        console.error('Status stream error:', error);
        onError?.(error);
      }
    );

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [deploymentId, enabled, onStatusUpdate, onError]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  const reconnect = useCallback(() => {
    if (!deploymentId) return;

    disconnect();

    const eventSource = api.streamDeploymentStatus(
      deploymentId,
      (status) => {
        onStatusUpdate?.(status);
      },
      (error) => {
        console.error('Status stream error:', error);
        onError?.(error);
      }
    );

    eventSourceRef.current = eventSource;
  }, [deploymentId, onStatusUpdate, onError, disconnect]);

  return { disconnect, reconnect };
}

interface UseMetricsStreamOptions {
  onMetrics?: (metrics: Metrics) => void;
  onError?: (error: Event) => void;
  enabled?: boolean;
}

export function useMetricsStream(deploymentId: string | null, options: UseMetricsStreamOptions = {}) {
  const { onMetrics, onError, enabled = true } = options;
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!deploymentId || !enabled) return;

    const eventSource = api.streamDeploymentMetrics(
      deploymentId,
      (metrics) => {
        onMetrics?.(metrics);
      },
      (error) => {
        console.error('Metrics stream error:', error);
        onError?.(error);
      }
    );

    eventSourceRef.current = eventSource;

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [deploymentId, enabled, onMetrics, onError]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  const reconnect = useCallback(() => {
    if (!deploymentId) return;

    disconnect();

    const eventSource = api.streamDeploymentMetrics(
      deploymentId,
      (metrics) => {
        onMetrics?.(metrics);
      },
      (error) => {
        console.error('Metrics stream error:', error);
        onError?.(error);
      }
    );

    eventSourceRef.current = eventSource;
  }, [deploymentId, onMetrics, onError, disconnect]);

  return { disconnect, reconnect };
}
