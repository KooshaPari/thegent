'use client';

import Link from 'next/link';
import { Home, ArrowLeft, Terminal } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-dark-surface px-6">
      <div className="w-full max-w-md text-center">
        {/* Icon */}
        <div className="mb-8 flex justify-center">
          <div className="rounded-full bg-dark-surfaceContainerHigh p-6">
            <Terminal className="h-16 w-16 text-dark-primary" />
          </div>
        </div>

        {/* Error Code */}
        <h1 className="mb-4 bg-gradient-to-r from-dark-primary to-blue-400 bg-clip-text text-8xl font-bold text-transparent">
          404
        </h1>

        {/* Title */}
        <h2 className="mb-4 text-2xl font-semibold text-dark-onSurface">
          Page Not Found
        </h2>

        {/* Description */}
        <p className="mb-8 text-dark-onSurfaceVariant">
          The page you're looking for doesn't exist or has been moved.
          Please check the URL or return to the home page.
        </p>

        {/* Actions */}
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-dark-primary px-6 py-3 text-sm font-medium text-white transition hover:bg-dark-primary/90"
          >
            <Home className="h-4 w-4" />
            Go Home
          </Link>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-dark-surfaceVariant px-6 py-3 text-sm font-medium text-dark-onSurface transition hover:bg-dark-surfaceContainerHigh"
          >
            <ArrowLeft className="h-4 w-4" />
            Go Back
          </button>
        </div>

        {/* Footer Note */}
        <p className="mt-12 text-xs text-dark-secondary">
          Error Code: 404 • BytePort Platform
        </p>
      </div>
    </div>
  );
}
