'use client';

import toast from 'react-hot-toast';
import type { DeploymentStatus } from './types';

/**
 * Toast notification utilities for BytePort
 *
 * Provides pre-configured toast notifications for common events
 */

// ============================================================================
// Deployment Notifications
// ============================================================================

export const deploymentToasts = {
  started: (deploymentName: string) => {
    return toast.success(`Deployment "${deploymentName}" started`, {
      icon: '🚀',
      duration: 3000,
    });
  },

  building: (deploymentName: string) => {
    return toast.loading(`Building "${deploymentName}"...`, {
      icon: '🔨',
    });
  },

  deploying: (deploymentName: string) => {
    return toast.loading(`Deploying "${deploymentName}"...`, {
      icon: '📦',
    });
  },

  completed: (deploymentName: string, url?: string) => {
    return toast.success(
      url
        ? `Deployment "${deploymentName}" completed! Available at ${url}`
        : `Deployment "${deploymentName}" completed!`,
      {
        icon: '✅',
        duration: 5000,
      }
    );
  },

  failed: (deploymentName: string, error?: string) => {
    return toast.error(
      error
        ? `Deployment "${deploymentName}" failed: ${error}`
        : `Deployment "${deploymentName}" failed`,
      {
        icon: '❌',
        duration: 6000,
      }
    );
  },

  terminated: (deploymentName: string) => {
    return toast(`Deployment "${deploymentName}" terminated`, {
      icon: '🛑',
      duration: 3000,
    });
  },

  statusChange: (
    deploymentName: string,
    status: DeploymentStatus,
    toastId?: string
  ) => {
    const messages: Record<DeploymentStatus, { message: string; icon: string }> = {
      pending: { message: 'Pending...', icon: '⏳' },
      building: { message: 'Building...', icon: '🔨' },
      deploying: { message: 'Deploying...', icon: '📦' },
      running: { message: 'Running', icon: '✅' },
      failed: { message: 'Failed', icon: '❌' },
      terminated: { message: 'Terminated', icon: '🛑' },
    };

    const config = messages[status];

    if (status === 'failed') {
      if (toastId) {
        toast.error(`${deploymentName}: ${config.message}`, { id: toastId });
      } else {
        return toast.error(`${deploymentName}: ${config.message}`, {
          icon: config.icon,
        });
      }
    } else if (status === 'running') {
      if (toastId) {
        toast.success(`${deploymentName}: ${config.message}`, { id: toastId });
      } else {
        return toast.success(`${deploymentName}: ${config.message}`, {
          icon: config.icon,
        });
      }
    } else {
      if (toastId) {
        toast.loading(`${deploymentName}: ${config.message}`, { id: toastId });
      } else {
        return toast.loading(`${deploymentName}: ${config.message}`, {
          icon: config.icon,
        });
      }
    }
  },
};

// ============================================================================
// Cost Notifications
// ============================================================================

export const costToasts = {
  alert: (message: string, threshold?: number) => {
    return toast.error(
      threshold
        ? `Cost Alert: ${message} (Threshold: $${threshold})`
        : `Cost Alert: ${message}`,
      {
        icon: '💰',
        duration: 8000,
      }
    );
  },

  warning: (message: string) => {
    return toast(`Cost Warning: ${message}`, {
      icon: '⚠️',
      duration: 6000,
    });
  },

  estimate: (cost: number, currency: string = 'USD') => {
    return toast(`Estimated cost: ${currency} ${cost.toFixed(2)}`, {
      icon: '💵',
      duration: 4000,
    });
  },
};

// ============================================================================
// Provider Notifications
// ============================================================================

export const providerToasts = {
  connected: (providerName: string) => {
    return toast.success(`Connected to ${providerName}`, {
      icon: '🔗',
      duration: 3000,
    });
  },

  disconnected: (providerName: string) => {
    return toast(`Disconnected from ${providerName}`, {
      icon: '🔌',
      duration: 3000,
    });
  },

  error: (providerName: string, error: string) => {
    return toast.error(`${providerName} error: ${error}`, {
      icon: '⚠️',
      duration: 5000,
    });
  },

  testing: (providerName: string) => {
    return toast.loading(`Testing connection to ${providerName}...`, {
      icon: '🔍',
    });
  },

  testSuccess: (providerName: string, toastId?: string) => {
    if (toastId) {
      toast.success(`${providerName} connection successful`, { id: toastId });
    } else {
      return toast.success(`${providerName} connection successful`, {
        icon: '✅',
      });
    }
  },

  testFailed: (providerName: string, toastId?: string) => {
    if (toastId) {
      toast.error(`${providerName} connection failed`, { id: toastId });
    } else {
      return toast.error(`${providerName} connection failed`, {
        icon: '❌',
      });
    }
  },
};

// ============================================================================
// General Notifications
// ============================================================================

export const generalToasts = {
  success: (message: string) => {
    return toast.success(message);
  },

  error: (message: string) => {
    return toast.error(message);
  },

  info: (message: string) => {
    return toast(message);
  },

  loading: (message: string) => {
    return toast.loading(message);
  },

  promise: <T,>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((error: any) => string);
    }
  ) => {
    return toast.promise(promise, messages);
  },
};

// ============================================================================
// API Notifications
// ============================================================================

export const apiToasts = {
  requestError: (endpoint: string, error: string) => {
    return toast.error(`API Error (${endpoint}): ${error}`, {
      duration: 5000,
    });
  },

  networkError: () => {
    return toast.error('Network error. Please check your connection.', {
      icon: '🌐',
      duration: 5000,
    });
  },

  unauthorized: () => {
    return toast.error('Unauthorized. Please log in again.', {
      icon: '🔒',
      duration: 5000,
    });
  },

  rateLimited: () => {
    return toast.error('Rate limit exceeded. Please try again later.', {
      icon: '⏱️',
      duration: 5000,
    });
  },
};

// Export toast instance for custom usage
export { toast };
