'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/auth-context';
import { DashboardHeader } from '@/components/layout/Header';
import { getStats, listDeployments } from '@/lib/api';
import type { Stats, Deployment } from '@/lib/types';
import {
  Server,
  Activity,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
  Eye,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowRight
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';

export default function DashboardPage() {
  const router = useRouter();
  const { status, user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentDeployments, setRecentDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, deploymentsData] = await Promise.all([
        getStats(),
        listDeployments()
      ]);
      setStats(statsData);
      setRecentDeployments(deploymentsData.deployments.slice(0, 5));
    } catch (err) {
      console.error('Failed to load dashboard data', err);
      setError('Unable to load dashboard data');
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
    void loadDashboardData();
  }, [status, router, loadDashboardData]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'building':
      case 'deploying':
        return <Clock className="h-4 w-4 text-yellow-500 animate-pulse" />;
      default:
        return <Clock className="h-4 w-4 text-dark-secondary" />;
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'running':
        return 'default';
      case 'failed':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  if (status === 'pending' || loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-dark-primary border-t-transparent mx-auto" />
          <p className="text-dark-onSurfaceVariant">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto mb-4 h-12 w-12 text-red-500" />
          <h1 className="mb-2 text-xl font-semibold text-dark-onSurface">{error}</h1>
          <button
            onClick={loadDashboardData}
            className="mt-4 rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-white hover:bg-dark-primary/90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const greeting = user?.name?.split(' ')[0] || 'there';

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title={`Welcome back, ${greeting}`}
        subtitle={user?.email || ''}
        action={
          <Link
            href="/deploy"
            className="inline-flex items-center gap-2 rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-white hover:bg-dark-primary/90"
          >
            <Plus className="h-4 w-4" />
            New Deployment
          </Link>
        }
      />

      <div className="flex-1 overflow-y-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Total Deployments */}
          <Card className="border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-dark-secondary">Total Deployments</p>
                <p className="mt-2 text-3xl font-bold text-dark-onSurface">
                  {stats?.total_deployments || 0}
                </p>
              </div>
              <div className="rounded-lg bg-dark-primary/10 p-3">
                <Server className="h-6 w-6 text-dark-primary" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1 text-xs">
              <span className="text-green-500">{stats?.active_deployments || 0} active</span>
            </div>
          </Card>

          {/* Active Deployments */}
          <Card className="border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-dark-secondary">Active</p>
                <p className="mt-2 text-3xl font-bold text-dark-onSurface">
                  {stats?.active_deployments || 0}
                </p>
              </div>
              <div className="rounded-lg bg-green-500/10 p-3">
                <Activity className="h-6 w-6 text-green-500" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1 text-xs text-dark-secondary">
              <span>Running smoothly</span>
            </div>
          </Card>

          {/* Uptime */}
          <Card className="border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-dark-secondary">Uptime</p>
                <p className="mt-2 text-3xl font-bold text-dark-onSurface">
                  {stats?.uptime_percentage?.toFixed(1) || '99.9'}%
                </p>
              </div>
              <div className="rounded-lg bg-blue-500/10 p-3">
                <CheckCircle className="h-6 w-6 text-blue-500" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1 text-xs text-dark-secondary">
              <span>Last 30 days</span>
            </div>
          </Card>

          {/* Total Cost */}
          <Card className="border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-dark-secondary">Monthly Cost</p>
                <p className="mt-2 text-3xl font-bold text-dark-onSurface">
                  ${stats?.total_cost?.toFixed(2) || '0.00'}
                </p>
              </div>
              <div className="rounded-lg bg-purple-500/10 p-3">
                {stats?.cost_trend === 'up' ? (
                  <TrendingUp className="h-6 w-6 text-purple-500" />
                ) : stats?.cost_trend === 'down' ? (
                  <TrendingDown className="h-6 w-6 text-green-500" />
                ) : (
                  <Minus className="h-6 w-6 text-dark-secondary" />
                )}
              </div>
            </div>
            <div className="mt-4 flex items-center gap-1 text-xs text-dark-secondary">
              <span>
                {stats?.cost_trend === 'up'
                  ? 'Increased from last month'
                  : stats?.cost_trend === 'down'
                    ? 'Decreased from last month'
                    : 'Stable'}
              </span>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h3 className="mb-4 text-lg font-semibold text-dark-onSurface">Quick Actions</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button
              onClick={() => router.push('/deploy')}
              className="group flex items-center gap-3 rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-left transition hover:border-dark-primary hover:bg-dark-surfaceContainerHighest"
            >
              <div className="rounded-lg bg-dark-primary/10 p-2">
                <Plus className="h-5 w-5 text-dark-primary" />
              </div>
              <div>
                <p className="font-medium text-dark-onSurface">New Deployment</p>
                <p className="text-xs text-dark-secondary">Deploy your app</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/deployments')}
              className="group flex items-center gap-3 rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-left transition hover:border-dark-primary hover:bg-dark-surfaceContainerHighest"
            >
              <div className="rounded-lg bg-blue-500/10 p-2">
                <Eye className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="font-medium text-dark-onSurface">View All</p>
                <p className="text-xs text-dark-secondary">See deployments</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/monitoring')}
              className="group flex items-center gap-3 rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-left transition hover:border-dark-primary hover:bg-dark-surfaceContainerHighest"
            >
              <div className="rounded-lg bg-green-500/10 p-2">
                <Activity className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <p className="font-medium text-dark-onSurface">Monitor</p>
                <p className="text-xs text-dark-secondary">Check metrics</p>
              </div>
            </button>

            <button
              onClick={() => router.push('/settings/integrations')}
              className="group flex items-center gap-3 rounded-lg border border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 text-left transition hover:border-dark-primary hover:bg-dark-surfaceContainerHighest"
            >
              <div className="rounded-lg bg-purple-500/10 p-2">
                <Server className="h-5 w-5 text-purple-500" />
              </div>
              <div>
                <p className="font-medium text-dark-onSurface">Integrations</p>
                <p className="text-xs text-dark-secondary">Connect providers</p>
              </div>
            </button>
          </div>
        </div>

        {/* Recent Deployments */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-dark-onSurface">Recent Deployments</h3>
            <Link
              href="/deployments"
              className="flex items-center gap-1 text-sm font-medium text-dark-primary hover:underline"
            >
              View all
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {recentDeployments.length === 0 ? (
            <Card className="border-dashed border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-12 text-center">
              <Server className="mx-auto mb-4 h-12 w-12 text-dark-secondary" />
              <p className="mb-2 font-medium text-dark-onSurface">No deployments yet</p>
              <p className="mb-4 text-sm text-dark-secondary">
                Get started by deploying your first application
              </p>
              <button
                onClick={() => router.push('/deploy')}
                className="inline-flex items-center gap-2 rounded-lg bg-dark-primary px-4 py-2 text-sm font-medium text-white hover:bg-dark-primary/90"
              >
                <Plus className="h-4 w-4" />
                Deploy Now
              </button>
            </Card>
          ) : (
            <div className="space-y-3">
              {recentDeployments.map((deployment) => (
                <Card
                  key={deployment.id}
                  className="border-dark-surfaceVariant bg-dark-surfaceContainerHigh p-4 transition hover:border-dark-primary"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="rounded-lg bg-dark-surfaceContainerHighest p-2">
                        {getStatusIcon(deployment.status)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-dark-onSurface">{deployment.name}</h4>
                          <Badge variant={getStatusBadgeVariant(deployment.status)}>
                            {deployment.status}
                          </Badge>
                        </div>
                        <p className="mt-1 text-sm text-dark-secondary">
                          {deployment.provider} • {deployment.type} •{' '}
                          {formatDistanceToNow(new Date(deployment.created_at), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link
                        href={`/deployments/${deployment.id}`}
                        className="rounded-lg border border-dark-surfaceVariant px-3 py-1.5 text-sm font-medium text-dark-onSurface transition hover:bg-dark-surfaceContainerHighest"
                      >
                        View
                      </Link>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
