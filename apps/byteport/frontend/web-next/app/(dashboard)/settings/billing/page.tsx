'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Section } from '@/components/section';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  CreditCard,
  Download,
  Check,
  Info
} from 'lucide-react';
import { formatCurrency, formatDate } from '@/lib/utils';

// Mock data
const currentPlan = {
  id: 'free',
  name: 'Free Tier',
  tier: 'free' as const,
  price: 0,
  currency: 'USD',
  billing_period: 'monthly' as const,
  features: [
    'Up to 3 deployments',
    '100 API calls per day',
    '1GB bandwidth per month',
    '500MB storage',
    'Community support'
  ],
  limits: {
    deployments: 3,
    api_calls: 100,
    bandwidth_gb: 1,
    storage_gb: 0.5,
    team_members: 1
  }
};

const currentUsage = {
  current_period_start: '2024-03-01T00:00:00Z',
  current_period_end: '2024-03-31T23:59:59Z',
  total_cost: 0,
  currency: 'USD',
  deployments_used: 2,
  api_calls_used: 847,
  bandwidth_gb_used: 0.34,
  storage_gb_used: 0.12,
  breakdown: {
    compute: 0,
    storage: 0,
    bandwidth: 0,
    api_calls: 0
  }
};

const billingHistory = [
  {
    id: '1',
    period_start: '2024-02-01T00:00:00Z',
    period_end: '2024-02-29T23:59:59Z',
    amount: 0,
    currency: 'USD',
    status: 'paid' as const,
    invoice_url: '#',
    created_at: '2024-03-01T00:00:00Z'
  },
  {
    id: '2',
    period_start: '2024-01-01T00:00:00Z',
    period_end: '2024-01-31T23:59:59Z',
    amount: 0,
    currency: 'USD',
    status: 'paid' as const,
    invoice_url: '#',
    created_at: '2024-02-01T00:00:00Z'
  }
];

const upgradePlans = [
  {
    id: 'hobby',
    name: 'Hobby',
    tier: 'hobby' as const,
    price: 19,
    currency: 'USD',
    billing_period: 'monthly' as const,
    features: [
      'Up to 10 deployments',
      '10,000 API calls per day',
      '10GB bandwidth per month',
      '5GB storage',
      'Email support',
      'Custom domains'
    ],
    limits: {
      deployments: 10,
      api_calls: 10000,
      bandwidth_gb: 10,
      storage_gb: 5,
      team_members: 3
    }
  },
  {
    id: 'pro',
    name: 'Pro',
    tier: 'pro' as const,
    price: 49,
    currency: 'USD',
    billing_period: 'monthly' as const,
    popular: true,
    features: [
      'Unlimited deployments',
      '100,000 API calls per day',
      '100GB bandwidth per month',
      '50GB storage',
      'Priority support',
      'Custom domains',
      'Advanced analytics',
      'Team collaboration'
    ],
    limits: {
      deployments: -1,
      api_calls: 100000,
      bandwidth_gb: 100,
      storage_gb: 50,
      team_members: 10
    }
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    tier: 'enterprise' as const,
    price: 199,
    currency: 'USD',
    billing_period: 'monthly' as const,
    features: [
      'Unlimited everything',
      'Dedicated support',
      'SLA guarantees',
      'Custom integrations',
      'Advanced security',
      'Audit logs',
      'SSO/SAML',
      'Unlimited team members'
    ],
    limits: {
      deployments: -1,
      api_calls: -1,
      bandwidth_gb: -1,
      storage_gb: -1,
      team_members: -1
    }
  }
];

