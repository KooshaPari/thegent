'use client';

import { useEffect, useCallback } from 'react';
import { useHostStore } from '../stores';
import type { HostConfig } from '../types';
import { REFRESH_INTERVALS } from '../constants';

export function useHosts(autoRefresh: boolean = false) {
  const {
    hosts,
    currentHost,
    isLoading,
    error,
    fetchHosts,
    fetchHost,
    registerHost,
    updateHost,
    deleteHost,
    setCurrentHost,
    clearError,
  } = useHostStore();

  // Auto-fetch hosts on mount
  useEffect(() => {
    fetchHosts();
  }, [fetchHosts]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchHosts();
    }, REFRESH_INTERVALS.HOSTS);

    return () => clearInterval(interval);
  }, [autoRefresh, fetchHosts]);

  const register = useCallback(
    async (config: HostConfig) => {
      const host = await registerHost(config);
      return host;
    },
    [registerHost]
  );

  const update = useCallback(
    async (id: string, updates: Partial<HostConfig>) => {
      await updateHost(id, updates);
    },
    [updateHost]
  );

  const remove = useCallback(
    async (id: string) => {
      await deleteHost(id);
    },
    [deleteHost]
  );

  const refresh = useCallback(() => {
    return fetchHosts();
  }, [fetchHosts]);

  const getHost = useCallback(
    (id: string) => {
      return fetchHost(id);
    },
    [fetchHost]
  );

  const selectHost = useCallback(
    (id: string | null) => {
      if (id === null) {
        setCurrentHost(null);
      } else {
        const host = hosts.find((h) => h.id === id);
        if (host) {
          setCurrentHost(host);
        }
      }
    },
    [hosts, setCurrentHost]
  );

  const onlineHosts = hosts.filter((h) => h.status === 'online');
  const offlineHosts = hosts.filter((h) => h.status === 'offline');

  return {
    hosts,
    currentHost,
    onlineHosts,
    offlineHosts,
    isLoading,
    error,
    register,
    update,
    remove,
    refresh,
    getHost,
    selectHost,
    clearError,
  };
}

export function useHost(id: string | null, autoRefresh: boolean = false) {
  const {
    currentHost,
    hostMetrics,
    isLoading,
    error,
    fetchHost,
    fetchHostMetrics,
    updateHost,
    deleteHost,
    clearError,
  } = useHostStore();

  // Fetch host on mount or when id changes
  useEffect(() => {
    if (id) {
      fetchHost(id);
      fetchHostMetrics(id);
    }
  }, [id, fetchHost, fetchHostMetrics]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (!autoRefresh || !id) return;

    const interval = setInterval(() => {
      fetchHost(id);
      fetchHostMetrics(id);
    }, REFRESH_INTERVALS.HOSTS);

    return () => clearInterval(interval);
  }, [autoRefresh, id, fetchHost, fetchHostMetrics]);

  const metrics = id ? hostMetrics[id] || null : null;

  const update = useCallback(
    async (updates: Partial<HostConfig>) => {
      if (!id) return;
      await updateHost(id, updates);
    },
    [id, updateHost]
  );

  const remove = useCallback(async () => {
    if (!id) return;
    await deleteHost(id);
  }, [id, deleteHost]);

  const refresh = useCallback(async () => {
    if (!id) return;
    await fetchHost(id);
  }, [id, fetchHost]);

  const refreshMetrics = useCallback(async () => {
    if (!id) return;
    await fetchHostMetrics(id);
  }, [id, fetchHostMetrics]);

  return {
    host: currentHost,
    metrics,
    isLoading,
    error,
    update,
    remove,
    refresh,
    refreshMetrics,
    clearError,
  };
}
