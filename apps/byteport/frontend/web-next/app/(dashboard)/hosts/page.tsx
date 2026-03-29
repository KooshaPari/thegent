'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardHeader } from '@/components/layout/Header';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProviderBadge } from '@/components/provider-badge';
import { getHosts } from '@/lib/api';
import type { Host, HostStatus } from '@/lib/types';
import {
  Plus,
  Server,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Wrench,
  Cpu,
  HardDrive,
  Activity,
  MapPin,
  Clock
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

export default function HostsPage() {
  const router = useRouter();
  const [hosts, setHosts] = useState<Host[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHosts();
  }, []);

  const loadHosts = async () => {
    try {
      setLoading(true);
      const data = await getHosts();
      setHosts(data);
    } catch (error) {
      console.error('Failed to load hosts:', error);
      toast.error('Failed to load hosts');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: HostStatus) => {
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

  const getStatusBadge = (status: HostStatus) => {
    const variants = {
      online: 'bg-green-500/10 text-green-500',
      offline: 'bg-gray-500/10 text-gray-500',
      degraded: 'bg-yellow-500/10 text-yellow-500',
      maintenance: 'bg-blue-500/10 text-blue-500'
    };
    return <Badge className={variants[status]}>{status}</Badge>;
  };

  const formatBytes = (mb: number) => {
    if (mb >= 1024) {
      return `${(mb / 1024).toFixed(1)} GB`;
    }
    return `${mb} MB`;
  };

  const onlineHosts = hosts.filter(h => h.status === 'online');
  const offlineHosts = hosts.filter(h => h.status === 'offline');
  const degradedHosts = hosts.filter(h => h.status === 'degraded');
  const maintenanceHosts = hosts.filter(h => h.status === 'maintenance');

  if (loading) {
    return (
      <div className="flex flex-1 flex-col overflow-hidden">
        <DashboardHeader
          title="Hosts"
          subtitle="Loading hosts..."
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
        title="Hosts"
        subtitle={`${hosts.length} ${hosts.length === 1 ? 'host' : 'hosts'} registered`}
        action={
          <Button onClick={() => router.push('/hosts/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Register Host
          </Button>
        }
      />

      <section className="flex-1 overflow-y-auto px-6 py-8">
        {hosts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="rounded-full bg-muted p-6 mb-4">
              <Server className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No hosts registered</h3>
            <p className="text-muted-foreground mb-6 text-center max-w-md">
              Register your first host to start deploying applications to your own infrastructure.
            </p>
            <Button onClick={() => router.push('/hosts/new')}>
              <Plus className="h-4 w-4 mr-2" />
              Register Host
            </Button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Status Summary */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Online</p>
                    <p className="text-2xl font-bold">{onlineHosts.length}</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-500" />
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Degraded</p>
                    <p className="text-2xl font-bold">{degradedHosts.length}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Maintenance</p>
                    <p className="text-2xl font-bold">{maintenanceHosts.length}</p>
                  </div>
                  <Wrench className="h-8 w-8 text-blue-500" />
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Offline</p>
                    <p className="text-2xl font-bold">{offlineHosts.length}</p>
                  </div>
                  <XCircle className="h-8 w-8 text-gray-400" />
                </div>
              </Card>
            </div>

            {/* Hosts Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {hosts.map((host) => (
                <Card
                  key={host.id}
                  className="group cursor-pointer transition-all hover:border-primary hover:shadow-lg"
                  onClick={() => router.push(`/hosts/${host.id}`)}
                >
                  <div className="p-6">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                            {host.name}
                          </h3>
                          {getStatusIcon(host.status)}
                        </div>
                        <p className="text-sm text-muted-foreground font-mono">
                          {host.hostname}
                        </p>
                      </div>
                      {getStatusBadge(host.status)}
                    </div>

                    {/* Provider and Region */}
                    <div className="flex items-center gap-3 mb-4">
                      <ProviderBadge provider={host.provider} size="sm" />
                      <div className="flex items-center gap-1 text-sm text-muted-foreground">
                        <MapPin className="h-3 w-3" />
                        <span>{host.region}</span>
                      </div>
                    </div>

                    {/* Resources */}
                    <div className="grid grid-cols-3 gap-3 mb-4 py-3 border-t border-b">
                      {host.cpu_cores && (
                        <div className="text-center">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <Cpu className="h-3 w-3 text-muted-foreground" />
                          </div>
                          <p className="text-sm font-medium">{host.cpu_cores}</p>
                          <p className="text-xs text-muted-foreground">Cores</p>
                        </div>
                      )}
                      {host.memory_mb && (
                        <div className="text-center">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <Activity className="h-3 w-3 text-muted-foreground" />
                          </div>
                          <p className="text-sm font-medium">{formatBytes(host.memory_mb)}</p>
                          <p className="text-xs text-muted-foreground">RAM</p>
                        </div>
                      )}
                      {host.disk_gb && (
                        <div className="text-center">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <HardDrive className="h-3 w-3 text-muted-foreground" />
                          </div>
                          <p className="text-sm font-medium">{host.disk_gb} GB</p>
                          <p className="text-xs text-muted-foreground">Disk</p>
                        </div>
                      )}
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      {host.ip_address && (
                        <span className="font-mono">{host.ip_address}</span>
                      )}
                      {host.last_seen && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>
                            {formatDistanceToNow(new Date(host.last_seen), { addSuffix: true })}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Tags */}
                    {host.tags && host.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-3">
                        {host.tags.slice(0, 3).map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        {host.tags.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{host.tags.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
