'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchInstances, fetchProjects } from '@/lib/api';
import { normalizeInstance } from '@/lib/normalizers';
import type { NormalizedInstanceRecord, Project } from '@/lib/types';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';

interface MetricCard {
  label: string;
  value: string | number;
  hint?: string;
}

type LoadState = 'pending' | 'ready';

type ErrorState = string | null;

export default function MonitorPage() {
  const router = useRouter();
  const { status } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [instances, setInstances] = useState<NormalizedInstanceRecord[]>([]);
  const [loading, setLoading] = useState<LoadState>('pending');
  const [error, setError] = useState<ErrorState>(null);

  const loadMonitorData = useCallback(async () => {
    setLoading('pending');
    setError(null);
    try {
      const [projectData, instanceData] = await Promise.all([fetchProjects(), fetchInstances()]);
      setProjects(projectData);
      setInstances(instanceData.map((instance) => normalizeInstance(instance)));
    } catch (err) {
      console.error('Failed to load monitor data', err);
      setError('Unable to retrieve deployment metrics.');
    } finally {
      setLoading('ready');
    }
  }, []);

  useEffect(() => {
    if (status === 'pending') return;
    if (status === 'unauthenticated') {
      router.replace('/login');
      return;
    }

    void loadMonitorData();
  }, [loadMonitorData, router, status]);

  const metrics: MetricCard[] = useMemo(() => {
    const activeProjects = projects.length;
    const activeInstances = instances.length;
    const totalResources = instances.reduce((count, instance) => count + (instance.resources?.length ?? 0), 0);

    return [
      { label: 'Projects', value: activeProjects, hint: 'Total projects under management' },
      { label: 'Instances', value: activeInstances, hint: 'Firecracker VMs orchestrated by Byteport' },
      { label: 'Provisioned resources', value: totalResources, hint: 'AWS + auxiliary resources tracked' }
    ];
  }, [instances, projects]);

  if (status === 'pending' || loading === 'pending') {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Checking deployments…</p>
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
            void loadMonitorData();
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
        title="Deployment Monitor"
        subtitle="Live view of orchestrated Byteport resources"
        action={
          <button
            type="button"
            onClick={() => router.push('/home')}
            className="rounded-lg border border-dark-primary px-4 py-2 text-sm font-medium text-dark-primary hover:bg-dark-primary/10"
          >
            Back to dashboard
          </button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {metrics.map((metric) => (
            <div
              key={metric.label}
              className="rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 shadow"
            >
              <p className="text-sm uppercase tracking-wide text-dark-secondary">{metric.label}</p>
              <p className="mt-2 text-3xl font-semibold text-dark-onSurface">{metric.value}</p>
              {metric.hint ? <p className="mt-1 text-xs text-dark-onSurfaceVariant">{metric.hint}</p> : null}
            </div>
          ))}
        </div>

        <div className="mt-10 space-y-4">
          <h2 className="text-lg font-semibold text-dark-onSurface">Recent activity</h2>
          <div className="rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 text-sm text-dark-secondary">
            <p>
              Activity feeds will surface deployment progress, health checks, and tunnel lifetimes once the new Go
              orchestrator pipelines are wired. For now, use the Kubernetes/AWS dashboards linked from each project for
              deeper debugging.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
