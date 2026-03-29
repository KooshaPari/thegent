'use client';

import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { fetchProjects } from '@/lib/api';
import type { Project } from '@/lib/types';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';

export default function HomePage() {
  const router = useRouter();
  const { status, user, refresh } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchProjects();
      setProjects(data);
    } catch (err) {
      console.error('Failed to load projects', err);
      setError('Unable to retrieve projects – verify backend connectivity.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (status === 'pending') return;
    if (status === 'unauthenticated') {
      router.replace('/login');
      return;
    }

    void loadProjects();
  }, [loadProjects, router, status]);

  const greeting = useMemo(() => {
    if (!user) return 'Hello';
    const firstName = user.name?.split(' ')[0];
    return firstName ? `Hello, ${firstName}` : `Hello, ${user.name}`;
  }, [user]);

  const subtitle = useMemo(() => {
    if (!user?.email) return 'Deploy anywhere from one plan.';
    return `Signed in as ${user.email}`;
  }, [user]);

  if (status === 'pending' || loading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Loading workspace…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-4 bg-dark-surface text-center">
        <h1 className="text-xl font-semibold text-dark-onSurface">{error}</h1>
        <button
          type="button"
          onClick={() => {
            void refresh();
            void loadProjects();
          }}
          className="rounded-md border border-dark-primary px-4 py-2 text-sm font-medium text-dark-primary"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title={greeting}
        subtitle={subtitle}
        action={
          <button
            type="button"
            onClick={() => router.push('/projects/new')}
            className="rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-dark-onSurface shadow hover:bg-dark-primary/90"
          >
            New deployment
          </button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold">Projects</h3>
            <p className="text-sm text-dark-secondary">
              Declarative plans synchronised from Git and orchestrated across providers.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {projects.map((project) => (
            <article
              key={project.uuid}
              className="group flex flex-col justify-between rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-5 shadow transition hover:-translate-y-1 hover:border-dark-primary"
            >
              <div className="space-y-2">
                <h4 className="text-lg font-semibold text-dark-onSurface">{project.name}</h4>
                <p className="line-clamp-3 text-sm text-dark-onSurfaceVariant">
                  {project.description || 'No description synced from repository yet.'}
                </p>
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-dark-surfaceVariant pt-4 text-xs text-dark-secondary">
                <span>{Object.keys(project.deployments ?? {}).length} active deployments</span>
                <a
                  className="font-medium text-dark-primary hover:underline"
                  href={project.access_url}
                  rel="noreferrer"
                  target="_blank"
                >
                  View site
                </a>
              </div>
            </article>
          ))}

          {projects.length === 0 ? (
            <div className="col-span-full rounded-xl border border-dashed border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-8 text-center text-sm text-dark-secondary">
              You have no deployments yet. Connect a Git repository to bootstrap a Byteport plan.
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
