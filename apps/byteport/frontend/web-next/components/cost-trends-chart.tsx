'use client';

import { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatCurrency } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface CostTrendDataPoint {
  date: string;
  cost: number;
  previousPeriodCost?: number;
  provider?: string;
}

interface CostTrendsChartProps {
  data: CostTrendDataPoint[];
  title?: string;
  description?: string;
  showComparison?: boolean;
  defaultTimeRange?: TimeRange;
  height?: number;
  className?: string;
}

export type TimeRange = '7d' | '30d' | '90d' | '1y';

const timeRangeLabels: Record<TimeRange, string> = {
  '7d': '7 Days',
  '30d': '30 Days',
  '90d': '90 Days',
  '1y': '1 Year',
};

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const current = payload.find(p => p.dataKey === 'cost');
    const previous = payload.find(p => p.dataKey === 'previousPeriodCost');

    return (
      <div className="rounded-lg border bg-background p-3 shadow-lg">
        <p className="text-xs text-muted-foreground mb-2">{label}</p>
        <div className="space-y-1">
          {current && (
            <div className="flex items-center justify-between gap-4">
              <span className="text-xs font-medium">Current:</span>
              <span className="text-sm font-bold">{formatCurrency(current.value as number)}</span>
            </div>
          )}
          {previous && previous.value !== undefined && (
            <div className="flex items-center justify-between gap-4">
              <span className="text-xs font-medium text-muted-foreground">Previous:</span>
              <span className="text-xs text-muted-foreground">
                {formatCurrency(previous.value as number)}
              </span>
            </div>
          )}
          {current && previous && previous.value !== undefined && (
            <div className="flex items-center justify-between gap-4 pt-1 border-t">
              <span className="text-xs font-medium">Change:</span>
              <span
                className={cn(
                  'text-xs font-medium',
                  (current.value as number) > (previous.value as number)
                    ? 'text-red-500'
                    : (current.value as number) < (previous.value as number)
                    ? 'text-green-500'
                    : 'text-muted-foreground'
                )}
              >
                {((((current.value as number) - (previous.value as number)) /
                  (previous.value as number)) *
                  100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }
  return null;
};

export function CostTrendsChart({
  data,
  title = 'Cost Trends',
  description = 'Track your spending over time',
  showComparison = true,
  defaultTimeRange = '30d',
  height = 350,
  className,
}: CostTrendsChartProps) {
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>(defaultTimeRange);
  const [chartType, setChartType] = useState<'line' | 'area'>('area');

  // Filter data based on selected time range
  const filteredData = useMemo(() => {
    const now = new Date();
    const ranges: Record<TimeRange, number> = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '1y': 365,
    };

    const daysToFilter = ranges[selectedTimeRange];
    const cutoffDate = new Date(now.getTime() - daysToFilter * 24 * 60 * 60 * 1000);

    return data
      .filter(item => new Date(item.date) >= cutoffDate)
      .map(item => ({
        ...item,
        date: new Date(item.date).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: selectedTimeRange === '1y' ? 'numeric' : undefined,
        }),
      }));
  }, [data, selectedTimeRange]);

  // Calculate statistics
  const statistics = useMemo(() => {
    if (filteredData.length === 0) {
      return {
        total: 0,
        average: 0,
        trend: 'stable' as const,
        trendPercentage: 0,
        min: 0,
        max: 0,
      };
    }

    const costs = filteredData.map(d => d.cost);
    const total = costs.reduce((sum, cost) => sum + cost, 0);
    const average = total / costs.length;
    const min = Math.min(...costs);
    const max = Math.max(...costs);

    // Calculate trend (compare first half to second half)
    const midpoint = Math.floor(costs.length / 2);
    const firstHalf = costs.slice(0, midpoint);
    const secondHalf = costs.slice(midpoint);

    const firstAvg = firstHalf.reduce((sum, c) => sum + c, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, c) => sum + c, 0) / secondHalf.length;

    const trendPercentage = firstAvg > 0 ? ((secondAvg - firstAvg) / firstAvg) * 100 : 0;
    const trend =
      Math.abs(trendPercentage) < 5
        ? ('stable' as const)
        : trendPercentage > 0
        ? ('up' as const)
        : ('down' as const);

    return {
      total,
      average,
      trend,
      trendPercentage: Math.abs(trendPercentage),
      min,
      max,
    };
  }, [filteredData]);

  const getTrendIcon = () => {
    switch (statistics.trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4" />;
      case 'down':
        return <TrendingDown className="h-4 w-4" />;
      default:
        return <Minus className="h-4 w-4" />;
    }
  };

  const getTrendColor = () => {
    switch (statistics.trend) {
      case 'up':
        return 'text-red-500';
      case 'down':
        return 'text-green-500';
      default:
        return 'text-muted-foreground';
    }
  };

  const ChartComponent = chartType === 'area' ? AreaChart : LineChart;
  const _DataComponent = chartType === 'area' ? Area : Line;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex gap-1 border rounded-lg p-1">
              <Button
                variant={chartType === 'line' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setChartType('line')}
                className="h-7 px-2"
              >
                Line
              </Button>
              <Button
                variant={chartType === 'area' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setChartType('area')}
                className="h-7 px-2"
              >
                Area
              </Button>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Total</p>
            <p className="text-lg font-bold">{formatCurrency(statistics.total)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Average</p>
            <p className="text-lg font-bold">{formatCurrency(statistics.average)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Range</p>
            <p className="text-lg font-bold">
              {formatCurrency(statistics.min)} - {formatCurrency(statistics.max)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Trend</p>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className={cn('gap-1', getTrendColor())}>
                {getTrendIcon()}
                {statistics.trendPercentage.toFixed(1)}%
              </Badge>
            </div>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2 pt-4 border-t">
          {(Object.keys(timeRangeLabels) as TimeRange[]).map(range => (
            <Button
              key={range}
              variant={selectedTimeRange === range ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedTimeRange(range)}
              className="text-xs"
            >
              {timeRangeLabels[range]}
            </Button>
          ))}
        </div>
      </CardHeader>

      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <ChartComponent data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
            <XAxis
              dataKey="date"
              stroke="hsl(var(--muted-foreground))"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={value => `$${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            {showComparison && (
              <Legend
                wrapperStyle={{ fontSize: '12px' }}
                iconType="line"
              />
            )}
            {chartType === 'area' && <Area type="monotone" dataKey="cost" name="Current Period" stroke="hsl(var(--primary))" fill="hsl(var(--primary))" fillOpacity={0.2} strokeWidth={2} />}
            {chartType === 'line' && <Line type="monotone" dataKey="cost" name="Current Period" stroke="hsl(var(--primary))" strokeWidth={2} />}
            {showComparison && chartType === 'area' && <Area type="monotone" dataKey="previousPeriodCost" name="Previous Period" stroke="hsl(var(--muted-foreground))" fill="hsl(var(--muted-foreground))" fillOpacity={0.1} strokeWidth={1.5} strokeDasharray="5 5" />}
            {showComparison && chartType === 'line' && <Line type="monotone" dataKey="previousPeriodCost" name="Previous Period" stroke="hsl(var(--muted-foreground))" strokeWidth={1.5} strokeDasharray="5 5" />}
          </ChartComponent>
        </ResponsiveContainer>

        {filteredData.length === 0 && (
          <div className="flex items-center justify-center h-[350px]">
            <p className="text-sm text-muted-foreground">No data available for selected period</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
