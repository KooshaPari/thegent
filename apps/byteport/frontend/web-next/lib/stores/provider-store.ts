'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Provider, ProviderConfig } from '../types';
import * as api from '../api';

interface ProviderState {
  // State
  providers: Provider[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchProviders: () => Promise<void>;
  fetchProvider: (name: string) => Promise<Provider | null>;
  connectProvider: (config: ProviderConfig) => Promise<boolean>;
  updateProvider: (name: string, config: Partial<ProviderConfig>) => Promise<boolean>;
  disconnectProvider: (name: string) => Promise<boolean>;
  testProvider: (name: string) => Promise<boolean>;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  providers: [],
  isLoading: false,
  error: null,
};

export const useProviderStore = create<ProviderState>()(
  devtools(
    persist(
      (set, _get) => ({
        ...initialState,

        fetchProviders: async () => {
          set({ isLoading: true, error: null });
          try {
            const providers = await api.getProviders();
            set({ providers, isLoading: false });
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to fetch providers';
            set({ error: message, isLoading: false });
          }
        },

        fetchProvider: async (name: string) => {
          set({ isLoading: true, error: null });
          try {
            const provider = await api.getProvider(name);
            set((state) => {
              const providers = state.providers.filter((p) => p.name !== name);
              return {
                providers: [...providers, provider],
                isLoading: false,
              };
            });
            return provider;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to fetch provider';
            set({ error: message, isLoading: false });
            return null;
          }
        },

        connectProvider: async (config: ProviderConfig) => {
          set({ isLoading: true, error: null });
          try {
            const provider = await api.connectProvider(config);
            set((state) => ({
              providers: [...state.providers.filter((p) => p.name !== config.name), provider],
              isLoading: false,
            }));
            return true;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to connect provider';
            set({ error: message, isLoading: false });
            return false;
          }
        },

        updateProvider: async (name: string, config: Partial<ProviderConfig>) => {
          set({ isLoading: true, error: null });
          try {
            const provider = await api.updateProvider(name, config);
            set((state) => ({
              providers: state.providers.map((p) => (p.name === name ? provider : p)),
              isLoading: false,
            }));
            return true;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to update provider';
            set({ error: message, isLoading: false });
            return false;
          }
        },

        disconnectProvider: async (name: string) => {
          set({ isLoading: true, error: null });
          try {
            await api.disconnectProvider(name);
            set((state) => ({
              providers: state.providers.filter((p) => p.name !== name),
              isLoading: false,
            }));
            return true;
          } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to disconnect provider';
            set({ error: message, isLoading: false });
            return false;
          }
        },

        testProvider: async (name: string) => {
          try {
            const result = await api.testProviderConnection(name);
            return result.connected;
          } catch (error) {
            console.error('Provider test failed:', error);
            return false;
          }
        },

        clearError: () => {
          set({ error: null });
        },

        reset: () => {
          set(initialState);
        },
      }),
      {
        name: 'provider-store',
        partialize: (state) => ({ providers: state.providers }),
      }
    ),
    { name: 'provider-store' }
  )
);
