'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProviderBadge } from '@/components/provider-badge';
import { getHost, deleteHost, getHostMetrics } from '@/lib/api';
import type { Host, Metrics } from '@/lib/types';
import {
  ArrowLeft,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Wrench,
  Server,
  Activity,
  Cpu,
  HardDrive,
  Network,
  MapPin,
  Clock,
  RefreshCw,
  Settings
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export default function HostDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const hostId = params.id as string;

  const [host, setHost] = useState<Host | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadHostData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hostId]);

  const loadHostData = async () => {
    try {
      setLoading(true);
      const [hostData, metricsData] = await Promise.all([
        getHost(hostId),
        getHostMetrics(hostId).catch(() => null)
      ]);
      setHost(hostData);
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to load host:', error);
      toast.error('Failed to load host details');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await deleteHost(hostId);
      toast.success('Host deleted successfully');
      router.push('/hosts');
    } catch (_error) {
      toast.error('Failed to delete host');
      setDeleting(false);
    }
  };

  const getStatusIcon = (status: Host['status']) => {
    switch (status) {
      case 'online':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'offline':
        return <XCircle className="h-5 w-5 text-gray-400" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'maintenance':
        return <Wrench className="h-5 w-5 text-blue-500" />;
      default:
        return null;
    }
  };

  const formatBytes = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(1)} GB`;
    }
    return `${mb} MB`;
  };

  const calculateAverage = (dataPoints: { value: number }[]) => {
    if (!dataPoints || dataPoints.length === 0) return 0;
    const sum = dataPoints.reduce((acc, point) => acc + point.value, 0);
    return (sum / dataPoints.length).toFixed(2);
  };

  if (loading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader title="Loading..." subtitle="Please wait" />
        <section className="flex-1 overflow-y-auto px-6 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </section>
      </div>
    );
  }

  if (!host) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader title="Host Not Found" />
        <section className="flex-1 overflow-y-auto px-6 py-8">
          <div className="flex flex-col items-center justify-center py-16">
            <Server className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">Host not found</h3>
            <p className="text-muted-foreground mb-6">The requested host could not be found.</p>
            <Button onClick={() => router.push('/hosts')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Hosts
            </Button>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title={host.name}
        subtitle={host.hostname}
        action={
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push('/hosts')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <Button
              variant="destructive"
              onClick={() => setDeleteDialogOpen(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(host.status)}
                  <div>
                    <CardTitle>Host Status</CardTitle>
                    <CardDescription className="capitalize">{host.status}</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <ProviderBadge provider={host.provider} size="md" />
                  <Button variant="outline" size="sm" onClick={loadHostData}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Region</p>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3 text-muted-foreground" />
                    <p className="text-sm font-medium">{host.region}</p>
                  </div>
                </div>
                {host.ip_address && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">IP Address</p>
                    <p className="text-sm font-mono">{host.ip_address}</p>
                  </div>
                )}
                {host.os && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Operating System</p>
                    <p className="text-sm">{host.os}</p>
                  </div>
                )}
                {host.last_seen && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Last Seen</p>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <p className="text-sm">
                        {formatDistanceToNow(new Date(host.last_seen), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="resources">Resources</TabsTrigger>
              <TabsTrigger value="metrics">Metrics</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">CPU Cores</CardTitle>
                    <Cpu className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{host.cpu_cores || 'N/A'}</div>
                    <p className="text-xs text-muted-foreground">
                      {metrics?.cpu_usage ? `${calculateAverage(metrics.cpu_usage)}% avg` : 'No data'}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Memory</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {host.memory_mb ? formatBytes(host.memory_mb) : 'N/A'}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {metrics?.memory_usage ? `${calculateAverage(metrics.memory_usage)}% avg` : 'No data'}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Disk Space</CardTitle>
                    <HardDrive className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {host.disk_gb ? `${host.disk_gb} GB` : 'N/A'}
                    </div>
                    <p className="text-xs text-muted-foreground">Total capacity</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Network</CardTitle>
                    <Network className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {host.status === 'online' ? 'Active' : 'Inactive'}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {host.ip_address || 'No IP assigned'}
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Host Information</CardTitle>
                  <CardDescription>Details about this host</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-sm font-medium mb-2">Provider</p>
                      <ProviderBadge provider={host.provider} size="md" />
                    </div>
                    <div>
                      <p className="text-sm font-medium mb-2">Created</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDistanceToNow(new Date(host.created_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>

                  {host.tags && host.tags.length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Tags</p>
                      <div className="flex flex-wrap gap-2">
                        {host.tags.map((tag) => (
                          <Badge key={tag} variant="outline">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="resources" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Resource Allocation</CardTitle>
                  <CardDescription>Hardware resources assigned to this host</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">CPU Cores</span>
                      <span className="text-sm text-muted-foreground">
                        {host.cpu_cores || 'Not specified'}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Memory</span>
                      <span className="text-sm text-muted-foreground">
                        {host.memory_mb ? formatBytes(host.memory_mb) : 'Not specified'}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Disk Space</span>
                      <span className="text-sm text-muted-foreground">
                        {host.disk_gb ? `${host.disk_gb} GB` : 'Not specified'}
                      </span>
                    </div>
                  </div>

                  {host.os && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Operating System</span>
                        <span className="text-sm text-muted-foreground">{host.os}</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="metrics" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Performance Metrics</CardTitle>
                  <CardDescription>Real-time and historical performance data</CardDescription>
                </CardHeader>
                <CardContent>
                  {metrics ? (
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium mb-2">CPU Usage</p>
                        <p className="text-2xl font-bold">
                          {calculateAverage(metrics.cpu_usage)}%
                        </p>
                        <p className="text-xs text-muted-foreground">Average usage</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium mb-2">Memory Usage</p>
                        <p className="text-2xl font-bold">
                          {calculateAverage(metrics.memory_usage)}%
                        </p>
                        <p className="text-xs text-muted-foreground">Average usage</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      No metrics data available for this host
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Host Configuration</CardTitle>
                  <CardDescription>Manage host settings and configuration</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between py-2 border-b">
                    <div>
                      <p className="font-medium">Hostname</p>
                      <p className="text-sm text-muted-foreground font-mono">{host.hostname}</p>
                    </div>
                  </div>

                  {host.ip_address && (
                    <div className="flex items-center justify-between py-2 border-b">
                      <div>
                        <p className="font-medium">IP Address</p>
                        <p className="text-sm text-muted-foreground font-mono">{host.ip_address}</p>
                      </div>
                    </div>
                  )}

                  <div className="pt-4">
                    <Button variant="outline" className="w-full" disabled>
                      <Settings className="h-4 w-4 mr-2" />
                      Update Configuration
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="text-destructive">Danger Zone</CardTitle>
                  <CardDescription>Irreversible actions for this host</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="destructive"
                    onClick={() => setDeleteDialogOpen(true)}
                    className="w-full"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Host
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete {host.name}?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this host from your account. This action cannot be undone.
              Any deployments running on this host may be affected.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleting ? 'Deleting...' : 'Delete Host'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
