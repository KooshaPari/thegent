'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { updateUserProfile } from '@/lib/api';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';

type ProfileState = 'idle' | 'saving' | 'saved' | 'error';

export default function ProfileSettingsPage() {
  const router = useRouter();
  const { status, user, setUser } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [state, setState] = useState<ProfileState>('idle');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.replace('/login');
    }
  }, [router, status]);

  useEffect(() => {
    if (user) {
      setName(user.name ?? '');
      setEmail(user.email ?? '');
    }
  }, [user]);

  if (status === 'pending') {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Loading profile…</p>
      </div>
    );
  }

  if (status !== 'authenticated' || !user) {
    return null;
  }

  const currentUser = user;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState('saving');
    setMessage('');

    try {
      const updated = await updateUserProfile(currentUser.uuid, {
        Name: name !== currentUser.name ? name : undefined,
        Email: email !== currentUser.email ? email : undefined,
        Password: password || undefined
      });
      setUser(updated);
      setPassword('');
      setState('saved');
      setMessage('Profile updated successfully.');
    } catch (err) {
      console.error('Failed to update profile', err);
      setState('error');
      setMessage('Unable to save changes.');
    }
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader title="Profile" subtitle="Update personal details and credentials" />
      <section className="flex-1 overflow-y-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="max-w-xl space-y-6">
          <div>
            <label htmlFor="name" className="text-sm font-medium text-dark-onSurface">
              Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(event) => {
                setName(event.target.value);
                if (state !== 'idle') {
                  setState('idle');
                }
              }}
              className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="email" className="text-sm font-medium text-dark-onSurface">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                if (state !== 'idle') {
                  setState('idle');
                }
              }}
              className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
            />
          </div>
          <div>
            <label htmlFor="password" className="text-sm font-medium text-dark-onSurface">
              New password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Leave blank to keep current password"
              className="mt-2 w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
            />
          </div>

          {message ? (
            <p
              className={
                state === 'error'
                  ? 'text-sm text-red-400'
                  : state === 'saved'
                  ? 'text-sm text-dark-primary'
                  : 'text-sm text-dark-onSurfaceVariant'
              }
            >
              {message}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={state === 'saving'}
            className="rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-dark-onSurface shadow hover:bg-dark-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {state === 'saving' ? 'Saving…' : 'Save changes'}
          </button>
        </form>
      </section>
    </div>
  );
}
