'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProviderBadge } from '@/components/provider-badge';
import { UsageBar } from '@/components/usage-bar';
import { getProvider, disconnectProvider, getProviderStats } from '@/lib/api';
import type { Provider } from '@/lib/types';
import {
  ArrowLeft,
  Settings,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Server,
  Activity,
  DollarSign,
  Globe,
  Shield,
  RefreshCw
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

export default function ProviderDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const providerName = params.provider as string;

  const [provider, setProvider] = useState<Provider | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [disconnectDialogOpen, setDisconnectDialogOpen] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);

  useEffect(() => {
    loadProviderData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [providerName]);

  const loadProviderData = async () => {
    try {
      setLoading(true);
      const [providerData, statsData] = await Promise.all([
        getProvider(providerName),
        getProviderStats(providerName).catch(() => null)
      ]);
      setProvider(providerData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load provider:', error);
      toast.error('Failed to load provider details');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      setDisconnecting(true);
      await disconnectProvider(providerName);
      toast.success('Provider disconnected successfully');
      router.push('/providers');
    } catch (_error) {
      toast.error('Failed to disconnect provider');
      setDisconnecting(false);
    }
  };

  const getStatusIcon = (status: Provider['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'disconnected':
        return <XCircle className="h-5 w-5 text-gray-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return null;
    }
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

  if (!provider) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader title="Provider Not Found" />
        <section className="flex-1 overflow-y-auto px-6 py-8">
          <div className="flex flex-col items-center justify-center py-16">
            <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">Provider not found</h3>
            <p className="text-muted-foreground mb-6">The requested provider could not be found.</p>
            <Button onClick={() => router.push('/providers')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Providers
            </Button>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title={provider.display_name}
        subtitle={`Provider: ${provider.name}`}
        action={
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push('/providers')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            {provider.status === 'connected' && (
              <Button
                variant="destructive"
                onClick={() => setDisconnectDialogOpen(true)}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Disconnect
              </Button>
            )}
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
                  <ProviderBadge provider={provider.name} size="lg" />
                  {getStatusIcon(provider.status)}
                  <div>
                    <CardTitle>Connection Status</CardTitle>
                    <CardDescription className="capitalize">{provider.status}</CardDescription>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={loadProviderData}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Tier</p>
                  <Badge variant="outline" className="capitalize">
                    {provider.pricing_tier || 'free'}
                  </Badge>
                </div>
                {provider.metadata?.organization && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Organization</p>
                    <p className="text-sm font-medium">{provider.metadata.organization}</p>
                  </div>
                )}
                {provider.metadata?.account_id && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Account ID</p>
                    <p className="text-sm font-mono">{provider.metadata.account_id}</p>
                  </div>
                )}
                {provider.metadata?.last_sync && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Last Synced</p>
                    <p className="text-sm">
                      {formatDistanceToNow(new Date(provider.metadata.last_sync), { addSuffix: true })}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="usage">Usage</TabsTrigger>
              <TabsTrigger value="regions">Regions</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Deployments</CardTitle>
                    <Server className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats?.total_deployments || 0}</div>
                    <p className="text-xs text-muted-foreground">
                      {stats?.active_deployments || 0} active
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      ${(stats?.total_cost || 0).toFixed(2)}
                    </div>
                    <p className="text-xs text-muted-foreground">This month</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                    <Activity className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {stats?.avg_response_time || 0}ms
                    </div>
                    <p className="text-xs text-muted-foreground">Last 24 hours</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Status</CardTitle>
                    <Shield className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold capitalize">{provider.status}</div>
                    <p className="text-xs text-muted-foreground">
                      {provider.is_configured ? 'Configured' : 'Not configured'}
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Capabilities</CardTitle>
                  <CardDescription>Features supported by this provider</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {provider.capabilities.map((capability) => (
                      <Badge key={capability} variant="outline">
                        {capability}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="usage" className="space-y-4">
              {provider.pricing_tier === 'free' && (
                <div className="grid gap-4 md:grid-cols-2">
                  <UsageBar
                    title="Deployments"
                    description="Free tier monthly limit"
                    current={stats?.total_deployments || 0}
                    limit={100}
                    unit="deployments"
                  />
                  <UsageBar
                    title="Build Minutes"
                    description="Free tier monthly limit"
                    current={42}
                    limit={100}
                    unit="minutes"
                  />
                  <UsageBar
                    title="Bandwidth"
                    description="Free tier monthly limit"
                    current={2.3}
                    limit={100}
                    unit="GB"
                  />
                  <UsageBar
                    title="Edge Requests"
                    description="Free tier monthly limit"
                    current={15420}
                    limit={100000}
                    unit="requests"
                  />
                </div>
              )}
              {provider.pricing_tier !== 'free' && (
                <Card>
                  <CardHeader>
                    <CardTitle>Usage Statistics</CardTitle>
                    <CardDescription>
                      Detailed usage statistics for {provider.pricing_tier} tier
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Usage tracking is available for paid tiers
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="regions" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Available Regions</CardTitle>
                  <CardDescription>Deployment regions supported by {provider.display_name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-2 md:grid-cols-3">
                    {provider.regions && provider.regions.length > 0 ? (
                      provider.regions.map((region) => (
                        <div key={region} className="flex items-center gap-2 p-2 border rounded">
                          <Globe className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{region}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground col-span-3">
                        Region information not available
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Provider Configuration</CardTitle>
                  <CardDescription>Manage your provider settings and credentials</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between py-2 border-b">
                    <div>
                      <p className="font-medium">Connection Status</p>
                      <p className="text-sm text-muted-foreground">
                        Current status: {provider.status}
                      </p>
                    </div>
                    {getStatusIcon(provider.status)}
                  </div>

                  {provider.metadata?.email && (
                    <div className="flex items-center justify-between py-2 border-b">
                      <div>
                        <p className="font-medium">Account Email</p>
                        <p className="text-sm text-muted-foreground">{provider.metadata.email}</p>
                      </div>
                    </div>
                  )}

                  <div className="pt-4">
                    <Button variant="outline" className="w-full" disabled>
                      <Settings className="h-4 w-4 mr-2" />
                      Update Credentials
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="text-destructive">Danger Zone</CardTitle>
                  <CardDescription>Irreversible actions for this provider</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="destructive"
                    onClick={() => setDisconnectDialogOpen(true)}
                    className="w-full"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Disconnect Provider
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      <AlertDialog open={disconnectDialogOpen} onOpenChange={setDisconnectDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Disconnect {provider.display_name}?</AlertDialogTitle>
            <AlertDialogDescription>
              This will disconnect your {provider.display_name} account. Any existing deployments
              will continue to run, but you won't be able to create new ones until you reconnect.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={disconnecting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDisconnect}
              disabled={disconnecting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {disconnecting ? 'Disconnecting...' : 'Disconnect'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
