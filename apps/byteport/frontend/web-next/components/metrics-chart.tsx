"use client"

import * as React from "react"
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
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn, formatDateTime } from "@/lib/utils"
import { MetricDataPoint } from "@/lib/types"

export interface MetricsChartProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  description?: string
  data: MetricDataPoint[]
  dataKey?: string
  type?: "line" | "area"
  color?: string
  valueFormatter?: (value: number) => string
  showGrid?: boolean
  showLegend?: boolean
  height?: number
}

const defaultColors = {
  primary: "hsl(var(--primary))",
  blue: "#3b82f6",
  green: "#10b981",
  yellow: "#f59e0b",
  red: "#ef4444",
  purple: "#8b5cf6",
}

function CustomTooltip({ active, payload, label, valueFormatter }: TooltipProps<any, any> & { valueFormatter?: (value: number) => string }) {
  if (!active || !payload || !payload.length) {
    return null
  }

  return (
    <div className="rounded-lg border bg-background p-2 shadow-md">
      <p className="text-xs font-medium">{formatDateTime(label)}</p>
      {payload.map((entry: any, index: number) => (
        <p key={index} className="text-xs text-muted-foreground">
          {entry.name}: {valueFormatter ? valueFormatter(entry.value) : entry.value}
        </p>
      ))}
    </div>
  )
}

export function MetricsChart({
  title,
  description,
  data,
  dataKey = "value",
  type = "line",
  color = defaultColors.primary,
  valueFormatter,
  showGrid = true,
  showLegend = false,
  height = 300,
  className,
  ...props
}: MetricsChartProps) {
  const chartData = React.useMemo(
    () =>
      data.map((point) => ({
        timestamp: point.timestamp,
        [dataKey]: point.value,
      })),
    [data, dataKey]
  )

  const Chart = type === "area" ? AreaChart : LineChart
  const _DataComponent = type === "area" ? Area : Line

  return (
    <Card className={cn("", className)} {...props}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle className="text-base">{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <Chart data={chartData}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />}
            <XAxis
              dataKey="timestamp"
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getHours()}:${date.getMinutes().toString().padStart(2, "0")}`
              }}
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
            />
            <YAxis
              tickFormatter={(value) =>
                valueFormatter ? valueFormatter(value) : value.toString()
              }
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
            />
            <Tooltip
              content={<CustomTooltip valueFormatter={valueFormatter} />}
            />
            {showLegend && <Legend />}
            {type === "area" && <Area type="monotone" dataKey={dataKey} stroke={color} fill={color} fillOpacity={0.2} strokeWidth={2} dot={false} />}
            {type === "line" && <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />}
          </Chart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export interface MultiMetricsChartProps extends Omit<MetricsChartProps, "data" | "dataKey"> {
  datasets: Array<{
    label: string
    data: MetricDataPoint[]
    color?: string
  }>
}

export function MultiMetricsChart({
  title,
  description,
  datasets,
  type = "line",
  valueFormatter,
  showGrid = true,
  showLegend = true,
  height = 300,
  className,
  ...props
}: MultiMetricsChartProps) {
  const chartData = React.useMemo(() => {
    if (!datasets.length) return []

    const timestamps = new Set<string>()
    datasets.forEach((dataset) => {
      dataset.data.forEach((point) => timestamps.add(point.timestamp))
    })

    return Array.from(timestamps)
      .sort()
      .map((timestamp) => {
        const point: any = { timestamp }
        datasets.forEach((dataset) => {
          const dataPoint = dataset.data.find((p) => p.timestamp === timestamp)
          point[dataset.label] = dataPoint?.value || 0
        })
        return point
      })
  }, [datasets])

  const Chart = type === "area" ? AreaChart : LineChart
  const _DataComponent = type === "area" ? Area : Line
  const colors = [
    defaultColors.blue,
    defaultColors.green,
    defaultColors.yellow,
    defaultColors.red,
    defaultColors.purple,
  ]

  return (
    <Card className={cn("", className)} {...props}>
      {(title || description) && (
        <CardHeader>
          {title && <CardTitle className="text-base">{title}</CardTitle>}
          {description && <CardDescription>{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <Chart data={chartData}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />}
            <XAxis
              dataKey="timestamp"
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getHours()}:${date.getMinutes().toString().padStart(2, "0")}`
              }}
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
            />
            <YAxis
              tickFormatter={(value) =>
                valueFormatter ? valueFormatter(value) : value.toString()
              }
              className="text-xs"
              stroke="hsl(var(--muted-foreground))"
            />
            <Tooltip content={<CustomTooltip valueFormatter={valueFormatter} />} />
            {showLegend && <Legend />}
            {type === "area" && datasets.map((dataset, index) => (
              <Area
                key={dataset.label}
                type="monotone"
                dataKey={dataset.label}
                stroke={dataset.color || colors[index % colors.length]}
                fill={dataset.color || colors[index % colors.length]}
                fillOpacity={0.2}
                strokeWidth={2}
                dot={false}
              />
            ))}
            {type === "line" && datasets.map((dataset, index) => (
              <Line
                key={dataset.label}
                type="monotone"
                dataKey={dataset.label}
                stroke={dataset.color || colors[index % colors.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </Chart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
