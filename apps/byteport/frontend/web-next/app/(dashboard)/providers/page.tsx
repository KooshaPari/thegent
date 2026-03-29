'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProviderBadge } from '@/components/provider-badge';
import { ProviderConnectDialog } from '@/components/provider-connect-dialog';
import { getProviders, testProviderConnection } from '@/lib/api';
import type { Provider } from '@/lib/types';
import {
  Plus,
  Settings,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Server
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

export default function ProvidersPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [testingProvider, setTestingProvider] = useState<string | null>(null);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setLoading(true);
      const data = await getProviders();
      setProviders(data);
    } catch (error) {
      console.error('Failed to load providers:', error);
      toast.error('Failed to load providers');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (providerName: string) => {
    try {
      setTestingProvider(providerName);
      const result = await testProviderConnection(providerName);
      if (result.connected) {
        toast.success(`${providerName} connection successful`);
      } else {
        toast.error(result.message || 'Connection test failed');
      }
    } catch (_error) {
      toast.error('Failed to test connection');
    } finally {
      setTestingProvider(null);
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

  const getStatusBadge = (status: Provider['status']) => {
    const variants = {
      connected: 'bg-green-500/10 text-green-500',
      disconnected: 'bg-gray-500/10 text-gray-500',
      error: 'bg-red-500/10 text-red-500',
      pending: 'bg-yellow-500/10 text-yellow-500'
    };
    return <Badge className={variants[status]}>{status}</Badge>;
  };

  const connectedProviders = providers.filter(p => p.status === 'connected');
  const disconnectedProviders = providers.filter(p => p.status !== 'connected');

  if (loading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader
          title="Providers"
          subtitle="Loading providers..."
        />
        <section className="flex-1 overflow-y-auto px-6 py-8">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </Card>
            ))}
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <DashboardHeader
        title="Providers"
        subtitle={`${connectedProviders.length} connected, ${disconnectedProviders.length} available`}
        action={
          <Button onClick={() => setConnectDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Connect Provider
          </Button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        {connectedProviders.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="rounded-full bg-muted p-6 mb-4">
              <Server className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No providers connected</h3>
            <p className="text-muted-foreground mb-6 text-center max-w-md">
              Connect a cloud provider to start deploying your applications.
            </p>
            <Button onClick={() => setConnectDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Connect Provider
            </Button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Connected Providers */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Connected Providers
              </h3>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {connectedProviders.map((provider) => (
                  <Card
                    key={provider.name}
                    className="group cursor-pointer transition-all hover:border-primary hover:shadow-lg"
                    onClick={() => router.push(`/providers/${provider.name}`)}
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <ProviderBadge provider={provider.name} size="lg" />
                          {getStatusIcon(provider.status)}
                        </div>
                        {getStatusBadge(provider.status)}
                      </div>

                      {provider.metadata?.organization && (
                        <p className="text-sm text-muted-foreground mb-3">
                          {provider.metadata.organization}
                        </p>
                      )}

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Tier</span>
                          <Badge variant="outline" className="capitalize">
                            {provider.pricing_tier || 'free'}
                          </Badge>
                        </div>
                        {provider.metadata?.last_sync && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Last sync</span>
                            <span className="text-xs">
                              {formatDistanceToNow(new Date(provider.metadata.last_sync), { addSuffix: true })}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-2 pt-4 border-t">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleTestConnection(provider.name);
                          }}
                          disabled={testingProvider === provider.name}
                        >
                          {testingProvider === provider.name ? 'Testing...' : 'Test Connection'}
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/providers/${provider.name}`);
                          }}
                        >
                          <Settings className="h-4 w-4 mr-1" />
                          Manage
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            {/* Available Providers */}
            {disconnectedProviders.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 text-muted-foreground">
                  Available Providers
                </h3>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {disconnectedProviders.map((provider) => (
                    <Card
                      key={provider.name}
                      className="p-4 cursor-pointer transition-all hover:border-primary"
                      onClick={() => router.push(`/providers/${provider.name}`)}
                    >
                      <div className="flex items-center justify-between">
                        <ProviderBadge provider={provider.name} size="sm" />
                        {getStatusBadge(provider.status)}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      <ProviderConnectDialog
        open={connectDialogOpen}
        onOpenChange={setConnectDialogOpen}
        onSuccess={loadProviders}
      />
    </div>
  );
}
