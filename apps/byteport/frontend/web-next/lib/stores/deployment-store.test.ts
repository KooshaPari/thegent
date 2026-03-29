import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useDeploymentStore } from './deployment-store';
import * as api from '../api';
import { mockDeployment, mockDeployRequest } from '@/test/utils';

// Mock the API module
vi.mock('../api', () => ({
  listDeployments: vi.fn(),
  getDeployment: vi.fn(),
  deployApp: vi.fn(),
  updateDeployment: vi.fn(),
  terminateDeployment: vi.fn(),
  restartDeployment: vi.fn(),
  getDeploymentLogs: vi.fn(),
  getDeploymentMetrics: vi.fn(),
}));

describe('DeploymentStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchDeployments', () => {
    it('fetches deployments successfully', async () => {
      const deployments = [mockDeployment(), mockDeployment()];
      (api.listDeployments as any).mockResolvedValue({ deployments, total: 2 });

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchDeployments();
      });

      expect(result.current.deployments).toEqual(deployments);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('sets loading state while fetching', async () => {
      const deployments = [mockDeployment()];
      (api.listDeployments as any).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ deployments, total: 1 }), 100))
      );

      const { result } = renderHook(() => useDeploymentStore());

      const promise = act(async () => {
        await result.current.fetchDeployments();
      });

      // Check loading state immediately
      expect(result.current.isLoading).toBe(true);

      await promise;

      expect(result.current.isLoading).toBe(false);
    });

    it('handles fetch error', async () => {
      const errorMessage = 'Network error';
      (api.listDeployments as any).mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchDeployments();
      });

      expect(result.current.error).toBe(errorMessage);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.deployments).toEqual([]);
    });
  });

  describe('fetchDeployment', () => {
    it('fetches single deployment successfully', async () => {
      const deployment = mockDeployment({ id: 'deploy-123' });
      (api.getDeployment as any).mockResolvedValue(deployment);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchDeployment('deploy-123');
      });

      expect(result.current.currentDeployment).toEqual(deployment);
      expect(result.current.error).toBeNull();
    });

    it('updates deployment in list if exists', async () => {
      const existingDeployment = mockDeployment({ id: 'deploy-123', name: 'Old Name' });
      const updatedDeployment = mockDeployment({ id: 'deploy-123', name: 'New Name' });

      (api.getDeployment as any).mockResolvedValue(updatedDeployment);

      const { result } = renderHook(() => useDeploymentStore());

      // Set initial deployment
      act(() => {
        result.current.fetchDeployments = async () => {
          result.current.deployments = [existingDeployment];
        };
      });

      await act(async () => {
        result.current.deployments = [existingDeployment];
        await result.current.fetchDeployment('deploy-123');
      });

      expect(result.current.deployments[0]).toEqual(updatedDeployment);
      expect(result.current.currentDeployment).toEqual(updatedDeployment);
    });

    it('adds deployment to list if not exists', async () => {
      const newDeployment = mockDeployment({ id: 'deploy-new' });
      (api.getDeployment as any).mockResolvedValue(newDeployment);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [mockDeployment({ id: 'deploy-existing' })];
        await result.current.fetchDeployment('deploy-new');
      });

      expect(result.current.deployments).toHaveLength(2);
      expect(result.current.deployments[1]).toEqual(newDeployment);
    });

    it('handles fetch error', async () => {
      (api.getDeployment as any).mockRejectedValue(new Error('Not found'));

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchDeployment('deploy-123');
      });

      expect(result.current.error).toBe('Not found');
      expect(result.current.currentDeployment).toBeNull();
    });
  });

  describe('createDeployment', () => {
    it('creates deployment successfully', async () => {
      const request = mockDeployRequest();
      const response = { id: 'deploy-new', message: 'Created' };
      const newDeployment = mockDeployment({ id: 'deploy-new' });

      (api.deployApp as any).mockResolvedValue(response);
      (api.getDeployment as any).mockResolvedValue(newDeployment);

      const { result } = renderHook(() => useDeploymentStore());

      let createdDeployment;
      await act(async () => {
        createdDeployment = await result.current.createDeployment(request);
      });

      expect(createdDeployment).toEqual(newDeployment);
      expect(result.current.deployments[0]).toEqual(newDeployment);
      expect(result.current.currentDeployment).toEqual(newDeployment);
    });

    it('adds new deployment to beginning of list', async () => {
      const existingDeployment = mockDeployment({ id: 'existing' });
      const newDeployment = mockDeployment({ id: 'new' });

      (api.deployApp as any).mockResolvedValue({ id: 'new' });
      (api.getDeployment as any).mockResolvedValue(newDeployment);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [existingDeployment];
        await result.current.createDeployment(mockDeployRequest());
      });

      expect(result.current.deployments[0]).toEqual(newDeployment);
      expect(result.current.deployments[1]).toEqual(existingDeployment);
    });

    it('handles create error', async () => {
      (api.deployApp as any).mockRejectedValue(new Error('Creation failed'));

      const { result } = renderHook(() => useDeploymentStore());

      let createdDeployment;
      await act(async () => {
        createdDeployment = await result.current.createDeployment(mockDeployRequest());
      });

      expect(createdDeployment).toBeNull();
      expect(result.current.error).toBe('Creation failed');
    });
  });

  describe('updateDeployment', () => {
    it('updates deployment successfully', async () => {
      const original = mockDeployment({ id: 'deploy-123', name: 'Original' });
      const updated = mockDeployment({ id: 'deploy-123', name: 'Updated' });

      (api.updateDeployment as any).mockResolvedValue(updated);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [original];
        result.current.currentDeployment = original;
        await result.current.updateDeployment('deploy-123', { name: 'Updated' });
      });

      expect(result.current.deployments[0].name).toBe('Updated');
      expect(result.current.currentDeployment?.name).toBe('Updated');
    });

    it('updates only matching deployment in list', async () => {
      const deploy1 = mockDeployment({ id: 'deploy-1' });
      const deploy2 = mockDeployment({ id: 'deploy-2', name: 'Original' });
      const updated = mockDeployment({ id: 'deploy-2', name: 'Updated' });

      (api.updateDeployment as any).mockResolvedValue(updated);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [deploy1, deploy2];
        await result.current.updateDeployment('deploy-2', { name: 'Updated' });
      });

      expect(result.current.deployments[0]).toEqual(deploy1);
      expect(result.current.deployments[1].name).toBe('Updated');
    });

    it('handles update error', async () => {
      (api.updateDeployment as any).mockRejectedValue(new Error('Update failed'));

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.updateDeployment('deploy-123', { name: 'New' });
      });

      expect(result.current.error).toBe('Update failed');
    });
  });

  describe('terminateDeployment', () => {
    it('removes deployment from list', async () => {
      const deploy1 = mockDeployment({ id: 'deploy-1' });
      const deploy2 = mockDeployment({ id: 'deploy-2' });

      (api.terminateDeployment as any).mockResolvedValue(undefined);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [deploy1, deploy2];
        await result.current.terminateDeployment('deploy-1');
      });

      expect(result.current.deployments).toEqual([deploy2]);
    });

    it('clears current deployment if terminated', async () => {
      const deployment = mockDeployment({ id: 'deploy-123' });

      (api.terminateDeployment as any).mockResolvedValue(undefined);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [deployment];
        result.current.currentDeployment = deployment;
        await result.current.terminateDeployment('deploy-123');
      });

      expect(result.current.currentDeployment).toBeNull();
      expect(result.current.deployments).toEqual([]);
    });

    it('keeps current deployment if different', async () => {
      const deploy1 = mockDeployment({ id: 'deploy-1' });
      const deploy2 = mockDeployment({ id: 'deploy-2' });

      (api.terminateDeployment as any).mockResolvedValue(undefined);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [deploy1, deploy2];
        result.current.currentDeployment = deploy2;
        await result.current.terminateDeployment('deploy-1');
      });

      expect(result.current.currentDeployment).toEqual(deploy2);
    });

    it('handles terminate error', async () => {
      (api.terminateDeployment as any).mockRejectedValue(new Error('Termination failed'));

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.terminateDeployment('deploy-123');
      });

      expect(result.current.error).toBe('Termination failed');
    });
  });

  describe('restartDeployment', () => {
    it('restarts deployment and fetches updated state', async () => {
      const original = mockDeployment({ id: 'deploy-123', status: 'terminated' });
      const restarted = mockDeployment({ id: 'deploy-123', status: 'starting' });

      (api.restartDeployment as any).mockResolvedValue(undefined);
      (api.getDeployment as any).mockResolvedValue(restarted);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        result.current.deployments = [original];
        await result.current.restartDeployment('deploy-123');
      });

      expect(api.restartDeployment).toHaveBeenCalledWith('deploy-123');
      expect(api.getDeployment).toHaveBeenCalledWith('deploy-123');
    });

    it('handles restart error', async () => {
      (api.restartDeployment as any).mockRejectedValue(new Error('Restart failed'));

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.restartDeployment('deploy-123');
      });

      expect(result.current.error).toBe('Restart failed');
    });
  });

  describe('fetchLogs', () => {
    it('fetches and stores logs', async () => {
      const logs = [
        { timestamp: '2024-01-01T00:00:00Z', level: 'info', message: 'Log 1' },
        { timestamp: '2024-01-01T00:00:01Z', level: 'info', message: 'Log 2' },
      ];

      (api.getDeploymentLogs as any).mockResolvedValue({ logs });

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchLogs('deploy-123');
      });

      expect(result.current.logs['deploy-123']).toEqual(logs);
    });

    it('handles multiple deployment logs separately', async () => {
      const logs1 = [{ timestamp: '2024-01-01T00:00:00Z', level: 'info', message: 'Log 1' }];
      const logs2 = [{ timestamp: '2024-01-01T00:00:01Z', level: 'info', message: 'Log 2' }];

      (api.getDeploymentLogs as any)
        .mockResolvedValueOnce({ logs: logs1 })
        .mockResolvedValueOnce({ logs: logs2 });

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchLogs('deploy-1');
        await result.current.fetchLogs('deploy-2');
      });

      expect(result.current.logs['deploy-1']).toEqual(logs1);
      expect(result.current.logs['deploy-2']).toEqual(logs2);
    });
  });

  describe('addLog', () => {
    it('adds log entry to deployment logs', () => {
      const { result } = renderHook(() => useDeploymentStore());

      const log = { timestamp: '2024-01-01T00:00:00Z', level: 'info', message: 'New log' };

      act(() => {
        result.current.addLog('deploy-123', log as any);
      });

      expect(result.current.logs['deploy-123']).toContainEqual(log);
    });

    it('appends to existing logs', () => {
      const { result } = renderHook(() => useDeploymentStore());

      const log1 = { timestamp: '2024-01-01T00:00:00Z', level: 'info', message: 'Log 1' };
      const log2 = { timestamp: '2024-01-01T00:00:01Z', level: 'info', message: 'Log 2' };

      act(() => {
        result.current.addLog('deploy-123', log1 as any);
        result.current.addLog('deploy-123', log2 as any);
      });

      expect(result.current.logs['deploy-123']).toEqual([log1, log2]);
    });
  });

  describe('fetchMetrics', () => {
    it('fetches and stores metrics', async () => {
      const metrics = {
        cpu: 45,
        memory: 512,
        requests: 1000,
        errors: 5,
      };

      (api.getDeploymentMetrics as any).mockResolvedValue(metrics);

      const { result } = renderHook(() => useDeploymentStore());

      await act(async () => {
        await result.current.fetchMetrics('deploy-123');
      });

      expect(result.current.metrics['deploy-123']).toEqual(metrics);
    });
  });

  describe('setCurrentDeployment', () => {
    it('sets current deployment', () => {
      const deployment = mockDeployment();
      const { result } = renderHook(() => useDeploymentStore());

      act(() => {
        result.current.setCurrentDeployment(deployment);
      });

      expect(result.current.currentDeployment).toEqual(deployment);
    });

    it('clears current deployment when set to null', () => {
      const { result } = renderHook(() => useDeploymentStore());

      act(() => {
        result.current.setCurrentDeployment(mockDeployment());
        result.current.setCurrentDeployment(null);
      });

      expect(result.current.currentDeployment).toBeNull();
    });
  });

  describe('clearError', () => {
    it('clears error state', () => {
      const { result } = renderHook(() => useDeploymentStore());

      act(() => {
        result.current.error = 'Some error';
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('reset', () => {
    it('resets store to initial state', () => {
      const { result } = renderHook(() => useDeploymentStore());

      act(() => {
        result.current.deployments = [mockDeployment()];
        result.current.currentDeployment = mockDeployment();
        result.current.error = 'Error';
        result.current.reset();
      });

      expect(result.current.deployments).toEqual([]);
      expect(result.current.currentDeployment).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.isLoading).toBe(false);
    });
  });
});
