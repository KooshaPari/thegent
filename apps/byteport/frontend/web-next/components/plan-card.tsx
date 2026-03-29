'use client';

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatCurrency } from '@/lib/utils';

export type PlanType = 'free' | 'pro' | 'enterprise';

export interface PlanFeature {
  name: string;
  included: boolean;
  limit?: string;
}

export interface Plan {
  id: string;
  name: string;
  type: PlanType;
  price: number;
  interval: 'month' | 'year';
  description: string;
  features: PlanFeature[];
  popular?: boolean;
  current?: boolean;
}

interface PlanCardProps {
  plan: Plan;
  onSelect?: (plan: Plan) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function PlanCard({ plan, onSelect, isLoading = false, disabled = false }: PlanCardProps) {
  const isCurrentPlan = plan.current;
  const buttonText = isCurrentPlan ? 'Current Plan' : plan.type === 'enterprise' ? 'Contact Sales' : 'Upgrade';

  return (
    <Card className={cn(
      'relative',
      plan.popular && 'border-primary shadow-lg',
      isCurrentPlan && 'border-2 border-primary'
    )}>
      {plan.popular && (
        <div className="absolute -top-3 left-0 right-0 flex justify-center">
          <Badge className="bg-primary">Most Popular</Badge>
        </div>
      )}

      <CardHeader className="text-center pb-4">
        <CardTitle className="text-2xl">{plan.name}</CardTitle>
        <CardDescription>{plan.description}</CardDescription>
        <div className="mt-4">
          <div className="flex items-baseline justify-center gap-1">
            <span className="text-4xl font-bold">
              {plan.price === 0 ? 'Free' : formatCurrency(plan.price)}
            </span>
            {plan.price > 0 && (
              <span className="text-muted-foreground">/{plan.interval}</span>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {plan.features.map((feature, index) => (
          <div key={index} className="flex items-start gap-3">
            <Check
              className={cn(
                'h-5 w-5 mt-0.5 flex-shrink-0',
                feature.included ? 'text-primary' : 'text-muted-foreground opacity-50'
              )}
            />
            <div className="flex-1">
              <p className={cn(
                'text-sm',
                !feature.included && 'text-muted-foreground line-through'
              )}>
                {feature.name}
              </p>
              {feature.limit && (
                <p className="text-xs text-muted-foreground">{feature.limit}</p>
              )}
            </div>
          </div>
        ))}
      </CardContent>

      <CardFooter>
        <Button
          className="w-full"
          variant={isCurrentPlan ? 'outline' : 'default'}
          onClick={() => onSelect?.(plan)}
          disabled={disabled || isCurrentPlan || isLoading}
        >
          {isLoading ? 'Loading...' : buttonText}
        </Button>
      </CardFooter>
    </Card>
  );
}
