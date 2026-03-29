'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { useAuth } from '@/context/auth-context';

type SubmissionState = 'idle' | 'submitting' | 'success' | 'error';

export default function NewProjectPage() {
  const router = useRouter();
  const { status } = useAuth();
  const [submission, setSubmission] = useState<SubmissionState>('idle');
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.replace('/login');
    }
  }, [router, status]);

  if (status === 'pending') {
    return (
      <div className="flex flex-1 items-center justify-center bg-dark-surface">
        <p className="text-dark-onSurfaceVariant">Preparing project scaffolding…</p>
      </div>
    );
  }

  if (status === 'unauthenticated') {
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmission('submitting');
    setMessage(null);

    const formData = new FormData(event.currentTarget);
    const payload = {
      name: formData.get('name')?.toString().trim() ?? '',
      repositoryUrl: formData.get('repositoryUrl')?.toString().trim() ?? '',
      branch: formData.get('branch')?.toString().trim() ?? 'main',
      deployTarget: formData.get('deployTarget')?.toString() ?? 'aws'
    };

    try {
      // TODO: Swap this placeholder once the project creation endpoint lands.
      await new Promise((resolve) => setTimeout(resolve, 600));
      console.debug('Queued project blueprint', payload);
      event.currentTarget.reset();
      setSubmission('success');
      setMessage(
        'Blueprint captured. Run the Byteport CLI to provision infrastructure until the new orchestrator is wired.'
      );
    } catch (error) {
      console.error('Failed to queue project blueprint', error);
      setSubmission('error');
      setMessage('Unable to queue the project right now. Please try again in a moment.');
    }
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="New project"
        subtitle="Connect a repository and choose a deployment target to bootstrap a Byteport plan"
        action={
          <button
            type="button"
            onClick={() => router.push('/home')}
            className="rounded-lg border border-dark-primary px-4 py-2 text-sm font-medium text-dark-primary hover:bg-dark-primary/10"
          >
            Back to projects
          </button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        {submission === 'success' ? (
          <div className="mx-auto max-w-2xl space-y-4 rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-8 text-center">
            <h2 className="text-xl font-semibold text-dark-onSurface">Project queued</h2>
            <p className="text-sm text-dark-onSurfaceVariant">
              {message}
            </p>
            <div className="flex justify-center gap-3">
              <button
                type="button"
                onClick={() => router.push('/home')}
                className="rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-dark-onSurface shadow hover:bg-dark-primary/90"
              >
                Return to dashboard
              </button>
              <button
                type="button"
                onClick={() => {
                  setSubmission('idle');
                  setMessage(null);
                }}
                className="rounded-lg border border-dark-surfaceVariant px-4 py-2 text-sm font-medium text-dark-onSurfaceVariant hover:bg-dark-surfaceContainerLow"
              >
                Create another
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mx-auto max-w-3xl space-y-8">
            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium text-dark-onSurface">
                Project name
              </label>
              <input
                id="name"
                name="name"
                required
                placeholder="Byteport Cloud Landing"
                className="w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              />
              <p className="text-xs text-dark-onSurfaceVariant">
                This becomes the label for dashboards, CLI commands, and infrastructure logs.
              </p>
            </div>

            <div className="space-y-2">
              <label htmlFor="repositoryUrl" className="text-sm font-medium text-dark-onSurface">
                Git repository URL
              </label>
              <input
                id="repositoryUrl"
                name="repositoryUrl"
                required
                placeholder="https://github.com/byteport/examples"
                className="w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
              />
              <p className="text-xs text-dark-onSurfaceVariant">
                Byteport watches this repository for plan updates. Supports GitHub, GitLab, and generic Git remotes.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <label htmlFor="branch" className="text-sm font-medium text-dark-onSurface">
                  Default branch
                </label>
                <input
                  id="branch"
                  name="branch"
                  defaultValue="main"
                  className="w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
                />
                <p className="text-xs text-dark-onSurfaceVariant">Branch Byteport should observe for deployable revisions.</p>
              </div>

              <div className="space-y-2">
                <label htmlFor="deployTarget" className="text-sm font-medium text-dark-onSurface">
                  Deployment target
                </label>
                <select
                  id="deployTarget"
                  name="deployTarget"
                  defaultValue="aws"
                  className="w-full rounded-md border border-dark-surfaceVariant bg-dark-surfaceContainerHigh px-4 py-3 text-dark-onSurface focus:border-dark-primary focus:outline-none"
                >
                  <option value="aws">AWS (KInfra tunnel)</option>
                  <option value="gcp">GCP (coming soon)</option>
                  <option value="azure">Azure (coming soon)</option>
                  <option value="onprem">On-prem Firecracker</option>
                </select>
                <p className="text-xs text-dark-onSurfaceVariant">
                  Select where Byteport should provision infrastructure. Additional targets will unlock as the Python SDK
                  lands.
                </p>
              </div>
            </div>

            {message ? (
              <p
                className={
                  submission === 'error'
                    ? 'text-sm text-red-400'
                    : 'text-sm text-dark-onSurfaceVariant'
                }
              >
                {message}
              </p>
            ) : null}

            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={submission === 'submitting'}
                className="rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-dark-onSurface shadow hover:bg-dark-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submission === 'submitting' ? 'Creating…' : 'Create project'}
              </button>
              <button
                type="button"
                onClick={() => router.push('/home')}
                className="rounded-lg border border-dark-surfaceVariant px-4 py-2 text-sm font-medium text-dark-onSurfaceVariant hover:bg-dark-surfaceContainerLow"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </section>
    </div>
  );
}
