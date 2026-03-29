'use client';

import { useEffect } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { CommandPalette, useCommandPalette } from '@/components/command-palette';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { open, setOpen } = useCommandPalette();

  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      if (event.key === 'k' && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setOpen((current) => !current);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [setOpen]);

  return (
    <>
      <AppShell>{children}</AppShell>
      <CommandPalette open={open} onOpenChange={setOpen} />
    </>
  );
}
