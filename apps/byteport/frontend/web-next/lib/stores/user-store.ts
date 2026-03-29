'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { NormalizedUser, AuthStatus } from '../types';
import * as api from '../api';

interface UserState {
  // State
  user: NormalizedUser | null;
  status: AuthStatus;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<boolean>;
  signup: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  updateProfile: (userId: string, updates: { Name?: string; Email?: string; Password?: string }) => Promise<boolean>;
  setUser: (user: NormalizedUser | null) => void;
  clearError: () => void;
}

const initialState = {
  user: null,
  status: 'pending' as AuthStatus,
  isLoading: false,
  error: null,
};

export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        login: async (email: string, password: string) => {
          set({ isLoading: true, error: null });
          try {
            const user = await api.login(email, password);
            const normalizedUser: NormalizedUser = {
              uuid: user.uuid,
              name: user.name,
              email: user.email,
              awsCreds: user.awsCreds,
              portfolio: user.portfolio,
              llmConfig: user.llmConfig,
            };
            set({
              user: normalizedUser,
              status: 'authenticated',
              isLoading: false,
            });
            return true;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Login failed';
            set({ error: message, status: 'unauthenticated', isLoading: false });
            return false;
          }
        },

        signup: async (name: string, email: string, password: string) => {
          set({ isLoading: true, error: null });
          try {
            const user = await api.signup(name, email, password);
            const normalizedUser: NormalizedUser = {
              uuid: user.uuid,
              name: user.name,
              email: user.email,
              awsCreds: user.awsCreds,
              portfolio: user.portfolio,
              llmConfig: user.llmConfig,
            };
            set({
              user: normalizedUser,
              status: 'authenticated',
              isLoading: false,
            });
            return true;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Signup failed';
            set({ error: message, status: 'unauthenticated', isLoading: false });
            return false;
          }
        },

        logout: () => {
          set({
            user: null,
            status: 'unauthenticated',
            error: null,
          });
        },

        fetchUser: async () => {
          set({ isLoading: true, error: null });
          try {
            const user = await api.fetchAuthenticatedUser();
            const normalizedUser: NormalizedUser = {
              uuid: user.uuid,
              name: user.name,
              email: user.email,
              awsCreds: user.awsCreds,
              portfolio: user.portfolio,
              llmConfig: user.llmConfig,
            };
            set({
              user: normalizedUser,
              status: 'authenticated',
              isLoading: false,
            });
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to fetch user';
            set({
              error: message,
              status: 'unauthenticated',
              isLoading: false,
            });
          }
        },

        updateProfile: async (userId: string, updates: { Name?: string; Email?: string; Password?: string }) => {
          set({ isLoading: true, error: null });
          try {
            const user = await api.updateUserProfile(userId, updates);
            const normalizedUser: NormalizedUser = {
              uuid: user.uuid,
              name: user.name,
              email: user.email,
              awsCreds: user.awsCreds,
              portfolio: user.portfolio,
              llmConfig: user.llmConfig,
            };
            set({ user: normalizedUser, isLoading: false });
            return true;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to update profile';
            set({ error: message, isLoading: false });
            return false;
          }
        },

        setUser: (user: NormalizedUser | null) => {
          set({
            user,
            status: user ? 'authenticated' : 'unauthenticated',
          });
        },

        clearError: () => {
          set({ error: null });
        },
      }),
      {
        name: 'user-store',
        partialize: (state) => ({ user: state.user, status: state.status }),
      }
    ),
    { name: 'user-store' }
  )
);
