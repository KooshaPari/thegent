'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { buildAuthkitAuthorizeUrl, resolveRedirectUri } from '@/lib/authkit';
import { useAuth } from '@/context/auth-context';

export default function LoginPageClient() {
  const router = useRouter();
  const { status } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (status === 'authenticated') {
      router.replace('/home');
    }
  }, [status, router]);

  function handleWorkOSRedirect() {
    setError(null);
    setLoading(true);

    try {
      const state = crypto.randomUUID();
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('byteport_auth_state', state);
        sessionStorage.setItem('byteport_auth_redirect', resolveRedirectUri(window));
      }
      const authorizeUrl = buildAuthkitAuthorizeUrl(state);
      window.location.assign(authorizeUrl);
    } catch (err) {
      console.error('Failed to redirect to AuthKit', err);
      setError('WorkOS AuthKit is not configured. Please contact your administrator.');
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-dark-surface">
      <div className="w-full max-w-md rounded-2xl bg-dark-surfaceContainer p-10 shadow-xl">
        <div className="mb-8 text-center">
          <p className="text-sm uppercase tracking-wide text-dark-secondary">Byteport</p>
          <h1 className="mt-2 text-3xl font-semibold text-dark-onSurface">Welcome back</h1>
          <p className="mt-2 text-sm text-dark-onSurfaceVariant">
            Sign in with WorkOS AuthKit to orchestrate deployments across cloud targets.
          </p>
        </div>

        <div className="space-y-6">
          <button
            type="button"
            onClick={handleWorkOSRedirect}
            disabled={loading || status === 'pending'}
            className="w-full rounded-lg bg-dark-primary px-4 py-3 text-sm font-semibold text-dark-onSurface shadow-lg transition hover:bg-dark-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading || status === 'pending' ? 'Preparing redirect…' : 'Continue with WorkOS AuthKit'}
          </button>

          {error ? <p className="text-center text-sm text-red-400">{error}</p> : null}

          <p className="text-center text-xs text-dark-secondary">
            Having trouble? Confirm the AuthKit environment variables match the Zen MCP deployment.
          </p>
        </div>
      </div>
    </div>
  );
}
