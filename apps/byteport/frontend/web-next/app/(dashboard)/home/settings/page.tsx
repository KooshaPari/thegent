'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';

const QUICK_LINKS = [
  { label: 'Profile', href: '/settings/profile', description: 'Manage personal details and account security.' },
  {
    label: 'Integrations',
    href: '/settings/integrations',
    description: 'Configure cloud credentials, LLM providers, and portfolio endpoints.'
  }
];

export default function SettingsPage() {
  const { user } = useAuth();
  const router = useRouter();

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader title="Settings" subtitle={user ? `Managing ${user.email}` : 'Account configuration'} />
      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="grid gap-4 md:grid-cols-2">
          {QUICK_LINKS.map((link) => (
            <button
              type="button"
              key={link.href}
              onClick={() => router.push(link.href)}
              className="rounded-xl border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6 text-left shadow transition hover:-translate-y-1 hover:border-dark-primary"
            >
              <p className="text-lg font-semibold text-dark-onSurface">{link.label}</p>
              <p className="mt-2 text-sm text-dark-onSurfaceVariant">{link.description}</p>
            </button>
          ))}
        </div>
        <div className="mt-10 space-y-4">
          <h2 className="text-lg font-semibold text-dark-onSurface">API access</h2>
          <p className="text-sm text-dark-onSurfaceVariant">
            SDK tokens and service accounts will appear here once the shared Byteport SDKs (Go, Python, TypeScript)
            stabilise. Until then, use the CLI bootstrapper to generate local tokens tied to your WorkOS session.
          </p>
        </div>
      </section>
    </div>
  );
}
