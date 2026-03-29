'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import Link from 'next/link';

export default function Error({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Global error boundary caught:', error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-dark-surface px-6">
      <div className="w-full max-w-lg text-center">
        {/* Icon */}
        <div className="mb-8 flex justify-center">
          <div className="rounded-full bg-red-500/10 p-6">
            <AlertTriangle className="h-16 w-16 text-red-500" />
          </div>
        </div>

        {/* Title */}
        <h1 className="mb-4 text-3xl font-bold text-dark-onSurface">
          Something went wrong
        </h1>

        {/* Description */}
        <p className="mb-2 text-dark-onSurfaceVariant">
          We encountered an unexpected error. This has been logged and we'll look into it.
        </p>

        {/* Error Details (in development) */}
        {process.env.NODE_ENV === 'development' && (
          <details className="mb-8 mt-4 rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-left">
            <summary className="cursor-pointer text-sm font-medium text-dark-onSurfaceVariant">
              Error Details (Development Only)
            </summary>
            <pre className="mt-4 overflow-auto text-xs text-dark-secondary">
              {error.message}
              {error.digest && `\nDigest: ${error.digest}`}
            </pre>
          </details>
        )}

        {/* Actions */}
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-dark-primary px-6 py-3 text-sm font-medium text-white transition hover:bg-dark-primary/90"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
          </button>
          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-dark-surfaceVariant px-6 py-3 text-sm font-medium text-dark-onSurface transition hover:bg-dark-surfaceContainerHigh"
          >
            <Home className="h-4 w-4" />
            Go Home
          </Link>
        </div>

        {/* Footer Note */}
        <p className="mt-12 text-xs text-dark-secondary">
          {error.digest ? `Error ID: ${error.digest} • ` : ''}BytePort Platform
        </p>
      </div>
    </div>
  );
}
