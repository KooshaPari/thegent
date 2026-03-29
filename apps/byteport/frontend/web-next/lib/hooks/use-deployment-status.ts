'use client';

import { useState, useCallback } from 'react';
import { useSSE } from './use-sse';
import type { DeploymentStatusUpdate } from '../types';
import { getDeploymentApiBaseUrl } from '../config';

export interface UseDeploymentStatusOptions {
  deploymentId: string | null;
  onStatusChange?: (status: DeploymentStatusUpdate) => void;
  onError?: (error: Event | string) => void;
  enabled?: boolean;
}

/**
 * Hook for streaming real-time deployment status updates via SSE
 *
 * @example
 * ```tsx
 * const { status, isConnected, reconnect } = useDeploymentStatus({
 *   deploymentId: 'deploy-123',
 *   onStatusChange: (status) => {
 *     console.log('Status:', status.status, 'Progress:', status.progress);
 *   },
 * });
 * ```
 */
export function useDeploymentStatus(options: UseDeploymentStatusOptions) {
  const { deploymentId, onStatusChange, onError, enabled = true } = options;
  const [currentStatus, setCurrentStatus] = useState<DeploymentStatusUpdate | null>(null);

  const handleMessage = useCallback(
    (status: DeploymentStatusUpdate) => {
      setCurrentStatus(status);
      onStatusChange?.(status);
    },
    [onStatusChange]
  );

  const baseUrl = getDeploymentApiBaseUrl();
  const url = deploymentId
    ? `${baseUrl}/deployments/${deploymentId}/status/stream`
    : '';

  const { state, disconnect, reconnect } = useSSE(url, {
    onMessage: handleMessage,
    onError,
    enabled: enabled && !!deploymentId,
    reconnect: true,
    maxRetries: 5,
  });

  return {
    status: currentStatus,
    isConnected: state.isConnected,
    isConnecting: state.isConnecting,
    error: state.error,
    retryCount: state.retryCount,
    disconnect,
    reconnect,
  };
}
