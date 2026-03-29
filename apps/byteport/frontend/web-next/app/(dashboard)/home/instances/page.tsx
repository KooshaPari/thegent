'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchInstances } from '@/lib/api';
import { normalizeInstance } from '@/lib/normalizers';
import type { NormalizedInstanceRecord } from '@/lib/types';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';

export default function InstancesPage() {
  const router = useRouter();
  const { status, user } = useAuth();
  const [instances, setInstances] = useState<NormalizedInstanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadInstances = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchInstances();
      setInstances(data.map((instance) => normalizeInstance(instance)));
    } catch (err) {
      console.error('Failed to load instances', err);
      setError('Unable to retrieve instances.');
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

    void loadInstances();
  }, [loadInstances, router, status]);

  const subtitle = useMemo(() => {
    if (!user) return 'Instances';
    const firstName = user.name?.split(' ')[0];
    return firstName ? `${firstName}'s instances` : `${user.name}'s instances`;
  }, [user]);

  if (status === 'pending' || loading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Loading instances…</p>
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
            void loadInstances();
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
      <DashboardHeader title="Instances" subtitle={subtitle} />
      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {instances.map((instance) => (
            <article
              key={instance.uuid}
              className="rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-5 shadow transition hover:-translate-y-1 hover:border-dark-primary"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-dark-onSurface">{instance.name}</h3>
                  <p className="text-xs uppercase tracking-wide text-dark-secondary">{instance.status}</p>
                </div>
                <span className="rounded-full border border-dark-surfaceVariant px-2 py-1 text-xs text-dark-onSurfaceVariant">
                  {instance.resources?.length ?? 0} resources
                </span>
              </div>

              <div className="mt-4 space-y-2 text-sm text-dark-onSurfaceVariant">
                {instance.resources && instance.resources.length > 0 ? (
                  instance.resources.slice(0, 4).map((resource, index) => (
                    <div key={`${instance.uuid}-${index}`} className="flex justify-between">
                      <span>{resource.name ?? resource.id ?? 'Resource'}</span>
                      <span className="text-dark-secondary">{resource.type ?? resource.service}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-dark-secondary">No resources reported yet.</p>
                )}
              </div>
            </article>
          ))}

          {instances.length === 0 ? (
            <div className="col-span-full rounded-xl border border-dashed border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-8 text-center text-sm text-dark-secondary">
              No running instances. Deploy a project to provision infrastructure.
            </div>
          ) : null}
        </div>
      </section>
    </div>
  );
}
