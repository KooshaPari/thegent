"use client"

import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface ResourceGaugeProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  value: number
  max?: number
  description?: string
  size?: "sm" | "md" | "lg"
  showPercentage?: boolean
  showValue?: boolean
  valueFormatter?: (value: number) => string
  color?: string
  warningThreshold?: number
  criticalThreshold?: number
}

export function ResourceGauge({
  title,
  value,
  max = 100,
  description,
  size = "md",
  showPercentage = true,
  showValue = false,
  valueFormatter,
  color,
  warningThreshold = 70,
  criticalThreshold = 90,
  className,
  ...props
}: ResourceGaugeProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  const sizes = {
    sm: { radius: 50, strokeWidth: 8, fontSize: "text-xl" },
    md: { radius: 70, strokeWidth: 10, fontSize: "text-2xl" },
    lg: { radius: 90, strokeWidth: 12, fontSize: "text-3xl" },
  }

  const { radius, strokeWidth, fontSize } = sizes[size]
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  const getColor = () => {
    if (color) return color

    if (percentage >= criticalThreshold) {
      return "#ef4444" // red-500
    } else if (percentage >= warningThreshold) {
      return "#f59e0b" // yellow-500
    } else {
      return "#10b981" // green-500
    }
  }

  const getBackgroundColor = () => {
    if (percentage >= criticalThreshold) {
      return "#fee2e2" // red-100
    } else if (percentage >= warningThreshold) {
      return "#fef3c7" // yellow-100
    } else {
      return "#d1fae5" // green-100
    }
  }

  const svgSize = (radius + strokeWidth) * 2

  return (
    <Card className={cn("", className)} {...props}>
      {(title || description) && (
        <CardHeader className="pb-2">
          {title && <CardTitle className="text-sm font-medium">{title}</CardTitle>}
          {description && <CardDescription className="text-xs">{description}</CardDescription>}
        </CardHeader>
      )}
      <CardContent className="flex flex-col items-center justify-center pt-4 pb-6">
        <div className="relative" style={{ width: svgSize, height: svgSize }}>
          <svg
            width={svgSize}
            height={svgSize}
            viewBox={`0 0 ${svgSize} ${svgSize}`}
            className="transform -rotate-90"
          >
            {/* Background circle */}
            <circle
              cx={svgSize / 2}
              cy={svgSize / 2}
              r={radius}
              fill="none"
              stroke={getBackgroundColor()}
              strokeWidth={strokeWidth}
            />
            {/* Progress circle */}
            <circle
              cx={svgSize / 2}
              cy={svgSize / 2}
              r={radius}
              fill="none"
              stroke={getColor()}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-500 ease-in-out"
            />
          </svg>

          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {showPercentage && (
              <div className={cn("font-bold", fontSize)} style={{ color: getColor() }}>
                {percentage.toFixed(1)}%
              </div>
            )}
            {showValue && (
              <div className="text-xs text-muted-foreground mt-1">
                {valueFormatter ? valueFormatter(value) : value}
                {max !== 100 && ` / ${valueFormatter ? valueFormatter(max) : max}`}
              </div>
            )}
          </div>
        </div>

        {(showValue || description) && !description && (
          <div className="mt-3 text-center">
            <div className="text-sm text-muted-foreground">
              {valueFormatter ? valueFormatter(value) : value}
              {max !== 100 && ` / ${valueFormatter ? valueFormatter(max) : max}`}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export interface ResourceGaugeGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  gauges: ResourceGaugeProps[]
  columns?: 1 | 2 | 3 | 4
}

export function ResourceGaugeGroup({
  gauges,
  columns = 3,
  className,
  ...props
}: ResourceGaugeGroupProps) {
  const gridClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 md:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
  }

  return (
    <div className={cn("grid gap-4", gridClasses[columns], className)} {...props}>
      {gauges.map((gauge, index) => (
        <ResourceGauge key={index} {...gauge} />
      ))}
    </div>
  )
}
