'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CostChart, CostDataPoint } from '@/components/cost-chart';
import { CostTracker } from '@/components/cost-tracker';
import { FreeTierUsage, FreeTierLimit } from '@/components/free-tier-usage';
import { CostBreakdownTable, CostBreakdownItem } from '@/components/cost-breakdown-table';
import { CostEstimateDialog, CostEstimate } from '@/components/cost-estimate-dialog';
import { Download, TrendingDown, TrendingUp, DollarSign, AlertTriangle, Calculator, Award, Zap } from 'lucide-react';
import { getCostAnalytics } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import toast from 'react-hot-toast';
import type { CostData, ProviderName } from '@/lib/types';

export default function CostAnalyticsPage() {
  const [costData, setCostData] = useState<CostData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, _setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [estimateDialogOpen, setEstimateDialogOpen] = useState(false);
  const [selectedEstimate, setSelectedEstimate] = useState<CostEstimate | undefined>();

  useEffect(() => {
    loadCostData();
  }, [timeRange]);

  const loadCostData = async () => {
    try {
      setLoading(true);
      const data = await getCostAnalytics();
      setCostData(data);
    } catch (error) {
      toast.error('Failed to load cost analytics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const exportData = (format: 'csv' | 'pdf') => {
    if (!costData) return;
    
    if (format === 'csv') {
      const csvContent = generateCSV(costData);
      downloadFile(csvContent, 'cost-analytics.csv', 'text/csv');
      toast.success('Cost data exported as CSV');
    } else {
      toast('PDF export coming soon');
    }
  };

  const generateCSV = (data: CostData): string => {
    const headers = ['Deployment', 'Provider', 'Cost', 'Usage Hours'];
    const rows = data.deployments.map(d => [
      d.name,
      d.provider,
      d.cost.toString(),
      d.usage_hours.toString()
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading cost analytics...</p>
        </div>
      </div>
    );
  }

  if (!costData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Failed to load cost data</p>
          <Button onClick={loadCostData} className="mt-4">Retry</Button>
        </div>
      </div>
    );
  }

  // Calculate metrics
  const currentMonthCost = costData.total_cost || 0;
  const projectedCost = costData.projected_monthly_cost || currentMonthCost * 1.5;
  const savings = Math.max(0, projectedCost - currentMonthCost);
  const freeTierUsage = costData.deployments.filter(d => d.cost === 0).length;
  const totalDeployments = costData.deployments.length;
  const freeTierPercentage = totalDeployments > 0 ? (freeTierUsage / totalDeployments) * 100 : 0;
  const zeroDeploymentsCount = costData.deployments.filter(d => d.cost === 0).length;

  // Cost trend calculation
  const costTrend: 'increasing' | 'decreasing' | 'stable' =
    projectedCost > currentMonthCost * 1.1 ? 'increasing' :
    projectedCost < currentMonthCost * 0.9 ? 'decreasing' : 'stable';

  // Prepare chart data
  const costOverTimeData: CostDataPoint[] = costData.deployments.map((d, i) => ({
    date: new Date(Date.now() - (totalDeployments - i) * 24 * 60 * 60 * 1000).toISOString(),
    cost: d.cost,
    provider: d.provider,
    label: d.name
  }));

  const providerData: CostDataPoint[] = Object.entries(costData.by_provider || {}).map(([provider, cost]) => ({
    date: provider,
    cost: cost as number,
    provider: provider as ProviderName
  }));

  // Transform deployment data for breakdown table
  const breakdownItems: CostBreakdownItem[] = costData.deployments.map((d) => ({
    id: d.id,
    name: d.name,
    provider: d.provider,
    type: 'Web Service', // You can enhance this based on actual deployment type
    cost: d.cost,
    usage: d.usage_hours,
    usageUnit: 'hours',
    status: 'active' as const,
    lastUpdated: new Date().toISOString(),
    trend: Math.random() > 0.5 ? 'up' : 'down',
    trendPercentage: Math.random() * 20,
  }));

  // Free tier limits data
  const freeTierLimits: FreeTierLimit[] = [
    {
      provider: 'vercel',
      displayName: 'Vercel',
      resources: [
        {
          name: 'Deployments',
          description: 'Monthly deployment limit',
          current: 12,
          limit: 20,
          unit: 'deployments',
          resetPeriod: 'monthly',
        },
        {
          name: 'Bandwidth',
          description: 'Data transfer limit',
          current: 85,
          limit: 100,
          unit: 'GB',
          resetPeriod: 'monthly',
        },
      ],
    },
    {
      provider: 'netlify',
      displayName: 'Netlify',
      resources: [
        {
          name: 'Build Minutes',
          description: 'Monthly build time',
          current: 280,
          limit: 300,
          unit: 'minutes',
          resetPeriod: 'monthly',
        },
        {
          name: 'Bandwidth',
          description: 'Data transfer limit',
          current: 75,
          limit: 100,
          unit: 'GB',
          resetPeriod: 'monthly',
        },
      ],
    },
    {
      provider: 'render',
      displayName: 'Render',
      resources: [
        {
          name: 'Build Minutes',
          description: 'Monthly build time',
          current: 400,
          limit: 500,
          unit: 'minutes',
          resetPeriod: 'monthly',
        },
        {
          name: 'Bandwidth',
          description: 'Data transfer limit',
          current: 85,
          limit: 100,
          unit: 'GB',
          resetPeriod: 'monthly',
        },
      ],
    },
    {
      provider: 'railway',
      displayName: 'Railway',
      resources: [
        {
          name: 'Execution Hours',
          description: 'Runtime hours limit',
          current: 450,
          limit: 500,
          unit: 'hours',
          resetPeriod: 'monthly',
        },
      ],
    },
  ];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Cost Analytics</h1>
          <p className="text-muted-foreground">
            Track and optimize your deployment costs
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => exportData('csv')}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => exportData('pdf')}>
            <Download className="mr-2 h-4 w-4" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(currentMonthCost)}</div>
            <p className="text-xs text-muted-foreground">
              {costTrend === 'increasing' ? '+' : costTrend === 'decreasing' ? '-' : ''}
              {Math.abs(((projectedCost - currentMonthCost) / currentMonthCost) * 100 || 0).toFixed(1)}% projected
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Projected</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(projectedCost)}</div>
            <p className="text-xs text-muted-foreground">
              End of month estimate
            </p>
          </CardContent>
        </Card>

        <Card className="border-green-500/50 bg-green-500/5">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">$0 Deployments</CardTitle>
            <Award className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{zeroDeploymentsCount}</div>
            <p className="text-xs text-green-600">
              {freeTierPercentage.toFixed(0)}% on free tier
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potential Savings</CardTitle>
            <TrendingDown className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">{formatCurrency(savings)}</div>
            <p className="text-xs text-muted-foreground">
              vs traditional hosting
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Cost Tracker Widget */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <CostTracker
          current={currentMonthCost}
          budget={100}
          projected={projectedCost}
          trend={costTrend}
          period="October 2025"
          className="lg:col-span-1"
        />

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Cost Optimization Tips</CardTitle>
            <CardDescription>Maximize your free tier usage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-green-500/10 flex items-center justify-center flex-shrink-0">
                <Zap className="h-4 w-4 text-green-500" />
              </div>
              <div>
                <p className="text-sm font-medium">Free Tier First</p>
                <p className="text-xs text-muted-foreground">
                  Deploy static sites on Vercel/Netlify and use serverless functions to stay within free limits
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                <Calculator className="h-4 w-4 text-blue-500" />
              </div>
              <div>
                <p className="text-sm font-medium">Monitor Usage</p>
                <p className="text-xs text-muted-foreground">
                  Track your resource usage to avoid unexpected charges and optimize deployments
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                <Award className="h-4 w-4 text-purple-500" />
              </div>
              <div>
                <p className="text-sm font-medium">Multi-Provider Strategy</p>
                <p className="text-xs text-muted-foreground">
                  Distribute workloads across providers to maximize free tier benefits across platforms
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="breakdown" className="space-y-4">
        <TabsList>
          <TabsTrigger value="breakdown">Cost Breakdown</TabsTrigger>
          <TabsTrigger value="timeline">Cost Over Time</TabsTrigger>
          <TabsTrigger value="providers">By Provider</TabsTrigger>
          <TabsTrigger value="freetier">Free Tier</TabsTrigger>
        </TabsList>

        <TabsContent value="breakdown" className="space-y-4">
          <CostBreakdownTable
            items={breakdownItems}
            showTrend={true}
            onItemClick={(item) => {
              toast.success(`Viewing details for ${item.name}`);
            }}
          />
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <CostChart
            data={costOverTimeData}
            type="area"
            title="Cost Over Time"
            description="Track your spending trends"
            height={400}
            color="hsl(var(--primary))"
          />
        </TabsContent>

        <TabsContent value="providers" className="space-y-4">
          <CostChart
            data={providerData}
            type="bar"
            title="Cost by Provider"
            description="Compare spending across providers"
            height={400}
            color="hsl(var(--primary))"
          />
        </TabsContent>

        <TabsContent value="freetier" className="space-y-4">
          <FreeTierUsage limits={freeTierLimits} />
        </TabsContent>
      </Tabs>

      {/* Cost Projection and Achievements */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Cost Projection</CardTitle>
            <CardDescription>
              Estimate your costs based on current usage patterns
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium mb-1">Current Daily Average</p>
                  <p className="text-2xl font-bold">
                    {formatCurrency(currentMonthCost / 30)}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium mb-1">7-Day Projection</p>
                  <p className="text-2xl font-bold">
                    {formatCurrency((currentMonthCost / 30) * 7)}
                  </p>
                </div>
              </div>
              <div className="pt-3 border-t">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">30-Day Projection</p>
                  <p className="text-3xl font-bold">
                    {formatCurrency(projectedCost)}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    setSelectedEstimate({
                      provider: 'Multi-Provider',
                      service: 'Optimized Deployment',
                      estimatedMonthlyCost: projectedCost,
                      freeTierEligible: true,
                      freeTierRemaining: 150,
                      freeTierLimit: 500,
                      breakdown: [
                        { label: 'Compute', cost: projectedCost * 0.4, unit: 'month' },
                        { label: 'Storage', cost: projectedCost * 0.2, unit: 'month' },
                        { label: 'Bandwidth', cost: projectedCost * 0.3, unit: 'month' },
                        { label: 'Other', cost: projectedCost * 0.1, unit: 'month' },
                      ],
                      comparisonCost: projectedCost * 3,
                      savingsPercentage: 67,
                    });
                    setEstimateDialogOpen(true);
                  }}
                >
                  <Calculator className="mr-2 h-4 w-4" />
                  View Detailed Estimate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-green-500/50 bg-gradient-to-br from-green-500/5 to-emerald-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-green-500" />
              $0 Achievement Tracker
            </CardTitle>
            <CardDescription>
              Maximize free tier deployments
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Free Deployments</p>
                  <p className="text-3xl font-bold text-green-600">{zeroDeploymentsCount}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Total Saved</p>
                  <p className="text-2xl font-bold">{formatCurrency(savings)}</p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Progress to 100% Free</span>
                  <span className="font-medium">{freeTierPercentage.toFixed(0)}%</span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all"
                    style={{ width: `${Math.min(freeTierPercentage, 100)}%` }}
                  />
                </div>
              </div>
              <div className="pt-3 border-t">
                <p className="text-xs text-muted-foreground">
                  Keep deploying on free tiers to maintain $0/month operation costs
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cost Estimate Dialog */}
      <CostEstimateDialog
        open={estimateDialogOpen}
        onOpenChange={setEstimateDialogOpen}
        onConfirm={() => {
          toast.success('Deployment confirmed!');
          setEstimateDialogOpen(false);
        }}
        onCancel={() => {
          setEstimateDialogOpen(false);
        }}
        estimate={selectedEstimate}
        deploymentName="Multi-Provider Strategy"
      />
    </div>
  );
}
