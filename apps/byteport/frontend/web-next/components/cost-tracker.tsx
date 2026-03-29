"use client"

import * as React from "react"
import { TrendingUp, TrendingDown, Minus, DollarSign } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { cn, formatCost } from "@/lib/utils"

export interface CostTrackerProps extends React.HTMLAttributes<HTMLDivElement> {
  current: number
  budget?: number
  projected?: number
  trend?: "increasing" | "decreasing" | "stable"
  period?: string
  currency?: string
}

export function CostTracker({
  current,
  budget,
  projected,
  trend = "stable",
  period = "this month",
  currency: _currency = "USD",
  className,
  ...props
}: CostTrackerProps) {
  const progressValue = budget ? Math.min((current / budget) * 100, 100) : 0
  const isOverBudget = budget ? current > budget : false
  const isNearLimit = budget ? current > budget * 0.8 : false

  const getTrendIcon = () => {
    switch (trend) {
      case "increasing":
        return <TrendingUp className="h-4 w-4 text-red-500" />
      case "decreasing":
        return <TrendingDown className="h-4 w-4 text-green-500" />
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getTrendColor = () => {
    switch (trend) {
      case "increasing":
        return "text-red-500"
      case "decreasing":
        return "text-green-500"
      default:
        return "text-muted-foreground"
    }
  }

  return (
    <Card className={cn("", className)} {...props}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base">Cost Tracking</CardTitle>
            <CardDescription className="capitalize">{period}</CardDescription>
          </div>
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
            <DollarSign className="h-5 w-5 text-primary" />
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current Cost */}
        <div className="space-y-2">
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold">{formatCost(current)}</span>
            {trend !== "stable" && (
              <div className={cn("flex items-center gap-1 text-sm", getTrendColor())}>
                {getTrendIcon()}
                <span className="capitalize">{trend}</span>
              </div>
            )}
          </div>

          {budget && (
            <>
              <Progress
                value={progressValue}
                className={cn(
                  "h-2",
                  isOverBudget && "bg-red-100 [&>div]:bg-red-500",
                  isNearLimit && !isOverBudget && "bg-yellow-100 [&>div]:bg-yellow-500"
                )}
              />
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  {formatCost(budget)} budget
                </span>
                {isOverBudget ? (
                  <Badge variant="destructive" className="text-xs">
                    Over budget
                  </Badge>
                ) : isNearLimit ? (
                  <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-700 text-xs">
                    Near limit
                  </Badge>
                ) : (
                  <span className="text-muted-foreground">
                    {Math.round(progressValue)}% used
                  </span>
                )}
              </div>
            </>
          )}
        </div>

        {/* Projected Cost */}
        {projected !== undefined && (
          <div className="rounded-lg bg-muted p-3 space-y-1">
            <p className="text-xs text-muted-foreground">Projected end of month</p>
            <p className="text-lg font-semibold">{formatCost(projected)}</p>
            {budget && projected > budget && (
              <p className="text-xs text-destructive">
                {formatCost(projected - budget)} over budget
              </p>
            )}
          </div>
        )}

        {/* Budget Status */}
        {budget && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Remaining</span>
            <span
              className={cn(
                "font-medium",
                isOverBudget ? "text-destructive" : "text-green-600"
              )}
            >
              {isOverBudget
                ? `-${formatCost(current - budget)}`
                : formatCost(budget - current)}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
