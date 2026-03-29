'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  getDeployment,
  getDeploymentLogs,
  streamDeploymentLogs,
  type Deployment,
  type LogEntry,
  type LogLevel,
} from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  ChevronLeft,
  RefreshCw,
  Download,
  Search,
  Play,
  Pause,
  Trash2,
  Terminal,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import toast from 'react-hot-toast';

type ServiceFilter = 'all' | 'build' | 'runtime' | 'system';

export default function DeploymentLogsPage() {
  const params = useParams();
  const id = params.id as string;
  const logsEndRef = useRef<HTMLDivElement>(null);
  const logsContainerRef = useRef<HTMLDivElement>(null);

  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState<LogLevel | 'all'>('all');
  const [serviceFilter, setServiceFilter] = useState<ServiceFilter>('all');

  // Controls
  const [autoScroll, setAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    loadDeploymentData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    if (!isPaused) {
      startStreaming();
    }

    return () => {
      stopStreaming();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, isPaused]);

  useEffect(() => {
    applyFilters();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [logs, searchQuery, levelFilter, serviceFilter]);

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs, autoScroll]);

  const loadDeploymentData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [deploymentData, logsData] = await Promise.all([
        getDeployment(id),
        getDeploymentLogs(id),
      ]);

      setDeployment(deploymentData);
      setLogs(logsData.logs || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load deployment');
    } finally {
      setLoading(false);
    }
  };

  const startStreaming = useCallback(() => {
    if (isStreaming || eventSourceRef.current) return;

    try {
      setIsStreaming(true);
      const eventSource = streamDeploymentLogs(
        id,
        (log) => {
          setLogs((prev) => [...prev, log]);
        },
        (error) => {
          console.error('Streaming error:', error);
          toast.error('Log streaming disconnected');
          setIsStreaming(false);
        }
      );

      eventSourceRef.current = eventSource;
    } catch (err) {
      console.error('Failed to start streaming:', err);
      setIsStreaming(false);
    }
  }, [id, isStreaming]);

  const stopStreaming = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsStreaming(false);
    }
  }, []);

  const applyFilters = () => {
    let filtered = [...logs];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((log) =>
        log.message.toLowerCase().includes(query)
      );
    }

    if (levelFilter !== 'all') {
      filtered = filtered.filter((log) => log.level === levelFilter);
    }

    if (serviceFilter !== 'all') {
      filtered = filtered.filter((log) => log.source === serviceFilter);
    }

    setFilteredLogs(filtered);
  };

  const handleClearLogs = () => {
    if (confirm('Are you sure you want to clear all logs from view?')) {
      setLogs([]);
      toast.success('Logs cleared');
    }
  };

  const handleDownloadLogs = () => {
    const logsText = filteredLogs
      .map(
        (log) =>
          `[${new Date(log.timestamp).toISOString()}] [${log.level.toUpperCase()}] ${
            log.source ? `[${log.source}] ` : ''
          }${log.message}`
      )
      .join('\n');

    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${deployment?.name || id}-logs-${new Date().toISOString()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Logs downloaded');
  };

  const togglePause = () => {
    if (isPaused) {
      setIsPaused(false);
      startStreaming();
      toast.success('Log streaming resumed');
    } else {
      setIsPaused(true);
      stopStreaming();
      toast.success('Log streaming paused');
    }
  };

  const _getLogColor = (level: string) => {
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

  const getLevelBadgeColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
      case 'fatal':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'warn':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'debug':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const logLevelCounts = logs.reduce((acc, log) => {
    acc[log.level] = (acc[log.level] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-3">
            <Loader2 className="h-8 w-8 text-blue-600 animate-spin" />
            <span className="text-gray-600">Loading logs...</span>
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
                <p className="font-medium text-red-900">Error loading logs</p>
                <p className="text-sm text-red-700 mt-1">{error || 'Deployment not found'}</p>
                <div className="flex gap-2 mt-4">
                  <Link href={`/deployments/${id}`}>
                    <Button variant="outline" size="sm">
                      Back to Deployment
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
          href={`/deployments/${id}`}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium inline-flex items-center gap-1 mb-4"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Deployment
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Deployment Logs</h1>
            <p className="text-gray-600">{deployment.name}</p>
          </div>

          <div className="flex items-center gap-2">
            <Badge className={isPaused ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}>
              {isPaused ? 'Paused' : 'Live'}
            </Badge>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{logs.length}</div>
          </CardContent>
        </Card>
        {(['error', 'warn', 'info', 'debug'] as const).map((level) => (
          <Card key={level}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600 capitalize">{level}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{logLevelCounts[level] || 0}</div>
            </CardContent>
          </Card>
        ))}
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
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filters */}
            <div className="flex gap-2 flex-wrap">
              <select
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value as LogLevel | 'all')}
                className="px-4 py-2 border rounded-md bg-white text-sm"
              >
                <option value="all">All Levels</option>
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warn">Warn</option>
                <option value="error">Error</option>
                <option value="fatal">Fatal</option>
              </select>

              <select
                value={serviceFilter}
                onChange={(e) => setServiceFilter(e.target.value as ServiceFilter)}
                className="px-4 py-2 border rounded-md bg-white text-sm"
              >
                <option value="all">All Sources</option>
                <option value="build">Build</option>
                <option value="runtime">Runtime</option>
                <option value="system">System</option>
              </select>

              <Button
                variant={autoScroll ? 'default' : 'outline'}
                size="sm"
                onClick={() => setAutoScroll(!autoScroll)}
              >
                Auto-scroll
              </Button>

              <Button variant="outline" size="sm" onClick={togglePause}>
                {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
              </Button>

              <Button variant="outline" size="sm" onClick={loadDeploymentData}>
                <RefreshCw className="w-4 h-4" />
              </Button>

              <Button variant="outline" size="sm" onClick={handleDownloadLogs}>
                <Download className="w-4 h-4" />
              </Button>

              <Button variant="outline" size="sm" onClick={handleClearLogs}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            Showing {filteredLogs.length} of {logs.length} log entries
          </div>
        </CardContent>
      </Card>

      {/* Logs Display */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            Log Stream
            {isStreaming && !isPaused && (
              <Badge className="bg-green-100 text-green-800 ml-2">
                <div className="w-2 h-2 bg-green-600 rounded-full mr-2 animate-pulse" />
                Streaming
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            ref={logsContainerRef}
            className="bg-gray-900 rounded-lg p-4 font-mono text-sm overflow-x-auto max-h-[600px] overflow-y-auto"
          >
            {filteredLogs.length === 0 ? (
              <div className="text-gray-400 text-center py-12">
                <Terminal className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>
                  {logs.length === 0
                    ? 'No logs available'
                    : 'No logs match the current filters'}
                </p>
              </div>
            ) : (
              <div className="space-y-0.5">
                {filteredLogs.map((log, idx) => (
                  <div
                    key={log.id || idx}
                    className="hover:bg-gray-800 px-2 py-1 rounded transition-colors"
                  >
                    <span className="text-gray-500 select-none">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>{' '}
                    <Badge
                      className={`${getLevelBadgeColor(log.level)} text-xs mx-2`}
                    >
                      {log.level.toUpperCase()}
                    </Badge>
                    {log.source && (
                      <span className="text-purple-400 mr-2">[{log.source}]</span>
                    )}
                    <span className="text-gray-300">{log.message}</span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
