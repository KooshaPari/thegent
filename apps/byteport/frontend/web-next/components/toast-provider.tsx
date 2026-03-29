'use client';

import { Toaster } from 'react-hot-toast';

/**
 * Toast Provider Component
 *
 * Wraps the application with react-hot-toast configuration
 * Add this to your root layout or app component
 */
export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      reverseOrder={false}
      gutter={8}
      toastOptions={{
        // Default options for all toasts
        duration: 4000,
        style: {
          background: 'hsl(var(--background))',
          color: 'hsl(var(--foreground))',
          border: '1px solid hsl(var(--border))',
        },
        // Success toasts
        success: {
          duration: 3000,
          iconTheme: {
            primary: 'hsl(var(--success))',
            secondary: 'hsl(var(--success-foreground))',
          },
        },
        // Error toasts
        error: {
          duration: 5000,
          iconTheme: {
            primary: 'hsl(var(--destructive))',
            secondary: 'hsl(var(--destructive-foreground))',
          },
        },
        // Loading toasts
        loading: {
          duration: Infinity,
          iconTheme: {
            primary: 'hsl(var(--primary))',
            secondary: 'hsl(var(--primary-foreground))',
          },
        },
      }}
    />
  );
}
