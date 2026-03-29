'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  TooltipProps
} from 'recharts';
import { formatCurrency } from '@/lib/utils';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export type ChartType = 'line' | 'bar' | 'area';

export interface CostDataPoint {
  date: string;
  cost: number;
  provider?: string;
  label?: string;
}

interface CostChartProps {
  data: CostDataPoint[];
  type?: ChartType;
  title?: string;
  description?: string;
  height?: number;
  showLegend?: boolean;
  dataKey?: string;
  color?: string;
}

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-2 shadow-sm">
        <div className="grid gap-2">
          <div className="flex flex-col">
            <span className="text-[0.70rem] uppercase text-muted-foreground">
              {label}
            </span>
            <span className="font-bold text-muted-foreground">
              {formatCurrency(payload[0].value as number)}
            </span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

export function CostChart({
  data,
  type = 'line',
  title,
  description,
  height = 300,
  showLegend = false,
  dataKey = 'cost',
  color = 'hsl(var(--primary))'
}: CostChartProps) {
  const chartData = useMemo(() => {
    return data.map((item) => ({
      ...item,
      date: new Date(item.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    }));
  }, [data]);

  const ChartComponent = useMemo(() => {
    switch (type) {
      case 'bar':
        return BarChart;
      case 'area':
        return AreaChart;
      default:
        return LineChart;
    }
  }, [type]);

  const _DataComponent = useMemo(() => {
    switch (type) {
      case 'bar':
        return Bar;
      case 'area':
        return Area;
      default:
        return Line;
    }
  }, [type]);

  const content = (
    <ResponsiveContainer width="100%" height={height}>
      <ChartComponent data={chartData}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="date"
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          stroke="hsl(var(--muted-foreground))"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(value) => `$${value}`}
        />
        <Tooltip content={<CustomTooltip />} />
        {showLegend && <Legend />}
        {type === 'area' && <Area type="monotone" dataKey={dataKey} stroke={color} fill={color} fillOpacity={0.3} strokeWidth={2} />}
        {type === 'line' && <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} />}
        {type === 'bar' && <Bar dataKey={dataKey} fill={color} />}
      </ChartComponent>
    </ResponsiveContainer>
  );

  if (title || description) {
    return (
      <Card>
        <CardHeader>
          {title && <CardTitle>{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
        <CardContent>{content}</CardContent>
      </Card>
    );
  }

  return content;
}
