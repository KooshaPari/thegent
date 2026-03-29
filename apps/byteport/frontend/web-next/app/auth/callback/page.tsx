'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { completeWorkosCallback } from '@/lib/api';
import { useAuth } from '@/context/auth-context';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh } = useAuth();
  const [status, setStatus] = useState<'pending' | 'success' | 'error'>('pending');
  const [message, setMessage] = useState<string>('Finalising authentication…');

  const code = useMemo(() => searchParams.get('code'), [searchParams]);
  const state = useMemo(() => searchParams.get('state'), [searchParams]);
  const error = useMemo(() => searchParams.get('error'), [searchParams]);
  const errorDescription = useMemo(() => searchParams.get('error_description'), [searchParams]);

  useEffect(() => {
    if (error) {
      setStatus('error');
      setMessage(errorDescription ?? 'Authentication request was rejected.');
      return;
    }

  async function finalize() {
    try {
      if (!code) {
        setStatus('error');
        setMessage('Missing authorisation code.');
        return;
      }

      const cachedState = sessionStorage.getItem('byteport_auth_state');
      if (cachedState && state && cachedState !== state) {
        throw new Error('State mismatch detected.');
      }
      await completeWorkosCallback({ code, state });
        sessionStorage.removeItem('byteport_auth_state');
        sessionStorage.removeItem('byteport_auth_redirect');
        await refresh();
        setStatus('success');
        setMessage('Authentication complete. Redirecting…');
        router.replace('/home');
      } catch (err) {
        console.error('Failed to complete WorkOS callback', err);
        setStatus('error');
        setMessage('Failed to complete authentication. Please try again or contact support.');
      }
    }

    void finalize();
  }, [code, error, errorDescription, refresh, router, state]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-dark-surface">
      <div className="w-full max-w-sm rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainer p-8 text-center shadow-lg">
        <h1 className="text-lg font-semibold text-dark-onSurface">WorkOS Sign-in</h1>
        <p className="mt-2 text-sm text-dark-onSurfaceVariant">{message}</p>
        {status === 'pending' ? (
          <div className="mt-6 flex justify-center">
            <span className="h-4 w-4 animate-ping rounded-full bg-dark-primary" />
          </div>
        ) : null}
        {status === 'error' ? (
          <button
            type="button"
            onClick={() => router.replace('/login')}
            className="mt-6 w-full rounded-md border border-dark-primary px-4 py-2 text-sm font-medium text-dark-primary"
          >
            Back to login
          </button>
        ) : null}
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-dark-surface">
          <div className="w-full max-w-sm rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainer p-8 text-center shadow-lg">
            <h1 className="text-lg font-semibold text-dark-onSurface">WorkOS Sign-in</h1>
            <p className="mt-2 text-sm text-dark-onSurfaceVariant">Preparing authentication…</p>
            <div className="mt-6 flex justify-center">
              <span className="h-4 w-4 animate-ping rounded-full bg-dark-primary" />
            </div>
          </div>
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
