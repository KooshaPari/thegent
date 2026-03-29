'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;

  // Theme
  theme: Theme;

  // Modals
  modals: Record<string, boolean>;

  // Notifications
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: number;
  }>;

  // Loading states
  globalLoading: boolean;

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebarCollapsed: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: Theme) => void;
  openModal: (id: string) => void;
  closeModal: (id: string) => void;
  toggleModal: (id: string) => void;
  addNotification: (notification: Omit<UIState['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  setGlobalLoading: (loading: boolean) => void;
}

const initialState = {
  sidebarOpen: true,
  sidebarCollapsed: false,
  theme: 'system' as Theme,
  modals: {},
  notifications: [],
  globalLoading: false,
};

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        toggleSidebar: () => {
          set((state) => ({ sidebarOpen: !state.sidebarOpen }));
        },

        setSidebarOpen: (open: boolean) => {
          set({ sidebarOpen: open });
        },

        toggleSidebarCollapsed: () => {
          set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
        },

        setSidebarCollapsed: (collapsed: boolean) => {
          set({ sidebarCollapsed: collapsed });
        },

        setTheme: (theme: Theme) => {
          set({ theme });
          // Apply theme to document
          if (typeof window !== 'undefined') {
            const root = window.document.documentElement;
            root.classList.remove('light', 'dark');

            if (theme === 'system') {
              const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light';
              root.classList.add(systemTheme);
            } else {
              root.classList.add(theme);
            }
          }
        },

        openModal: (id: string) => {
          set((state) => ({
            modals: { ...state.modals, [id]: true },
          }));
        },

        closeModal: (id: string) => {
          set((state) => ({
            modals: { ...state.modals, [id]: false },
          }));
        },

        toggleModal: (id: string) => {
          set((state) => ({
            modals: { ...state.modals, [id]: !state.modals[id] },
          }));
        },

        addNotification: (notification) => {
          const id = Math.random().toString(36).substring(7);
          const timestamp = Date.now();
          set((state) => ({
            notifications: [
              ...state.notifications,
              { ...notification, id, timestamp },
            ],
          }));

          // Auto-remove after 5 seconds
          setTimeout(() => {
            set((state) => ({
              notifications: state.notifications.filter((n) => n.id !== id),
            }));
          }, 5000);
        },

        removeNotification: (id: string) => {
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }));
        },

        clearNotifications: () => {
          set({ notifications: [] });
        },

        setGlobalLoading: (loading: boolean) => {
          set({ globalLoading: loading });
        },
      }),
      {
        name: 'ui-store',
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          sidebarCollapsed: state.sidebarCollapsed,
          theme: state.theme,
        }),
      }
    ),
    { name: 'ui-store' }
  )
);
