"use client"

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, TrendingDown, Minus, LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  value: string | number
  description?: string
  icon?: LucideIcon
  trend?: {
    value: number
    label?: string
    isPositive?: boolean
  }
  status?: "success" | "warning" | "error" | "info"
  loading?: boolean
  suffix?: string
  prefix?: string
}

const statusColors = {
  success: "text-green-600 bg-green-50 border-green-200",
  warning: "text-yellow-600 bg-yellow-50 border-yellow-200",
  error: "text-red-600 bg-red-50 border-red-200",
  info: "text-blue-600 bg-blue-50 border-blue-200",
}

export function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  status,
  loading = false,
  suffix,
  prefix,
  className,
  ...props
}: MetricCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null

    const trendValue = trend.value
    const isPositive = trend.isPositive !== undefined ? trend.isPositive : trendValue > 0

    if (trendValue === 0) {
      return <Minus className="h-4 w-4 text-gray-400" />
    }

    if (trendValue > 0) {
      return <TrendingUp className={cn("h-4 w-4", isPositive ? "text-green-500" : "text-red-500")} />
    }

    return <TrendingDown className={cn("h-4 w-4", isPositive ? "text-red-500" : "text-green-500")} />
  }

  const getTrendColor = () => {
    if (!trend) return ""

    const trendValue = trend.value
    const isPositive = trend.isPositive !== undefined ? trend.isPositive : trendValue > 0

    if (trendValue === 0) return "text-gray-500"
    if (trendValue > 0) return isPositive ? "text-green-600" : "text-red-600"
    return isPositive ? "text-red-600" : "text-green-600"
  }

  return (
    <Card
      className={cn(
        "transition-all duration-200 hover:shadow-md",
        status && statusColors[status],
        className
      )}
      {...props}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <div className="h-8 w-24 bg-muted animate-pulse rounded" />
            {description && <div className="h-4 w-32 bg-muted animate-pulse rounded" />}
          </div>
        ) : (
          <>
            <div className="text-2xl font-bold">
              {prefix}
              {value}
              {suffix}
            </div>

            {(description || trend) && (
              <div className="flex items-center gap-2 mt-2">
                {trend && (
                  <div className={cn("flex items-center gap-1 text-xs font-medium", getTrendColor())}>
                    {getTrendIcon()}
                    <span>
                      {Math.abs(trend.value)}%
                      {trend.label && ` ${trend.label}`}
                    </span>
                  </div>
                )}

                {description && (
                  <p className={cn("text-xs text-muted-foreground", trend && "ml-auto")}>
                    {description}
                  </p>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}

export interface MetricGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  metrics: MetricCardProps[]
  columns?: 1 | 2 | 3 | 4
}

export function MetricGroup({ metrics, columns = 4, className, ...props }: MetricGroupProps) {
  const gridClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 md:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
  }

  return (
    <div className={cn("grid gap-4", gridClasses[columns], className)} {...props}>
      {metrics.map((metric, index) => (
        <MetricCard key={index} {...metric} />
      ))}
    </div>
  )
}
