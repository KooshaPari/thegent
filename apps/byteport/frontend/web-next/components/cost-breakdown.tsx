"use client"

import * as React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ProviderBadge } from "@/components/provider-badge"
import { cn, formatCost, formatPercentage } from "@/lib/utils"
import { ProviderName } from "@/lib/types"

export interface CostItem {
  id: string
  name: string
  provider?: ProviderName
  cost: number
  category?: "compute" | "storage" | "network" | "additional"
}

export interface CostBreakdownProps extends React.HTMLAttributes<HTMLDivElement> {
  items: CostItem[]
  total: number
  currency?: string
  groupBy?: "provider" | "category" | "none"
  showPercentages?: boolean
}

const categoryColors: Record<string, string> = {
  compute: "bg-blue-500",
  storage: "bg-green-500",
  network: "bg-purple-500",
  additional: "bg-orange-500",
}

const categoryLabels: Record<string, string> = {
  compute: "Compute",
  storage: "Storage",
  network: "Network",
  additional: "Additional",
}

export function CostBreakdown({
  items,
  total,
  currency: _currency = "USD",
  groupBy = "none",
  showPercentages = true,
  className,
  ...props
}: CostBreakdownProps) {
  const sortedItems = React.useMemo(() => {
    return [...items].sort((a, b) => b.cost - a.cost)
  }, [items])

  const groupedItems = React.useMemo(() => {
    if (groupBy === "none") return null

    const groups: Record<string, CostItem[]> = {}
    sortedItems.forEach((item) => {
      const key = groupBy === "provider" ? item.provider || "other" : item.category || "other"
      if (!groups[key]) {
        groups[key] = []
      }
      groups[key].push(item)
    })

    return Object.entries(groups).map(([key, items]) => ({
      key,
      items,
      total: items.reduce((sum, item) => sum + item.cost, 0),
    }))
  }, [sortedItems, groupBy])

  const renderCostItem = (item: CostItem, _index: number) => {
    const percentage = total > 0 ? (item.cost / total) * 100 : 0

    return (
      <div key={item.id} className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <span className="font-medium truncate">{item.name}</span>
            {item.provider && (
              <ProviderBadge provider={item.provider} size="sm" />
            )}
            {item.category && (
              <Badge variant="outline" className="text-xs">
                {categoryLabels[item.category]}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {showPercentages && (
              <span className="text-xs text-muted-foreground">
                {formatPercentage(percentage, 1)}
              </span>
            )}
            <span className="font-semibold">{formatCost(item.cost)}</span>
          </div>
        </div>
        <Progress
          value={percentage}
          className={cn(
            "h-2",
            item.category && `[&>div]:${categoryColors[item.category]}`
          )}
        />
      </div>
    )
  }

  return (
    <Card className={cn("", className)} {...props}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base">Cost Breakdown</CardTitle>
            <CardDescription>Detailed cost analysis</CardDescription>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{formatCost(total)}</p>
            <p className="text-xs text-muted-foreground">Total</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {groupedItems ? (
          groupedItems.map((group) => (
            <div key={group.key} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {groupBy === "provider" && group.key !== "other" ? (
                    <ProviderBadge provider={group.key as ProviderName} />
                  ) : (
                    <h4 className="font-medium capitalize">{group.key}</h4>
                  )}
                </div>
                <span className="text-sm font-semibold">{formatCost(group.total)}</span>
              </div>
              <div className="space-y-3 pl-4">
                {group.items.map((item,  _index) => renderCostItem(item,  _index))}
              </div>
            </div>
          ))
        ) : sortedItems.length > 0 ? (
          <div className="space-y-4">
            {sortedItems.map((item,  _index) => renderCostItem(item,  _index))}
          </div>
        ) : (
          <div className="py-8 text-center text-sm text-muted-foreground">
            No cost data available
          </div>
        )}
      </CardContent>
    </Card>
  )
}
