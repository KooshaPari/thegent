'use client';

import * as React from 'react';
import { DeploymentMonitor } from './deployment-monitor';
import { RealtimeLogViewer } from './realtime-log-viewer';
import { RealtimeMetricsDashboard } from './realtime-metrics-dashboard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, FileText, BarChart3 } from 'lucide-react';

export interface RealtimeDeploymentViewProps {
  deploymentId: string;
  deploymentName?: string;
  defaultTab?: 'status' | 'logs' | 'metrics';
}

/**
 * Complete Real-time Deployment View
 *
 * Combines all real-time features for a deployment:
 * - Status monitoring
 * - Log streaming
 * - Metrics dashboard
 *
 * @example
 * ```tsx
 * <RealtimeDeploymentView
 *   deploymentId="deploy-123"
 *   deploymentName="My App"
 *   defaultTab="logs"
 * />
 * ```
 */
export function RealtimeDeploymentView({
  deploymentId,
  deploymentName = 'Deployment',
  defaultTab = 'status',
}: RealtimeDeploymentViewProps) {
  return (
    <div className="space-y-6">
      {/* Deployment Monitor - Always visible */}
      <DeploymentMonitor
        deploymentId={deploymentId}
        deploymentName={deploymentName}
        showToasts={true}
      />

      {/* Tabbed Content */}
      <Tabs defaultValue={defaultTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="logs" className="gap-2">
            <FileText className="h-4 w-4" />
            Logs
          </TabsTrigger>
          <TabsTrigger value="metrics" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            Metrics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="logs" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Real-time Logs
              </CardTitle>
              <CardDescription>
                Stream deployment logs in real-time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RealtimeLogViewer
                deploymentId={deploymentId}
                autoScroll={true}
                terminalMode={true}
                showLineNumbers={true}
                maxLogs={1000}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Real-time Metrics
              </CardTitle>
              <CardDescription>
                Monitor deployment performance metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RealtimeMetricsDashboard
                deploymentId={deploymentId}
                maxDataPoints={50}
                showCombinedChart={false}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
