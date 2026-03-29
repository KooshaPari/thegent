import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { useDeployments, useDeployment } from './use-deployments';
import { useDeploymentStore } from '../stores';
import { mockDeployment } from '@/test/utils';

// Mock the store
vi.mock('../stores', () => ({
  useDeploymentStore: vi.fn(),
}));

describe('useDeployments', () => {
  const mockFetchDeployments = vi.fn();
  const mockFetchDeployment = vi.fn();
  const mockCreateDeployment = vi.fn();
  const mockUpdateDeployment = vi.fn();
  const mockTerminateDeployment = vi.fn();
  const mockRestartDeployment = vi.fn();
  const mockSetCurrentDeployment = vi.fn();
  const mockClearError = vi.fn();

  const defaultStoreState = {
    deployments: [],
    currentDeployment: null,
    isLoading: false,
    error: null,
    fetchDeployments: mockFetchDeployments,
    fetchDeployment: mockFetchDeployment,
    createDeployment: mockCreateDeployment,
    updateDeployment: mockUpdateDeployment,
    terminateDeployment: mockTerminateDeployment,
    restartDeployment: mockRestartDeployment,
    setCurrentDeployment: mockSetCurrentDeployment,
    clearError: mockClearError,
  };

  beforeEach(() => {
    vi.useFakeTimers();
    (useDeploymentStore as any).mockReturnValue(defaultStoreState);
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('fetches deployments on mount', () => {
    renderHook(() => useDeployments());

    expect(mockFetchDeployments).toHaveBeenCalledTimes(1);
  });

  it('returns deployments from store', () => {
    const deployments = [mockDeployment(), mockDeployment()];
    (useDeploymentStore as any).mockReturnValue({
      ...defaultStoreState,
      deployments,
    });

    const { result } = renderHook(() => useDeployments());

    expect(result.current.deployments).toEqual(deployments);
  });

  it('returns loading state from store', () => {
    (useDeploymentStore as any).mockReturnValue({
      ...defaultStoreState,
      isLoading: true,
    });

    const { result } = renderHook(() => useDeployments());

    expect(result.current.isLoading).toBe(true);
  });

  it('returns error from store', () => {
    (useDeploymentStore as any).mockReturnValue({
      ...defaultStoreState,
      error: 'Failed to fetch',
    });

    const { result } = renderHook(() => useDeployments());

    expect(result.current.error).toBe('Failed to fetch');
  });

  it('calls createDeployment when deploy is invoked', async () => {
    const newDeployment = mockDeployment();
    mockCreateDeployment.mockResolvedValue(newDeployment);

    const { result } = renderHook(() => useDeployments());

    const deployRequest = {
      name: 'New App',
      type: 'frontend' as const,
      provider: 'vercel' as const,
    };

    await act(async () => {
      await result.current.deploy(deployRequest);
    });

    expect(mockCreateDeployment).toHaveBeenCalledWith(deployRequest);
  });

  it('calls fetchDeployments when refresh is invoked', async () => {
    const { result } = renderHook(() => useDeployments());

    await act(async () => {
      await result.current.refresh();
    });

    // Called once on mount + once manually
    expect(mockFetchDeployments).toHaveBeenCalledTimes(2);
  });

  it('calls fetchDeployment when getDeployment is invoked', async () => {
    const { result } = renderHook(() => useDeployments());

    await act(async () => {
      await result.current.getDeployment('deploy-123');
    });

    expect(mockFetchDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('calls updateDeployment when update is invoked', async () => {
    const { result } = renderHook(() => useDeployments());

    const updates = { name: 'Updated Name' };

    await act(async () => {
      await result.current.update('deploy-123', updates);
    });

    expect(mockUpdateDeployment).toHaveBeenCalledWith('deploy-123', updates);
  });

  it('calls terminateDeployment when terminate is invoked', async () => {
    const { result } = renderHook(() => useDeployments());

    await act(async () => {
      await result.current.terminate('deploy-123');
    });

    expect(mockTerminateDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('calls restartDeployment when restart is invoked', async () => {
    const { result } = renderHook(() => useDeployments());

    await act(async () => {
      await result.current.restart('deploy-123');
    });

    expect(mockRestartDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('selects deployment from list when selectDeployment is called', () => {
    const deployments = [
      mockDeployment({ id: 'deploy-1' }),
      mockDeployment({ id: 'deploy-2' }),
    ];

    (useDeploymentStore as any).mockReturnValue({
      ...defaultStoreState,
      deployments,
    });

    const { result } = renderHook(() => useDeployments());

    act(() => {
      result.current.selectDeployment('deploy-2');
    });

    expect(mockSetCurrentDeployment).toHaveBeenCalledWith(deployments[1]);
  });

  it('clears current deployment when selectDeployment is called with null', () => {
    const { result } = renderHook(() => useDeployments());

    act(() => {
      result.current.selectDeployment(null);
    });

    expect(mockSetCurrentDeployment).toHaveBeenCalledWith(null);
  });

  it('auto-refreshes when enabled', () => {
    renderHook(() => useDeployments(true));

    // Initial fetch on mount
    expect(mockFetchDeployments).toHaveBeenCalledTimes(1);

    // Advance time by 5 seconds (REFRESH_INTERVALS.DEPLOYMENTS = 5000ms)
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(mockFetchDeployments).toHaveBeenCalledTimes(2);

    // Advance another 5 seconds
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(mockFetchDeployments).toHaveBeenCalledTimes(3);
  });

  it('does not auto-refresh when disabled', () => {
    renderHook(() => useDeployments(false));

    expect(mockFetchDeployments).toHaveBeenCalledTimes(1);

    act(() => {
      vi.advanceTimersByTime(30000);
    });

    // Should still only be called once (on mount)
    expect(mockFetchDeployments).toHaveBeenCalledTimes(1);
  });

  it('cleans up interval on unmount', () => {
    const { unmount } = renderHook(() => useDeployments(true));

    expect(mockFetchDeployments).toHaveBeenCalledTimes(1);

    unmount();

    act(() => {
      vi.advanceTimersByTime(20000);
    });

    // Should still only be called once since component unmounted
    expect(mockFetchDeployments).toHaveBeenCalledTimes(1);
  });
});

describe('useDeployment', () => {
  const mockFetchDeployment = vi.fn();
  const mockUpdateDeployment = vi.fn();
  const mockTerminateDeployment = vi.fn();
  const mockRestartDeployment = vi.fn();
  const mockClearError = vi.fn();

  const defaultStoreState = {
    currentDeployment: null,
    isLoading: false,
    error: null,
    fetchDeployment: mockFetchDeployment,
    updateDeployment: mockUpdateDeployment,
    terminateDeployment: mockTerminateDeployment,
    restartDeployment: mockRestartDeployment,
    clearError: mockClearError,
  };

  beforeEach(() => {
    vi.useFakeTimers();
    (useDeploymentStore as any).mockReturnValue(defaultStoreState);
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.useRealTimers();
  });

  it('fetches deployment on mount when id is provided', () => {
    renderHook(() => useDeployment('deploy-123'));

    expect(mockFetchDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('does not fetch when id is null', () => {
    renderHook(() => useDeployment(null));

    expect(mockFetchDeployment).not.toHaveBeenCalled();
  });

  it('refetches when id changes', () => {
    const { rerender } = renderHook(({ id }) => useDeployment(id), {
      initialProps: { id: 'deploy-1' },
    });

    expect(mockFetchDeployment).toHaveBeenCalledWith('deploy-1');

    mockFetchDeployment.mockClear();

    rerender({ id: 'deploy-2' });

    expect(mockFetchDeployment).toHaveBeenCalledWith('deploy-2');
  });

  it('returns current deployment from store', () => {
    const deployment = mockDeployment();
    (useDeploymentStore as any).mockReturnValue({
      ...defaultStoreState,
      currentDeployment: deployment,
    });

    const { result } = renderHook(() => useDeployment('deploy-123'));

    expect(result.current.deployment).toEqual(deployment);
  });

  it('calls updateDeployment when update is invoked', async () => {
    const { result } = renderHook(() => useDeployment('deploy-123'));

    const updates = { name: 'New Name' };

    await act(async () => {
      await result.current.update(updates);
    });

    expect(mockUpdateDeployment).toHaveBeenCalledWith('deploy-123', updates);
  });

  it('does not call updateDeployment when id is null', async () => {
    const { result } = renderHook(() => useDeployment(null));

    // Check that result.current exists before calling methods
    expect(result.current).toBeDefined();
    expect(result.current.update).toBeDefined();

    await act(async () => {
      await result.current.update({ name: 'New Name' });
    });

    expect(mockUpdateDeployment).not.toHaveBeenCalled();
  });

  it('calls terminateDeployment when terminate is invoked', async () => {
    const { result } = renderHook(() => useDeployment('deploy-123'));

    await act(async () => {
      await result.current.terminate();
    });

    expect(mockTerminateDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('calls restartDeployment when restart is invoked', async () => {
    const { result } = renderHook(() => useDeployment('deploy-123'));

    await act(async () => {
      await result.current.restart();
    });

    expect(mockRestartDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('calls fetchDeployment when refresh is invoked', async () => {
    const { result } = renderHook(() => useDeployment('deploy-123'));

    mockFetchDeployment.mockClear();

    await act(async () => {
      await result.current.refresh();
    });

    expect(mockFetchDeployment).toHaveBeenCalledWith('deploy-123');
  });

  it('auto-refreshes when enabled', () => {
    renderHook(() => useDeployment('deploy-123', true));

    expect(mockFetchDeployment).toHaveBeenCalledTimes(1);

    // Advance time by 5 seconds (REFRESH_INTERVALS.DEPLOYMENTS = 5000ms)
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(mockFetchDeployment).toHaveBeenCalledTimes(2);
  });

  it('does not auto-refresh when id is null', () => {
    renderHook(() => useDeployment(null, true));

    expect(mockFetchDeployment).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(mockFetchDeployment).not.toHaveBeenCalled();
  });

  it('cleans up interval on unmount', () => {
    const { unmount } = renderHook(() => useDeployment('deploy-123', true));

    expect(mockFetchDeployment).toHaveBeenCalledTimes(1);

    unmount();

    act(() => {
      vi.advanceTimersByTime(20000);
    });

    expect(mockFetchDeployment).toHaveBeenCalledTimes(1);
  });
});