export default function BillingPage() {
  const [_selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0; // Unlimited
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-destructive';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <Section>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Current Plan</CardTitle>
                <CardDescription>
                  You are currently on the {currentPlan.name} plan
                </CardDescription>
              </div>
              <Badge variant="secondary" className="text-lg px-4 py-2">
                {formatCurrency(currentPlan.price)}/{currentPlan.billing_period === 'monthly' ? 'mo' : 'yr'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {currentPlan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <Check className="h-4 w-4 text-green-600" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Current Usage */}
      <Section>
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Current Period Usage</CardTitle>
                <CardDescription>
                  {formatDate(currentUsage.current_period_start, 'MMM d')} - {formatDate(currentUsage.current_period_end, 'MMM d, yyyy')}
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">
                  {formatCurrency(currentUsage.total_cost)}
                </div>
                <p className="text-sm text-muted-foreground">Total cost</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Deployments */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">Deployments</span>
                  <span className={getUsageColor(getUsagePercentage(currentUsage.deployments_used, currentPlan.limits.deployments))}>
                    {currentUsage.deployments_used} / {currentPlan.limits.deployments}
                  </span>
                </div>
                <Progress
                  value={getUsagePercentage(currentUsage.deployments_used, currentPlan.limits.deployments)}
                  className="h-2"
                />
              </div>

              {/* API Calls */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">API Calls (Daily)</span>
                  <span className={getUsageColor(getUsagePercentage(currentUsage.api_calls_used, currentPlan.limits.api_calls))}>
                    {currentUsage.api_calls_used.toLocaleString()} / {currentPlan.limits.api_calls.toLocaleString()}
                  </span>
                </div>
                <Progress
                  value={getUsagePercentage(currentUsage.api_calls_used, currentPlan.limits.api_calls)}
                  className="h-2"
                />
              </div>

              {/* Bandwidth */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">Bandwidth</span>
                  <span className={getUsageColor(getUsagePercentage(currentUsage.bandwidth_gb_used, currentPlan.limits.bandwidth_gb))}>
                    {currentUsage.bandwidth_gb_used.toFixed(2)} GB / {currentPlan.limits.bandwidth_gb} GB
                  </span>
                </div>
                <Progress
                  value={getUsagePercentage(currentUsage.bandwidth_gb_used, currentPlan.limits.bandwidth_gb)}
                  className="h-2"
                />
              </div>

              {/* Storage */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">Storage</span>
                  <span className={getUsageColor(getUsagePercentage(currentUsage.storage_gb_used, currentPlan.limits.storage_gb))}>
                    {currentUsage.storage_gb_used.toFixed(2)} GB / {currentPlan.limits.storage_gb} GB
                  </span>
                </div>
                <Progress
                  value={getUsagePercentage(currentUsage.storage_gb_used, currentPlan.limits.storage_gb)}
                  className="h-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </Section>

      {/* Upgrade Plans */}
      <Section>
        <div className="mb-4">
          <h3 className="text-lg font-semibold">Upgrade Your Plan</h3>
          <p className="text-sm text-muted-foreground">
            Choose a plan that fits your needs
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {upgradePlans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative ${plan.popular ? 'border-primary shadow-lg' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-primary">Most Popular</Badge>
                </div>
              )}
              <CardHeader>
                <CardTitle>{plan.name}</CardTitle>
                <div className="mt-4">
                  <span className="text-4xl font-bold">
                    {formatCurrency(plan.price)}
                  </span>
                  <span className="text-muted-foreground">/{plan.billing_period === 'monthly' ? 'mo' : 'yr'}</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  className="w-full"
                  variant={plan.popular ? 'default' : 'outline'}
                  onClick={() => setSelectedPlan(plan.id)}
                >
                  {currentPlan.id === plan.id ? 'Current Plan' : 'Upgrade'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </Section>

      {/* Billing History */}
      <Section>
        <Card>
          <CardHeader>
            <CardTitle>Billing History</CardTitle>
            <CardDescription>
              View and download your past invoices
            </CardDescription>
          </CardHeader>
          <CardContent>
            {billingHistory.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No billing history available
              </div>
            ) : (
              <div className="space-y-4">
                {billingHistory.map((invoice) => (
                  <div
                    key={invoice.id}
                    className="flex items-center justify-between p-4 rounded-lg border"
                  >
                    <div className="flex items-center gap-4">
                      <div className="rounded-full bg-muted p-2">
                        <CreditCard className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-medium">
                          {formatDate(invoice.period_start, 'MMM d')} - {formatDate(invoice.period_end, 'MMM d, yyyy')}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {formatCurrency(invoice.amount)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge
                        variant={
                          invoice.status === 'paid'
                            ? 'secondary'
                            : invoice.status === 'pending'
                            ? 'default'
                            : 'destructive'
                        }
                      >
                        {invoice.status}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </Section>

      {/* Payment Method */}
      <Section>
        <Card>
          <CardHeader>
            <CardTitle>Payment Method</CardTitle>
            <CardDescription>
              Manage your payment methods
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Free Tier</AlertTitle>
              <AlertDescription>
                You're currently on the free tier. Add a payment method when you're ready to upgrade.
              </AlertDescription>
            </Alert>
            <div className="mt-4">
              <Button variant="outline">
                <CreditCard className="h-4 w-4 mr-2" />
                Add Payment Method
              </Button>
            </div>
          </CardContent>
        </Card>
      </Section>
    </div>
  );
}
