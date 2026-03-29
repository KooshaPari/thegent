'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { listDeployments } from '@/lib/api';
import type { Deployment } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DeploymentCard } from '@/components/deployment-card';
import { StatusBadge } from '@/components/status-badge';
import {
  Search,
  Grid3x3,
  List,
  Plus,
  RefreshCw,
  ExternalLink,
  Server,
  AlertCircle,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

type ViewMode = 'grid' | 'list';
type StatusFilter = 'all' | 'running' | 'deploying' | 'failed' | 'terminated';
type ProviderFilter = 'all' | string;

export default function DeploymentsPage() {
  const router = useRouter();
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [filteredDeployments, setFilteredDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [providerFilter, setProviderFilter] = useState<ProviderFilter>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<'created_at' | 'name' | 'status'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const itemsPerPage = 12;

  useEffect(() => {
    loadDeployments();
  }, []);

  useEffect(() => {
    applyFilters();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deployments, searchQuery, statusFilter, providerFilter, sortBy, sortOrder]);

  const loadDeployments = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listDeployments();
      setDeployments(data.deployments || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load deployments');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...deployments];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (d) =>
          d.name.toLowerCase().includes(query) ||
          d.id.toLowerCase().includes(query) ||
          d.provider.toLowerCase().includes(query)
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((d) => d.status === statusFilter);
    }

    if (providerFilter !== 'all') {
      filtered = filtered.filter((d) => d.provider === providerFilter);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'created_at') {
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      } else if (sortBy === 'name') {
        comparison = a.name.localeCompare(b.name);
      } else if (sortBy === 'status') {
        comparison = a.status.localeCompare(b.status);
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredDeployments(filtered);
    setCurrentPage(1);
  };

  const getUniqueProviders = () => {
    const providers = new Set(deployments.map((d) => d.provider));
    return Array.from(providers);
  };

  const stats = {
    total: deployments.length,
    running: deployments.filter((d) => d.status === 'running').length,
    deploying: deployments.filter((d) => d.status === 'deploying' || d.status === 'building').length,
    failed: deployments.filter((d) => d.status === 'failed').length,
  };

  const paginatedDeployments = filteredDeployments.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );
  const totalPages = Math.ceil(filteredDeployments.length / itemsPerPage);

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <RefreshCw className="h-8 w-8 text-blue-600 animate-spin" />
            <span className="text-gray-600">Loading deployments...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error loading deployments</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <Button onClick={loadDeployments} variant="outline" size="sm" className="mt-3">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try again
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">Deployments</h1>
          <p className="text-gray-600 mt-1">Manage and monitor all your BytePort deployments</p>
        </div>
        <Link href="/deployments/new">
          <Button size="lg">
            <Plus className="w-5 h-5 mr-2" />
            New Deployment
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Deployments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Running</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{stats.running}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Deploying</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-600">{stats.deploying}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Failed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">{stats.failed}</div>
          </CardContent>
        </Card>
      </div>

      {/* Toolbar */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                type="text"
                placeholder="Search deployments..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filters */}
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
                className="px-4 py-2 border rounded-md bg-white text-sm"
              >
                <option value="all">All Status</option>
                <option value="running">Running</option>
                <option value="deploying">Deploying</option>
                <option value="failed">Failed</option>
                <option value="terminated">Terminated</option>
              </select>

              <select
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                className="px-4 py-2 border rounded-md bg-white text-sm"
              >
                <option value="all">All Providers</option>
                {getUniqueProviders().map((provider) => (
                  <option key={provider} value={provider}>
                    {provider}
                  </option>
                ))}
              </select>

              {/* Sort Dropdown */}
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  setSortBy(field as any);
                  setSortOrder(order as any);
                }}
                className="px-4 py-2 border rounded-md bg-white text-sm"
              >
                <option value="created_at-desc">Newest First</option>
                <option value="created_at-asc">Oldest First</option>
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
                <option value="status-asc">Status (A-Z)</option>
              </select>

              {/* View Mode Toggle */}
              <div className="flex border rounded-md overflow-hidden">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 ${
                    viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600'
                  }`}
                >
                  <Grid3x3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 ${
                    viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

              <Button variant="outline" onClick={loadDeployments}>
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Deployments List/Grid */}
      {filteredDeployments.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Server className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <h2 className="text-2xl font-bold mb-2">
              {deployments.length === 0 ? 'No deployments yet' : 'No deployments found'}
            </h2>
            <p className="text-gray-600 mb-6">
              {deployments.length === 0
                ? 'Get started by deploying your first application'
                : 'Try adjusting your filters or search query'}
            </p>
            {deployments.length === 0 && (
              <Link href="/deployments/new">
                <Button size="lg">
                  <Plus className="w-5 h-5 mr-2" />
                  Deploy Your First App
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {paginatedDeployments.map((deployment) => (
            <DeploymentCard
              key={deployment.id}
              deployment={deployment}
              onView={(id) => router.push(`/deployments/${id}`)}
              onViewLogs={(id) => router.push(`/deployments/${id}?tab=logs`)}
              onSettings={(id) => router.push(`/deployments/${id}?tab=settings`)}
            />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Provider
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      URL
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {paginatedDeployments.map((deployment) => (
                    <tr key={deployment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          href={`/deployments/${deployment.id}`}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          {deployment.name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={deployment.status} size="sm" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{deployment.type}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{deployment.provider}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(deployment.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {deployment.url ? (
                          <a
                            href={deployment.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                          >
                            View
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {(currentPage - 1) * itemsPerPage + 1} to{' '}
            {Math.min(currentPage * itemsPerPage, filteredDeployments.length)} of{' '}
            {filteredDeployments.length} deployments
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(currentPage - 1)}
            >
              Previous
            </Button>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={currentPage === page ? 'default' : 'outline'}
                size="sm"
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </Button>
            ))}
            <Button
              variant="outline"
              size="sm"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(currentPage + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
