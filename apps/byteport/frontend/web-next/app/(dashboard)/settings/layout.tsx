'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { PageHeader } from '@/components/page-header';
import { Settings, Key, Cloud, CreditCard } from 'lucide-react';

const settingsTabs = [
  {
    name: 'General',
    href: '/settings',
    icon: Settings,
    description: 'Profile, preferences, and theme'
  },
  {
    name: 'API Keys',
    href: '/settings/api-keys',
    icon: Key,
    description: 'Manage your API keys'
  },
  {
    name: 'Providers',
    href: '/settings/providers',
    icon: Cloud,
    description: 'Cloud provider credentials'
  },
  {
    name: 'Billing',
    href: '/settings/billing',
    icon: CreditCard,
    description: 'Plans and usage'
  },
];

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="space-y-6">
      <PageHeader
        heading="Settings"
        description="Manage your account settings and preferences"
      />

      <div className="border-b">
        <nav className="-mb-px flex space-x-8 px-1" aria-label="Settings tabs">
          {settingsTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = pathname === tab.href;

            return (
              <Link
                key={tab.name}
                href={tab.href}
                className={cn(
                  'group inline-flex items-center gap-2 border-b-2 px-1 py-4 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-primary text-foreground'
                    : 'border-transparent text-muted-foreground hover:border-muted-foreground/50 hover:text-foreground'
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.name}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="pb-8">{children}</div>
    </div>
  );
}
