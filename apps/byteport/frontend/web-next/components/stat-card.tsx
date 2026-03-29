"use client"

import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export interface StatCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  value: string | number
  description?: string
  icon?: LucideIcon
  iconClassName?: string
  change?: {
    value: number
    label?: string
  }
  progress?: number
  variant?: "default" | "success" | "warning" | "error" | "info"
  compact?: boolean
}

const variantStyles = {
  default: {
    icon: "text-muted-foreground",
    card: "",
  },
  success: {
    icon: "text-green-600",
    card: "border-green-200",
  },
  warning: {
    icon: "text-yellow-600",
    card: "border-yellow-200",
  },
  error: {
    icon: "text-red-600",
    card: "border-red-200",
  },
  info: {
    icon: "text-blue-600",
    card: "border-blue-200",
  },
}

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  iconClassName,
  change,
  progress,
  variant = "default",
  compact = false,
  className,
  ...props
}: StatCardProps) {
  const styles = variantStyles[variant]

  const getChangeColor = () => {
    if (!change) return ""
    return change.value > 0 ? "text-green-600" : change.value < 0 ? "text-red-600" : "text-gray-500"
  }

  const getChangeSymbol = () => {
    if (!change) return ""
    return change.value > 0 ? "+" : ""
  }

  if (compact) {
    return (
      <div className={cn("flex items-center gap-4 rounded-lg border p-4", styles.card, className)} {...props}>
        {Icon && (
          <div className={cn("rounded-full p-2 bg-muted", iconClassName)}>
            <Icon className={cn("h-5 w-5", styles.icon)} />
          </div>
        )}
        <div className="flex-1 space-y-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-2xl font-bold">{value}</p>
            {change && (
              <span className={cn("text-xs font-medium", getChangeColor())}>
                {getChangeSymbol()}{change.value}%
              </span>
            )}
          </div>
          {description && <p className="text-xs text-muted-foreground">{description}</p>}
        </div>
      </div>
    )
  }

  return (
    <Card className={cn("transition-shadow hover:shadow-md", styles.card, className)} {...props}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && <Icon className={cn("h-4 w-4", styles.icon, iconClassName)} />}
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-bold">{value}</div>
          {change && (
            <div className={cn("flex items-center text-xs font-medium", getChangeColor())}>
              <span>
                {getChangeSymbol()}{change.value}%
              </span>
              {change.label && <span className="ml-1 text-muted-foreground">{change.label}</span>}
            </div>
          )}
        </div>

        {progress !== undefined && (
          <div className="space-y-1">
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-muted-foreground text-right">{progress}%</p>
          </div>
        )}

        {description && !progress && (
          <CardDescription className="text-xs">{description}</CardDescription>
        )}
      </CardContent>
    </Card>
  )
}

export interface StatGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  stats: StatCardProps[]
  columns?: 1 | 2 | 3 | 4
  compact?: boolean
}

export function StatGroup({ stats, columns = 4, compact = false, className, ...props }: StatGroupProps) {
  const gridClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 md:grid-cols-2",
    3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
  }

  return (
    <div className={cn("grid gap-4", gridClasses[columns], className)} {...props}>
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} compact={compact} />
      ))}
    </div>
  )
}
