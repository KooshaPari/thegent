'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export interface SSEState {
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  retryCount: number;
}

export interface SSEOptions {
  enabled?: boolean;
  reconnect?: boolean;
  reconnectDelay?: number;
  maxRetries?: number;
  onMessage?: (data: any) => void;
  onError?: (error: Event | string) => void;
  onOpen?: () => void;
}

export function useSSE(url: string, options: SSEOptions = {}) {
  const {
    enabled = true,
    reconnect = true,
    reconnectDelay = 3000,
    maxRetries = 5,
    onMessage,
    onError,
    onOpen,
  } = options;

  const [state, setState] = useState<SSEState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    retryCount: 0,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!url || eventSourceRef.current) return;

    setState((prev) => ({ ...prev, isConnecting: true, error: null }));

    try {
      const es = new EventSource(url);

      es.onopen = () => {
        setState({
          isConnected: true,
          isConnecting: false,
          error: null,
          retryCount: 0,
        });
        onOpen?.();
      };

      es.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      es.onerror = (event) => {
        console.error('SSE error:', event);
        const errorMessage = 'Connection error';

        setState((prev) => {
          const newRetryCount = prev.retryCount + 1;
          const shouldRetry = reconnect && newRetryCount < maxRetries;

          if (shouldRetry) {
            reconnectTimeoutRef.current = setTimeout(() => {
              cleanup();
              connect();
            }, reconnectDelay);
          }

          return {
            isConnected: false,
            isConnecting: shouldRetry,
            error: errorMessage,
            retryCount: newRetryCount,
          };
        });

        onError?.(event);
        es.close();
      };

      eventSourceRef.current = es;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to connect';
      setState((prev) => ({
        ...prev,
        isConnecting: false,
        error: message,
      }));
      onError?.(message);
    }
  }, [url, onOpen, onMessage, onError, reconnect, reconnectDelay, maxRetries, cleanup]);

  const disconnect = useCallback(() => {
    cleanup();
    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      retryCount: 0,
    });
  }, [cleanup]);

  const reconnectManually = useCallback(() => {
    cleanup();
    setState((prev) => ({ ...prev, retryCount: 0 }));
    connect();
  }, [cleanup, connect]);

  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      cleanup();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, url]); // Intentionally minimal deps to avoid reconnects

  return {
    state,
    disconnect,
    reconnect: reconnectManually,
    isConnected: state.isConnected,
    isConnecting: state.isConnecting,
    error: state.error,
  };
}
