'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  getDeployment,
  getDeploymentStatus,
  getDeploymentLogs,
  terminateDeployment,
  restartDeployment,
  streamDeploymentStatus,
} from '@/lib/api';
import type { Deployment, DeploymentStatusUpdate, LogEntry } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { StatusBadge } from '@/components/status-badge';
import { ServiceCard } from '@/components/service-card';
import {
  ChevronLeft,
  RefreshCw,
  ExternalLink,
  Copy,
  Check,
  AlertCircle,
  Activity,
  Server,
  Calendar,
  GitBranch,
  Terminal,
  BarChart3,
  Settings,
  PlayCircle,
  StopCircle,
  Trash2,
  Loader2,
  Package,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function DeploymentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const id = params.id as string;

  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [status, setStatus] = useState<DeploymentStatusUpdate | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'overview');
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Mock services data - in real app this would come from API
  const [services] = useState([
    {
      id: '1',
      name: 'Web Server',
      status: 'online' as const,
      type: 'nginx',
      cpu_usage: 45,
      memory_usage: 62,
      disk_usage: 38,
      uptime: '5d 12h',
      requests_per_minute: 1250,
    },
    {
      id: '2',
      name: 'Application',
      status: 'online' as const,
      type: deployment?.runtime || 'node',
      cpu_usage: 72,
      memory_usage: 81,
      disk_usage: 25,
      uptime: '5d 12h',
    },
  ]);

  useEffect(() => {
    loadDeploymentData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    // Set up real-time status updates via SSE
    const eventSource = streamDeploymentStatus(
      id,
      (statusUpdate) => {
        setStatus(statusUpdate);
        // Update deployment status as well
        if (deployment) {
          setDeployment({ ...deployment, status: statusUpdate.status });
        }
      },
      (error) => {
        console.error('SSE error:', error);
      }
    );

    return () => {
      eventSource.close();
    };
  }, [id, deployment]);

  const loadDeploymentData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [deploymentData, statusData] = await Promise.all([
        getDeployment(id),
        getDeploymentStatus(id),
      ]);

      setDeployment(deploymentData);
      setStatus(statusData);
    } catch (err: any) {
      setError(err.message || 'Failed to load deployment');
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = useCallback(async () => {
    try {
      const logsData = await getDeploymentLogs(id);
      setLogs(logsData.logs || []);
    } catch (err) {
      console.error('Failed to load logs:', err);
    }
  }, [id]);

  useEffect(() => {
    if (activeTab === 'logs') {
      loadLogs();
      const interval = setInterval(loadLogs, 5000);
      return () => clearInterval(interval);
    }
  }, [activeTab, loadLogs]);

  const handleRestart = async () => {
    try {
      setActionLoading('restart');
      await restartDeployment(id);
      toast.success('Deployment restarting...');
      await loadDeploymentData();
    } catch (err: any) {
      toast.error(`Failed to restart: ${err.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleTerminate = async () => {
    if (!confirm('Are you sure you want to terminate this deployment? This action cannot be undone.')) {
      return;
    }

    try {
      setActionLoading('terminate');
      await terminateDeployment(id);
      toast.success('Deployment terminated');
      router.push('/deployments');
    } catch (_err) {
      toast.error(`Failed to terminate`);
      setActionLoading(null);
    }
  };

  const handleCopyUrl = async () => {
    if (deployment?.url) {
      try {
        await navigator.clipboard.writeText(deployment.url);
        setCopiedUrl(true);
        toast.success('URL copied to clipboard');
        setTimeout(() => setCopiedUrl(false), 2000);
      } catch (_err) {
        toast.error('Failed to copy URL');
      }
    }
  };

  const getLogColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
      case 'fatal':
        return 'text-red-400';
      case 'warn':
        return 'text-yellow-400';
      case 'info':
        return 'text-blue-400';
      case 'debug':
        return 'text-gray-500';
      default:
        return 'text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
            <span className="text-gray-600">Loading deployment...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !deployment) {
    return (
      <div className="container mx-auto p-8">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-900">Error loading deployment</p>
                <p className="text-sm text-red-700 mt-1">{error || 'Deployment not found'}</p>
                <div className="flex gap-2 mt-4">
                  <Link href="/deployments">
                    <Button variant="outline" size="sm">
                      Back to Deployments
                    </Button>
                  </Link>
                  <Button onClick={loadDeploymentData} variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </Button>
                </div>
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
      <div>
        <Link
          href="/deployments"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center gap-1 mb-4"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Deployments
        </Link>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-4xl font-bold mb-2">{deployment.name}</h1>
            <div className="flex items-center gap-3 text-sm text-gray-600 flex-wrap">
              <span className="flex items-center gap-1">
                <Server className="w-4 h-4" />
                ID: {deployment.id}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                Created: {new Date(deployment.created_at).toLocaleString()}
              </span>
              {deployment.git_url && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <GitBranch className="w-4 h-4" />
                    {deployment.branch || 'main'}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleRestart}
              disabled={actionLoading !== null || deployment.status === 'terminated'}
              variant="outline"
            >
              {actionLoading === 'restart' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <PlayCircle className="w-4 h-4" />
              )}
              <span className="ml-2">Restart</span>
            </Button>
            <Button
              onClick={handleTerminate}
              disabled={actionLoading !== null || deployment.status === 'terminated'}
              variant="destructive"
            >
              {actionLoading === 'terminate' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <StopCircle className="w-4 h-4" />
              )}
              <span className="ml-2">Terminate</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Status Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Deployment Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <div className="text-sm text-gray-600 mb-2">Current State</div>
              <StatusBadge status={deployment.status} size="md" />
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-2">Progress</div>
              <div className="flex items-center gap-3">
                <Progress value={status?.progress || 0} className="flex-1" />
                <span className="text-sm font-medium">{status?.progress || 0}%</span>
              </div>
              {status?.message && (
                <p className="text-xs text-gray-600 mt-1">{status.message}</p>
              )}
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-2">Provider</div>
              <div className="font-medium capitalize">{deployment.provider}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-2">Type</div>
              <div className="font-medium capitalize">{deployment.type}</div>
            </div>
          </div>

          {deployment.url && (
            <div className="mt-6 pt-6 border-t">
              <div className="text-sm text-gray-600 mb-2">Application URL</div>
              <div className="flex items-center gap-2">
                <a
                  href={deployment.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2 flex-1 truncate"
                >
                  {deployment.url}
                  <ExternalLink className="w-4 h-4 flex-shrink-0" />
                </a>
                <Button onClick={handleCopyUrl} variant="outline" size="sm">
                  {copiedUrl ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          )}

          {deployment.error_message && (
            <div className="mt-6 pt-6 border-t">
              <div className="flex items-start gap-2 text-red-600">
                <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-medium mb-1">Error Details</div>
                  <div className="text-sm">{deployment.error_message}</div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <CardHeader className="pb-0">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <Server className="w-4 h-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="logs" className="flex items-center gap-2">
                <Terminal className="w-4 h-4" />
                Logs
              </TabsTrigger>
              <TabsTrigger value="metrics" className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Metrics
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Settings
              </TabsTrigger>
            </TabsList>
          </CardHeader>

          <CardContent className="pt-6">
            <TabsContent value="overview" className="space-y-6 mt-0">
              {/* Services */}
              {deployment.status === 'running' && services.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Package className="w-5 h-5" />
                    Running Services
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {services.map((service) => (
                      <ServiceCard
                        key={service.id}
                        service={service}
                        onView={(id) => console.log('View service:', id)}
                      />
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-lg font-semibold mb-4">Deployment Configuration</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {deployment.runtime && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-sm text-gray-600 mb-1">Runtime</div>
                      <div className="font-medium">{deployment.runtime}</div>
                    </div>
                  )}
                  {deployment.framework && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-sm text-gray-600 mb-1">Framework</div>
                      <div className="font-medium">{deployment.framework}</div>
                    </div>
                  )}
                  {deployment.git_url && (
                    <div className="bg-gray-50 rounded-lg p-4 md:col-span-2">
                      <div className="text-sm text-gray-600 mb-1">Git Repository</div>
                      <a
                        href={deployment.git_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1 break-all"
                      >
                        {deployment.git_url}
                        <ExternalLink className="w-3 h-3 flex-shrink-0" />
                      </a>
                    </div>
                  )}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Created At</div>
                    <div className="font-medium">
                      {new Date(deployment.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="text-sm text-gray-600 mb-1">Last Updated</div>
                    <div className="font-medium">
                      {new Date(deployment.updated_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>

              {deployment.env_vars && Object.keys(deployment.env_vars).length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Environment Variables</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="space-y-2">
                      {Object.entries(deployment.env_vars).map(([key, value]) => {
                        const stringValue = String(value ?? '');
                        const displayValue =
                          stringValue.length > 50
                            ? `${stringValue.substring(0, 50)}...`
                            : stringValue;

                        return (
                          <div key={key} className="flex items-center gap-2 text-sm font-mono">
                            <span className="font-semibold text-gray-700">{key}</span>
                            <span className="text-gray-400">=</span>
                            <span className="text-gray-600">{displayValue}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="logs" className="mt-0">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Deployment Logs</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={loadLogs}>
                    <RefreshCw className="w-4 h-4" />
                  </Button>
                  <Link href={`/deployments/${id}/logs`}>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Full Logs
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto max-h-[500px] overflow-y-auto">
                {logs.length === 0 ? (
                  <div className="text-gray-400 text-center py-8">No logs available</div>
                ) : (
                  <div className="space-y-1">
                    {logs.slice(-50).map((log, idx) => (
                      <div key={idx} className="text-gray-300">
                        <span className="text-gray-500">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>{' '}
                        <span className={getLogColor(log.level)}>[{log.level.toUpperCase()}]</span>{' '}
                        {log.message}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="metrics" className="mt-0">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Performance Metrics</h3>
                <Link href={`/deployments/${id}/metrics`}>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                </Link>
              </div>
              <div className="text-center py-12 text-gray-600">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p>Detailed metrics are available on the metrics page</p>
                <Link href={`/deployments/${id}/metrics`}>
                  <Button variant="outline" size="sm" className="mt-4">
                    View Metrics
                  </Button>
                </Link>
              </div>
            </TabsContent>

            <TabsContent value="settings" className="mt-0">
              <h3 className="text-lg font-semibold mb-4">Deployment Settings</h3>
              <div className="space-y-4">
                <Card className="border-red-200">
                  <CardHeader>
                    <CardTitle className="text-red-600 flex items-center gap-2">
                      <Trash2 className="w-5 h-5" />
                      Danger Zone
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Terminate Deployment</p>
                        <p className="text-sm text-gray-600">
                          Permanently delete this deployment and all associated data
                        </p>
                      </div>
                      <Button
                        onClick={handleTerminate}
                        disabled={actionLoading !== null || deployment.status === 'terminated'}
                        variant="destructive"
                      >
                        {actionLoading === 'terminate' ? (
                          <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        ) : (
                          <Trash2 className="w-4 h-4 mr-2" />
                        )}
                        Terminate
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </CardContent>
        </Tabs>
      </Card>
    </div>
  );
}
