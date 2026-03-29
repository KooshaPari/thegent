'use client';

import { useState, useCallback, useEffect } from 'react';
import { useSSE } from './use-sse';
import type { LogEntry, LogLevel } from '../types';
import { getDeploymentApiBaseUrl } from '../config';

export interface UseLogStreamOptions {
  deploymentId: string | null;
  onLog?: (log: LogEntry) => void;
  onError?: (error: Event | string) => void;
  enabled?: boolean;
  maxLogs?: number;
}

/**
 * Hook for streaming real-time logs via SSE
 *
 * @example
 * ```tsx
 * const { logs, isConnected, clearLogs } = useLogStream({
 *   deploymentId: 'deploy-123',
 *   maxLogs: 1000,
 *   onLog: (log) => console.log(log.message),
 * });
 * ```
 */
export function useLogStream(options: UseLogStreamOptions) {
  const {
    deploymentId,
    onLog,
    onError,
    enabled = true,
    maxLogs = 1000,
  } = options;

  const [logs, setLogs] = useState<LogEntry[]>([]);

  const handleMessage = useCallback(
    (log: LogEntry) => {
      setLogs((prevLogs) => {
        const newLogs = [...prevLogs, log];
        // Limit the number of logs to prevent memory issues
        if (newLogs.length > maxLogs) {
          return newLogs.slice(-maxLogs);
        }
        return newLogs;
      });
      onLog?.(log);
    },
    [onLog, maxLogs]
  );

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  const filterLogs = useCallback(
    (filter: {
      level?: LogLevel;
      source?: 'build' | 'runtime' | 'system';
      search?: string;
    }) => {
      return logs.filter((log) => {
        if (filter.level && log.level !== filter.level) return false;
        if (filter.source && log.source !== filter.source) return false;
        if (
          filter.search &&
          !log.message.toLowerCase().includes(filter.search.toLowerCase())
        ) {
          return false;
        }
        return true;
      });
    },
    [logs]
  );

  const baseUrl = getDeploymentApiBaseUrl();
  const url = deploymentId
    ? `${baseUrl}/deployments/${deploymentId}/logs/stream`
    : '';

  const { state, disconnect, reconnect } = useSSE(url, {
    onMessage: handleMessage,
    onError,
    enabled: enabled && !!deploymentId,
    reconnect: true,
    maxRetries: 5,
  });

  return {
    logs,
    isConnected: state.isConnected,
    isConnecting: state.isConnecting,
    error: state.error,
    retryCount: state.retryCount,
    clearLogs,
    filterLogs,
    disconnect,
    reconnect,
  };
}

/**
 * Simplified hook for streaming logs via SSE (matches requirements spec)
 *
 * @example
 * ```tsx
 * const logs = useLogStream(deploymentId);
 * ```
 */
export function useSimpleLogStream(deploymentId: string) {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    if (!deploymentId) return;

    const eventSource = new EventSource(
      `http://localhost:8080/api/v1/deployments/${deploymentId}/logs?stream=true`
    );

    eventSource.onmessage = (e) => {
      try {
        const log: LogEntry = JSON.parse(e.data);
        setLogs((prev) => [...prev, log].slice(-1000)); // Keep last 1000 logs
      } catch (error) {
        console.error('Failed to parse log entry:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [deploymentId]);

  return logs;
}
