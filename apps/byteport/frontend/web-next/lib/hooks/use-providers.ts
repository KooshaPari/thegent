'use client';

import { useEffect, useCallback } from 'react';
import { useProviderStore } from '../stores';
import type { ProviderConfig, ProviderName } from '../types';
import { REFRESH_INTERVALS } from '../constants';

export function useProviders(autoRefresh: boolean = false) {
  const {
    providers,
    isLoading,
    error,
    fetchProviders,
    connectProvider,
    updateProvider,
    disconnectProvider,
    testProvider,
    clearError,
  } = useProviderStore();

  // Auto-fetch providers on mount
  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchProviders();
    }, REFRESH_INTERVALS.PROVIDERS);

    return () => clearInterval(interval);
  }, [autoRefresh, fetchProviders]);

  const connect = useCallback(
    async (config: ProviderConfig) => {
      const success = await connectProvider(config);
      return success;
    },
    [connectProvider]
  );

  const update = useCallback(
    async (name: string, config: Partial<ProviderConfig>) => {
      const success = await updateProvider(name, config);
      return success;
    },
    [updateProvider]
  );

  const disconnect = useCallback(
    async (name: string) => {
      const success = await disconnectProvider(name);
      return success;
    },
    [disconnectProvider]
  );

  const test = useCallback(
    async (name: string) => {
      const success = await testProvider(name);
      return success;
    },
    [testProvider]
  );

  const refresh = useCallback(() => {
    return fetchProviders();
  }, [fetchProviders]);

  const getProvider = useCallback(
    (name: ProviderName) => {
      return providers.find((p) => p.name === name);
    },
    [providers]
  );

  const connectedProviders = providers.filter((p) => p.status === 'connected');
  const availableProviders = providers.filter((p) => p.status === 'disconnected');

  return {
    providers,
    connectedProviders,
    availableProviders,
    isLoading,
    error,
    connect,
    update,
    disconnect,
    test,
    refresh,
    getProvider,
    clearError,
  };
}

export function useProvider(name: ProviderName) {
  const {
    providers,
    isLoading,
    error,
    updateProvider,
    disconnectProvider,
    testProvider,
    clearError,
    fetchProviders,
  } = useProviderStore();

  const provider = providers.find((p) => p.name === name);

  // Fetch provider on mount
  useEffect(() => {
    fetchProviders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name]);

  const update = useCallback(
    async (config: Partial<ProviderConfig>) => {
      const success = await updateProvider(name, config);
      return success;
    },
    [name, updateProvider]
  );

  const disconnect = useCallback(async () => {
    const success = await disconnectProvider(name);
    return success;
  }, [name, disconnectProvider]);

  const test = useCallback(async () => {
    const success = await testProvider(name);
    return success;
  }, [name, testProvider]);

  const refresh = useCallback(async () => {
    await fetchProviders();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetchProviders]);

  return {
    provider,
    isLoading,
    error,
    update,
    disconnect,
    test,
    refresh,
    clearError,
  };
}
