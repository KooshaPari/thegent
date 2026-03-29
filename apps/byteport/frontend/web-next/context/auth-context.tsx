'use client';

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { AuthState, NormalizedUser, User } from '@/lib/types';
import { fetchAuthenticatedUser, logout as apiLogout } from '@/lib/api';
import { normalizeUser } from '@/lib/normalizers';

interface AuthContextValue extends AuthState {
  refresh: () => Promise<void>;
  setUser: (user: User | NormalizedUser | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'pending', user: null });

  const refresh = useCallback(async () => {
    try {
      const user = await fetchAuthenticatedUser();
      setState({ status: 'authenticated', user: normalizeUser(user) });
    } catch (error) {
      console.debug('Auth refresh failed:', error);
      setState({ status: 'unauthenticated', user: null });
    }
  }, []);

  const setUser = useCallback((user: User | NormalizedUser | null) => {
    if (user) {
      setState({ status: 'authenticated', user: normalizeUser(user) });
    } else {
      setState({ status: 'unauthenticated', user: null });
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch (error) {
      console.debug('Auth logout failed:', error);
    } finally {
      setState({ status: 'unauthenticated', user: null });
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const value = useMemo<AuthContextValue>(
    () => ({
      status: state.status,
      user: state.user,
      refresh,
      setUser,
      logout
    }),
    [state, refresh, setUser, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
