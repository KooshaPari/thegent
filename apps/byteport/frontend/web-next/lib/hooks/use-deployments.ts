'use client';

import { useEffect, useCallback } from 'react';
import { useDeploymentStore } from '../stores';
import type { DeployRequest } from '../types';
import { REFRESH_INTERVALS } from '../constants';

export function useDeployments(autoRefresh: boolean = false) {
  const {
    deployments,
    currentDeployment,
    isLoading,
    error,
    fetchDeployments,
    fetchDeployment,
    createDeployment,
    updateDeployment,
    terminateDeployment,
    restartDeployment,
    setCurrentDeployment,
    clearError,
  } = useDeploymentStore();

  // Auto-fetch deployments on mount
  useEffect(() => {
    fetchDeployments();
  }, [fetchDeployments]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchDeployments();
    }, REFRESH_INTERVALS.DEPLOYMENTS);

    return () => clearInterval(interval);
  }, [autoRefresh, fetchDeployments]);

  const deploy = useCallback(
    async (request: DeployRequest) => {
      const result = await createDeployment(request);
      return result;
    },
    [createDeployment]
  );

  const refresh = useCallback(() => {
    return fetchDeployments();
  }, [fetchDeployments]);

  const getDeployment = useCallback(
    (id: string) => {
      return fetchDeployment(id);
    },
    [fetchDeployment]
  );

  const update = useCallback(
    (id: string, updates: Partial<DeployRequest>) => {
      return updateDeployment(id, updates);
    },
    [updateDeployment]
  );

  const terminate = useCallback(
    (id: string) => {
      return terminateDeployment(id);
    },
    [terminateDeployment]
  );

  const restart = useCallback(
    (id: string) => {
      return restartDeployment(id);
    },
    [restartDeployment]
  );

  const selectDeployment = useCallback(
    (id: string | null) => {
      if (id === null) {
        setCurrentDeployment(null);
      } else {
        const deployment = deployments.find((d) => d.id === id);
        if (deployment) {
          setCurrentDeployment(deployment);
        }
      }
    },
    [deployments, setCurrentDeployment]
  );

  return {
    deployments,
    currentDeployment,
    isLoading,
    error,
    deploy,
    refresh,
    getDeployment,
    update,
    terminate,
    restart,
    selectDeployment,
    clearError,
  };
}

export function useDeployment(id: string | null, autoRefresh: boolean = false) {
  const {
    currentDeployment,
    isLoading,
    error,
    fetchDeployment,
    updateDeployment,
    terminateDeployment,
    restartDeployment,
    clearError,
  } = useDeploymentStore();

  // Fetch deployment on mount or when id changes
  useEffect(() => {
    if (id) {
      fetchDeployment(id);
    }
  }, [id, fetchDeployment]);

  // Auto-refresh if enabled
  useEffect(() => {
    if (!autoRefresh || !id) return;

    const interval = setInterval(() => {
      fetchDeployment(id);
    }, REFRESH_INTERVALS.DEPLOYMENTS);

    return () => clearInterval(interval);
  }, [autoRefresh, id, fetchDeployment]);

  const update = useCallback(
    async (updates: Partial<DeployRequest>) => {
      if (!id) return;
      await updateDeployment(id, updates);
    },
    [id, updateDeployment]
  );

  const terminate = useCallback(async () => {
    if (!id) return;
    await terminateDeployment(id);
  }, [id, terminateDeployment]);

  const restart = useCallback(async () => {
    if (!id) return;
    await restartDeployment(id);
  }, [id, restartDeployment]);

  const refresh = useCallback(async () => {
    if (!id) return;
    await fetchDeployment(id);
  }, [id, fetchDeployment]);

  return {
    deployment: currentDeployment,
    isLoading,
    error,
    update,
    terminate,
    restart,
    refresh,
    clearError,
  };
}
