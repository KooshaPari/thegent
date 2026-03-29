'use client';

import { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  X,
  TrendingUp,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface UsageAlert {
  id: string;
  type: 'warning' | 'critical' | 'info' | 'success';
  provider: string;
  resource: string;
  message: string;
  currentUsage: number;
  limit: number;
  unit: string;
  recommendations?: string[];
  alternativeProviders?: {
    name: string;
    benefit: string;
  }[];
  timestamp: string;
  dismissible?: boolean;
}

interface UsageAlertsProps {
  alerts: UsageAlert[];
  onDismiss?: (alertId: string) => void;
  onViewProvider?: (provider: string) => void;
  showRecommendations?: boolean;
  className?: string;
}

export function UsageAlerts({
  alerts,
  onDismiss,
  onViewProvider,
  showRecommendations = true,
  className,
}: UsageAlertsProps) {
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  const handleDismiss = (alertId: string) => {
    setDismissedAlerts(prev => new Set(prev).add(alertId));
    onDismiss?.(alertId);
  };

  const visibleAlerts = alerts.filter(alert => !dismissedAlerts.has(alert.id));

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return <AlertCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4" />;
      case 'success':
        return <CheckCircle2 className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getAlertVariant = (type: string) => {
    switch (type) {
      case 'critical':
        return 'destructive' as const;
      case 'warning':
        return 'warning' as const;
      case 'success':
        return 'success' as const;
      default:
        return 'default' as const;
    }
  };

  const getUsagePercentage = (alert: UsageAlert) => {
    return ((alert.currentUsage / alert.limit) * 100).toFixed(1);
  };

  if (visibleAlerts.length === 0) {
    return null;
  }

  // Critical alerts (banner style at top)
  const criticalAlerts = visibleAlerts.filter(a => a.type === 'critical');
  const otherAlerts = visibleAlerts.filter(a => a.type !== 'critical');

  return (
    <div className={cn('space-y-4', className)}>
      {/* Critical Alerts - Full Width Banner */}
      {criticalAlerts.map((alert) => (
        <Alert key={alert.id} variant={getAlertVariant(alert.type)} className="relative">
          {getAlertIcon(alert.type)}
          <div className="flex items-start justify-between gap-4 flex-1">
            <div className="flex-1">
              <AlertTitle className="flex items-center gap-2">
                {alert.provider} - {alert.resource}
                <Badge variant="destructive" className="ml-2">
                  {getUsagePercentage(alert)}% Used
                </Badge>
              </AlertTitle>
              <AlertDescription className="mt-2">
                {alert.message}
              </AlertDescription>

              {showRecommendations && alert.recommendations && alert.recommendations.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-sm font-medium">Immediate Actions Required:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {alert.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              {alert.alternativeProviders && alert.alternativeProviders.length > 0 && (
                <div className="mt-3 space-y-2">
                  <p className="text-sm font-medium">Alternative Providers:</p>
                  <div className="flex gap-2 flex-wrap">
                    {alert.alternativeProviders.map((provider, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        onClick={() => onViewProvider?.(provider.name)}
                        className="text-xs"
                      >
                        {provider.name}
                        <ArrowRight className="ml-1 h-3 w-3" />
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            {alert.dismissible && onDismiss && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDismiss(alert.id)}
                className="h-6 w-6 p-0 absolute top-3 right-3"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </Alert>
      ))}

      {/* Other Alerts - Card Format */}
      {otherAlerts.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Usage Alerts</CardTitle>
                <CardDescription>
                  {otherAlerts.length} active alert{otherAlerts.length !== 1 ? 's' : ''}
                </CardDescription>
              </div>
              {otherAlerts.filter(a => a.type === 'warning').length > 0 && (
                <Badge variant="warning">
                  <AlertTriangle className="mr-1 h-3 w-3" />
                  {otherAlerts.filter(a => a.type === 'warning').length} Warning
                  {otherAlerts.filter(a => a.type === 'warning').length !== 1 ? 's' : ''}
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {otherAlerts.map((alert) => (
              <Alert key={alert.id} variant={getAlertVariant(alert.type)} className="relative">
                {getAlertIcon(alert.type)}
                <div className="flex items-start justify-between gap-4 flex-1">
                  <div className="flex-1">
                    <AlertTitle className="flex items-center gap-2">
                      {alert.provider} - {alert.resource}
                      <Badge variant="outline" className="ml-2 text-xs">
                        {alert.currentUsage.toLocaleString()} / {alert.limit.toLocaleString()} {alert.unit}
                      </Badge>
                    </AlertTitle>
                    <AlertDescription className="mt-1.5">
                      {alert.message}
                    </AlertDescription>

                    {showRecommendations && alert.recommendations && alert.recommendations.length > 0 && (
                      <div className="mt-3 space-y-1.5">
                        <p className="text-xs font-medium">Recommendations:</p>
                        <ul className="list-disc list-inside space-y-0.5 text-xs">
                          {alert.recommendations.map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {alert.alternativeProviders && alert.alternativeProviders.length > 0 && (
                      <div className="mt-2 flex gap-2 flex-wrap">
                        {alert.alternativeProviders.map((provider, idx) => (
                          <Button
                            key={idx}
                            variant="outline"
                            size="sm"
                            onClick={() => onViewProvider?.(provider.name)}
                            className="text-xs h-7"
                          >
                            <TrendingUp className="mr-1 h-3 w-3" />
                            Try {provider.name}
                          </Button>
                        ))}
                      </div>
                    )}

                    <p className="text-xs text-muted-foreground mt-2">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  {alert.dismissible && onDismiss && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDismiss(alert.id)}
                      className="h-6 w-6 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </Alert>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
