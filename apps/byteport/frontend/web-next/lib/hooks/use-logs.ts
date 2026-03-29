'use client';

import { useState, useEffect, useCallback } from 'react';
import { useDeploymentStore } from '../stores';
import type { LogEntry, LogLevel } from '../types';
import { useLogStream } from './use-realtime';

interface UseLogsOptions {
  stream?: boolean;
  autoFetch?: boolean;
  filter?: {
    level?: LogLevel;
    source?: 'build' | 'runtime' | 'system';
    search?: string;
  };
}

export function useLogs(deploymentId: string | null, options: UseLogsOptions = {}) {
  const { stream = false, autoFetch = true, filter } = options;
  const { logs: storeLogs, fetchLogs, addLog } = useDeploymentStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentLogs = deploymentId ? storeLogs[deploymentId] || [] : [];

  // Auto-fetch logs on mount
  useEffect(() => {
    if (deploymentId && autoFetch && !stream) {
      setIsLoading(true);
      fetchLogs(deploymentId)
        .then(() => setIsLoading(false))
        .catch((err) => {
          setError(err instanceof Error ? err.message : 'Failed to fetch logs');
          setIsLoading(false);
        });
    }
  }, [deploymentId, autoFetch, stream, fetchLogs]);

  // Handle log streaming
  const handleNewLog = useCallback(
    (log: LogEntry) => {
      if (deploymentId) {
        addLog(deploymentId, log);
      }
    },
    [deploymentId, addLog]
  );

  const handleStreamError = useCallback((error: Event) => {
    setError('Log stream error');
    console.error('Log stream error:', error);
  }, []);

  useLogStream(deploymentId, {
    onLog: handleNewLog,
    onError: handleStreamError,
    enabled: stream,
  });

  // Filter logs based on options
  const filteredLogs = currentLogs.filter((log) => {
    if (filter?.level && log.level !== filter.level) return false;
    if (filter?.source && log.source !== filter.source) return false;
    if (filter?.search && !log.message.toLowerCase().includes(filter.search.toLowerCase())) {
      return false;
    }
    return true;
  });

  const refresh = useCallback(async () => {
    if (!deploymentId) return;
    setIsLoading(true);
    setError(null);
    try {
      await fetchLogs(deploymentId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch logs');
    } finally {
      setIsLoading(false);
    }
  }, [deploymentId, fetchLogs]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    logs: filteredLogs,
    allLogs: currentLogs,
    isLoading,
    error,
    refresh,
    clearError,
  };
}

export function useLogFilter() {
  const [level, setLevel] = useState<LogLevel | undefined>();
  const [source, setSource] = useState<'build' | 'runtime' | 'system' | undefined>();
  const [search, setSearch] = useState<string>('');

  const reset = useCallback(() => {
    setLevel(undefined);
    setSource(undefined);
    setSearch('');
  }, []);

  return {
    filter: {
      level,
      source,
      search,
    },
    setLevel,
    setSource,
    setSearch,
    reset,
  };
}
