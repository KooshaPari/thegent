"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { DeploymentStatus } from "@/lib/types"

export interface StatusIndicatorProps extends React.HTMLAttributes<HTMLDivElement> {
  status: DeploymentStatus | "online" | "offline" | "degraded"
  size?: "sm" | "md" | "lg"
  showLabel?: boolean
  pulsing?: boolean
}

const statusColors = {
  // Deployment statuses
  pending: "bg-yellow-500",
  building: "bg-blue-500",
  deploying: "bg-blue-500",
  running: "bg-green-500",
  failed: "bg-red-500",
  terminated: "bg-gray-500",
  // Service statuses
  online: "bg-green-500",
  offline: "bg-gray-500",
  degraded: "bg-yellow-500",
} as const

const statusLabels = {
  pending: "Pending",
  building: "Building",
  deploying: "Deploying",
  running: "Running",
  failed: "Failed",
  terminated: "Terminated",
  online: "Online",
  offline: "Offline",
  degraded: "Degraded",
} as const

const sizeClasses = {
  sm: "h-2 w-2",
  md: "h-3 w-3",
  lg: "h-4 w-4",
}

export function StatusIndicator({
  status,
  size = "md",
  showLabel = false,
  pulsing = false,
  className,
  ...props
}: StatusIndicatorProps) {
  const shouldPulse = pulsing || ["building", "deploying", "pending"].includes(status)

  return (
    <div className={cn("flex items-center gap-2", className)} {...props}>
      <div className="relative">
        <div
          className={cn(
            "rounded-full",
            sizeClasses[size],
            statusColors[status as keyof typeof statusColors]
          )}
        />
        {shouldPulse && (
          <div
            className={cn(
              "absolute inset-0 animate-ping rounded-full opacity-75",
              sizeClasses[size],
              statusColors[status as keyof typeof statusColors]
            )}
          />
        )}
      </div>
      {showLabel && (
        <span className="text-sm font-medium">
          {statusLabels[status as keyof typeof statusLabels]}
        </span>
      )}
    </div>
  )
}
