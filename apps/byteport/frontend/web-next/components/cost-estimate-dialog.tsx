'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  TrendingDown,
  Loader2,
  Info,
} from 'lucide-react';
import { formatCurrency } from '@/lib/utils';

export interface CostEstimate {
  provider: string;
  service: string;
  estimatedMonthlyCost: number;
  freeTierEligible: boolean;
  freeTierRemaining?: number;
  freeTierLimit?: number;
  breakdown: {
    label: string;
    cost: number;
    unit: string;
  }[];
  comparisonCost?: number; // AWS comparison
  savingsPercentage?: number;
}

interface CostEstimateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  onCancel: () => void;
  estimate?: CostEstimate;
  loading?: boolean;
  deploymentName?: string;
}

export function CostEstimateDialog({
  open,
  onOpenChange,
  onConfirm,
  onCancel,
  estimate,
  loading = false,
  deploymentName = 'your deployment',
}: CostEstimateDialogProps) {
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
    if (!open) {
      setConfirmed(false);
    }
  }, [open]);

  const handleConfirm = () => {
    setConfirmed(true);
    onConfirm();
  };

  const freeTierPercentage = estimate?.freeTierRemaining && estimate?.freeTierLimit
    ? ((estimate.freeTierLimit - estimate.freeTierRemaining) / estimate.freeTierLimit) * 100
    : 0;

  const isFreeTierAvailable = estimate?.freeTierEligible && freeTierPercentage < 100;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Cost Estimate</DialogTitle>
          <DialogDescription>
            Review estimated costs for {deploymentName}
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-sm text-muted-foreground">Calculating costs...</p>
            </div>
          </div>
        ) : estimate ? (
          <div className="space-y-4">
            {/* Main Cost Card */}
            <Card className={isFreeTierAvailable ? 'border-green-500/50 bg-green-500/5' : ''}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Estimated Monthly Cost</p>
                    <div className="flex items-baseline gap-2">
                      <p className="text-4xl font-bold">
                        {formatCurrency(estimate.estimatedMonthlyCost)}
                      </p>
                      {isFreeTierAvailable && (
                        <Badge variant="default" className="bg-green-500">
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                          Free Tier
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="text-sm">
                      {estimate.provider}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      {estimate.service}
                    </p>
                  </div>
                </div>

                {/* Savings Comparison */}
                {estimate.comparisonCost && estimate.comparisonCost > estimate.estimatedMonthlyCost && (
                  <Alert variant="success" className="mt-4">
                    <TrendingDown className="h-4 w-4" />
                    <AlertDescription>
                      <span className="font-medium">
                        Save {formatCurrency(estimate.comparisonCost - estimate.estimatedMonthlyCost)}
                      </span>
                      {' '}compared to AWS (
                      {estimate.savingsPercentage
                        ? `${estimate.savingsPercentage.toFixed(0)}% savings`
                        : 'significant savings'
                      })
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Free Tier Status */}
            {estimate.freeTierEligible && estimate.freeTierRemaining !== undefined && estimate.freeTierLimit && (
              <Card>
                <CardContent className="pt-6 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium">Free Tier Usage</p>
                    <p className="text-sm text-muted-foreground">
                      {estimate.freeTierRemaining.toLocaleString()} / {estimate.freeTierLimit.toLocaleString()} remaining
                    </p>
                  </div>
                  <Progress
                    value={freeTierPercentage}
                    className={freeTierPercentage >= 80 ? '[&>*]:bg-yellow-500' : '[&>*]:bg-green-500'}
                  />
                  {freeTierPercentage >= 80 && (
                    <Alert variant="warning">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        Approaching free tier limit. Additional usage may incur charges.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Cost Breakdown */}
            {estimate.breakdown && estimate.breakdown.length > 0 && (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm font-medium mb-4">Cost Breakdown</p>
                  <div className="space-y-3">
                    {estimate.breakdown.map((item, index) => (
                      <div key={index}>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">{item.label}</span>
                          <div className="flex items-baseline gap-2">
                            <span className="font-medium">{formatCurrency(item.cost)}</span>
                            <span className="text-xs text-muted-foreground">/ {item.unit}</span>
                          </div>
                        </div>
                        {index < estimate.breakdown.length - 1 && (
                          <Separator className="mt-3" />
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Important Notice */}
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                This is an estimate based on typical usage patterns. Actual costs may vary based on
                your specific usage, traffic, and resource consumption.
              </AlertDescription>
            </Alert>

            {/* Zero Cost Achievement */}
            {estimate.estimatedMonthlyCost === 0 && (
              <Card className="border-green-500 bg-green-500/10">
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-green-500/20 flex items-center justify-center">
                      <DollarSign className="h-6 w-6 text-green-500" />
                    </div>
                    <div>
                      <p className="font-semibold text-green-700 dark:text-green-400">
                        $0 Deployment Achieved!
                      </p>
                      <p className="text-sm text-muted-foreground">
                        This deployment will run entirely on free tier resources
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Unable to calculate cost estimate</p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onCancel} disabled={confirmed}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={!estimate || confirmed || loading}>
            {confirmed ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deploying...
              </>
            ) : (
              'Confirm & Deploy'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
