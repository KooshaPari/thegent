'use client';

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Host, HostConfig, Metrics } from '../types';
import * as api from '../api';

interface HostState {
  // State
  hosts: Host[];
  currentHost: Host | null;
  hostMetrics: Record<string, Metrics | null>;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchHosts: () => Promise<void>;
  fetchHost: (id: string) => Promise<void>;
  registerHost: (config: HostConfig) => Promise<Host | null>;
  updateHost: (id: string, updates: Partial<HostConfig>) => Promise<void>;
  deleteHost: (id: string) => Promise<void>;
  fetchHostMetrics: (id: string) => Promise<void>;
  setCurrentHost: (host: Host | null) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  hosts: [],
  currentHost: null,
  hostMetrics: {},
  isLoading: false,
  error: null,
};

export const useHostStore = create<HostState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      fetchHosts: async () => {
        set({ isLoading: true, error: null });
        try {
          const hosts = await api.getHosts();
          set({ hosts, isLoading: false });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to fetch hosts';
          set({ error: message, isLoading: false });
        }
      },

      fetchHost: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const host = await api.getHost(id);
          set({ currentHost: host, isLoading: false });

          // Update in hosts list if exists
          const hosts = get().hosts;
          const index = hosts.findIndex((h) => h.id === id);
          if (index !== -1) {
            const newHosts = [...hosts];
            newHosts[index] = host;
            set({ hosts: newHosts });
          } else {
            set({ hosts: [...hosts, host] });
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to fetch host';
          set({ error: message, isLoading: false });
        }
      },

      registerHost: async (config: HostConfig) => {
        set({ isLoading: true, error: null });
        try {
          const host = await api.registerHost(config);
          set((state) => ({
            hosts: [...state.hosts, host],
            currentHost: host,
            isLoading: false,
          }));
          return host;
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to register host';
          set({ error: message, isLoading: false });
          return null;
        }
      },

      updateHost: async (id: string, updates: Partial<HostConfig>) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await api.updateHost(id, updates);
          set((state) => ({
            hosts: state.hosts.map((h) => (h.id === id ? updated : h)),
            currentHost: state.currentHost?.id === id ? updated : state.currentHost,
            isLoading: false,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to update host';
          set({ error: message, isLoading: false });
        }
      },

      deleteHost: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.deleteHost(id);
          set((state) => ({
            hosts: state.hosts.filter((h) => h.id !== id),
            currentHost: state.currentHost?.id === id ? null : state.currentHost,
            isLoading: false,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to delete host';
          set({ error: message, isLoading: false });
        }
      },

      fetchHostMetrics: async (id: string) => {
        try {
          const metrics = await api.getHostMetrics(id);
          set((state) => ({
            hostMetrics: { ...state.hostMetrics, [id]: metrics },
          }));
        } catch (error) {
          console.error('Failed to fetch host metrics:', error);
        }
      },

      setCurrentHost: (host: Host | null) => {
        set({ currentHost: host });
      },

      clearError: () => {
        set({ error: null });
      },

      reset: () => {
        set(initialState);
      },
    }),
    { name: 'host-store' }
  )
);
