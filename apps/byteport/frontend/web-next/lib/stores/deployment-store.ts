'use client';

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Deployment, DeployRequest, LogEntry, Metrics } from '../types';
import * as api from '../api';

interface DeploymentState {
  // State
  deployments: Deployment[];
  currentDeployment: Deployment | null;
  logs: Record<string, LogEntry[]>;
  metrics: Record<string, Metrics | null>;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchDeployments: () => Promise<void>;
  fetchDeployment: (id: string) => Promise<void>;
  createDeployment: (req: DeployRequest) => Promise<Deployment | null>;
  updateDeployment: (id: string, updates: Partial<DeployRequest>) => Promise<void>;
  terminateDeployment: (id: string) => Promise<void>;
  restartDeployment: (id: string) => Promise<void>;
  fetchLogs: (id: string) => Promise<void>;
  addLog: (id: string, log: LogEntry) => void;
  fetchMetrics: (id: string) => Promise<void>;
  setCurrentDeployment: (deployment: Deployment | null) => void;
  clearError: () => void;
  reset: () => void;
}

const initialState = {
  deployments: [],
  currentDeployment: null,
  logs: {},
  metrics: {},
  isLoading: false,
  error: null,
};

export const useDeploymentStore = create<DeploymentState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      fetchDeployments: async () => {
        set({ isLoading: true, error: null });
        try {
          const result = await api.listDeployments();
          set({ deployments: result.deployments, isLoading: false });
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to fetch deployments';
          set({ error: message, isLoading: false });
        }
      },

      fetchDeployment: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          const deployment = await api.getDeployment(id);
          set({ currentDeployment: deployment, isLoading: false });

          // Update in deployments list if exists
          const deployments = get().deployments;
          const index = deployments.findIndex((d) => d.id === id);
          if (index !== -1) {
            const newDeployments = [...deployments];
            newDeployments[index] = deployment;
            set({ deployments: newDeployments });
          } else {
            set({ deployments: [...deployments, deployment] });
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to fetch deployment';
          set({ error: message, isLoading: false });
        }
      },

      createDeployment: async (req: DeployRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.deployApp(req);
          const newDeployment = await api.getDeployment(response.id);
          set((state) => ({
            deployments: [newDeployment, ...state.deployments],
            currentDeployment: newDeployment,
            isLoading: false,
          }));
          return newDeployment;
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to create deployment';
          set({ error: message, isLoading: false });
          return null;
        }
      },

      updateDeployment: async (id: string, updates: Partial<DeployRequest>) => {
        set({ isLoading: true, error: null });
        try {
          const updated = await api.updateDeployment(id, updates);
          set((state) => ({
            deployments: state.deployments.map((d) => (d.id === id ? updated : d)),
            currentDeployment: state.currentDeployment?.id === id ? updated : state.currentDeployment,
            isLoading: false,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to update deployment';
          set({ error: message, isLoading: false });
        }
      },

      terminateDeployment: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.terminateDeployment(id);
          set((state) => ({
            deployments: state.deployments.filter((d) => d.id !== id),
            currentDeployment: state.currentDeployment?.id === id ? null : state.currentDeployment,
            isLoading: false,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to terminate deployment';
          set({ error: message, isLoading: false });
        }
      },

      restartDeployment: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
          await api.restartDeployment(id);
          await get().fetchDeployment(id);
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Failed to restart deployment';
          set({ error: message, isLoading: false });
        }
      },

      fetchLogs: async (id: string) => {
        try {
          const result = await api.getDeploymentLogs(id);
          set((state) => ({
            logs: { ...state.logs, [id]: result.logs },
          }));
        } catch (error) {
          console.error('Failed to fetch logs:', error);
        }
      },

      addLog: (id: string, log: LogEntry) => {
        set((state) => ({
          logs: {
            ...state.logs,
            [id]: [...(state.logs[id] || []), log],
          },
        }));
      },

      fetchMetrics: async (id: string) => {
        try {
          const metrics = await api.getDeploymentMetrics(id);
          set((state) => ({
            metrics: { ...state.metrics, [id]: metrics },
          }));
        } catch (error) {
          console.error('Failed to fetch metrics:', error);
        }
      },

      setCurrentDeployment: (deployment: Deployment | null) => {
        set({ currentDeployment: deployment });
      },

      clearError: () => {
        set({ error: null });
      },

      reset: () => {
        set(initialState);
      },
    }),
    { name: 'deployment-store' }
  )
);
