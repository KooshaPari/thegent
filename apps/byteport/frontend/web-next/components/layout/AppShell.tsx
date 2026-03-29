'use client';

import { Sidebar } from '../sidebar';
import { Breadcrumbs } from './Breadcrumbs';
import { UserNav } from '@/components/user-nav';
import { usePathname } from 'next/navigation';
import { Menu, Search, Bell } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const showHeader = pathname !== '/';

  return (
    <div className="flex min-h-screen bg-dark-surface text-dark-onSurface">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform md:relative md:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header with Breadcrumbs and User Menu */}
        {showHeader && (
          <header className="sticky top-0 z-30 border-b border-dark-surfaceVariant bg-dark-surfaceContainer/95 backdrop-blur supports-[backdrop-filter]:bg-dark-surfaceContainer/60">
            <div className="flex h-16 items-center gap-4 px-4 md:px-6">
              <button
                onClick={() => setSidebarOpen(true)}
                className="text-dark-onSurfaceVariant md:hidden"
                aria-label="Open sidebar"
              >
                <Menu className="h-6 w-6" />
              </button>

              <div className="flex-1">
                <Breadcrumbs />
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  className="relative text-dark-onSurfaceVariant hover:text-dark-onSurface"
                  onClick={() => {
                    const event = new KeyboardEvent('keydown', {
                      key: 'k',
                      metaKey: true,
                      bubbles: true
                    });
                    document.dispatchEvent(event);
                  }}
                >
                  <Search className="h-5 w-5" />
                  <span className="sr-only">Search</span>
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  className="relative text-dark-onSurfaceVariant hover:text-dark-onSurface"
                >
                  <Bell className="h-5 w-5" />
                  <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-dark-primary" />
                  <span className="sr-only">Notifications</span>
                </Button>

                <UserNav />
              </div>
            </div>
          </header>
        )}

        {/* Page Content */}
        <div className="flex-1 overflow-auto">{children}</div>
      </div>
    </div>
  );
}
