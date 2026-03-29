import { renderHook, waitFor } from '@testing-library/react';
import { act } from 'react';
import { AuthProvider, useAuth } from '@/context/auth-context';
import { fetchAuthenticatedUser, logout as apiLogout } from '@/lib/api';
import { vi } from 'vitest';

// Mock the API functions
vi.mock('@/lib/api', () => ({
  fetchAuthenticatedUser: vi.fn(),
  logout: vi.fn(),
}));

// Mock the normalizer
vi.mock('@/lib/normalizers', () => ({
  normalizeUser: vi.fn((user) => user),
}));

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('provides auth context to children', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    };

    vi.mocked(fetchAuthenticatedUser).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // Initially should be pending
    expect(result.current.status).toBe('pending');

    // Wait for the auth check to complete
    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    expect(result.current.user).toEqual(mockUser);
  });

  it('handles unauthenticated state when fetch fails', async () => {
    vi.mocked(fetchAuthenticatedUser).mockRejectedValue(new Error('Not authenticated'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('unauthenticated');
    });

    expect(result.current.user).toBeNull();
  });

  it('refreshes user data', async () => {
    const initialUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    };

    const updatedUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Updated User',
    };

    vi.mocked(fetchAuthenticatedUser)
      .mockResolvedValueOnce(initialUser)
      .mockResolvedValueOnce(updatedUser);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    expect(result.current.user?.name).toBe('Test User');

    // Refresh
    await act(async () => {
      await result.current.refresh();
    });

    await waitFor(() => {
      expect(result.current.user?.name).toBe('Updated User');
    });
  });

  it('handles refresh failure gracefully', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    };

    vi.mocked(fetchAuthenticatedUser)
      .mockResolvedValueOnce(mockUser)
      .mockRejectedValueOnce(new Error('Refresh failed'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    // Refresh should fail and set to unauthenticated
    await act(async () => {
      await result.current.refresh();
    });

    await waitFor(() => {
      expect(result.current.status).toBe('unauthenticated');
      expect(result.current.user).toBeNull();
    });
  });

  it('sets user manually', async () => {
    vi.mocked(fetchAuthenticatedUser).mockRejectedValue(new Error('Not authenticated'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('unauthenticated');
    });

    const newUser = {
      id: 'user-456',
      email: 'manual@example.com',
      name: 'Manual User',
    };

    // Set user manually
    act(() => {
      result.current.setUser(newUser);
    });

    expect(result.current.status).toBe('authenticated');
    expect(result.current.user).toEqual(newUser);
  });

  it('clears user when setUser called with null', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    };

    vi.mocked(fetchAuthenticatedUser).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    // Clear user
    act(() => {
      result.current.setUser(null);
    });

    expect(result.current.status).toBe('unauthenticated');
    expect(result.current.user).toBeNull();
  });

  it('logs out successfully', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    };

    vi.mocked(fetchAuthenticatedUser).mockResolvedValue(mockUser);
    vi.mocked(apiLogout).mockResolvedValue(undefined);

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    // Logout
    await act(async () => {
      await result.current.logout();
    });

    expect(apiLogout).toHaveBeenCalled();
    expect(result.current.status).toBe('unauthenticated');
    expect(result.current.user).toBeNull();
  });

  it('handles logout API failure gracefully', async () => {
    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    };

    vi.mocked(fetchAuthenticatedUser).mockResolvedValue(mockUser);
    vi.mocked(apiLogout).mockRejectedValue(new Error('Logout failed'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    // Logout should still clear local state even if API fails
    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.status).toBe('unauthenticated');
    expect(result.current.user).toBeNull();
  });
});

describe('useAuth', () => {
  it('throws error when used outside AuthProvider', () => {
    // Suppress console.error for this test
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');

    spy.mockRestore();
  });

  it('returns auth context when used within AuthProvider', async () => {
    vi.mocked(fetchAuthenticatedUser).mockRejectedValue(new Error('Not authenticated'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('unauthenticated');
    });

    expect(result.current).toHaveProperty('status');
    expect(result.current).toHaveProperty('user');
    expect(result.current).toHaveProperty('refresh');
    expect(result.current).toHaveProperty('setUser');
    expect(result.current).toHaveProperty('logout');
  });

  it('has stable function references', async () => {
    vi.mocked(fetchAuthenticatedUser).mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
    });

    const { result, rerender } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await waitFor(() => {
      expect(result.current.status).toBe('authenticated');
    });

    const { refresh, setUser, logout } = result.current;

    // Rerender
    rerender();

    // Function references should be stable
    expect(result.current.refresh).toBe(refresh);
    expect(result.current.setUser).toBe(setUser);
    expect(result.current.logout).toBe(logout);
  });
});
