"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Loader2,
  MinusCircle,
  XCircle,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { DeploymentStatus } from "@/lib/types"

export interface StatusBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  status: DeploymentStatus | string
  showIcon?: boolean
  animated?: boolean
  size?: "sm" | "md" | "lg"
}

const STATUS_CONFIG: Record<
  string,
  {
    label: string
    variant: "default" | "secondary" | "destructive" | "outline"
    className: string
    icon: React.ComponentType<{ className?: string }>
  }
> = {
  pending: {
    label: "Pending",
    variant: "secondary",
    className: "bg-gray-100 text-gray-800 border-gray-300",
    icon: Clock,
  },
  building: {
    label: "Building",
    variant: "default",
    className: "bg-blue-100 text-blue-800 border-blue-300",
    icon: Loader2,
  },
  deploying: {
    label: "Deploying",
    variant: "default",
    className: "bg-yellow-100 text-yellow-800 border-yellow-300",
    icon: Loader2,
  },
  running: {
    label: "Running",
    variant: "default",
    className: "bg-green-100 text-green-800 border-green-300",
    icon: CheckCircle,
  },
  deployed: {
    label: "Deployed",
    variant: "default",
    className: "bg-green-100 text-green-800 border-green-300",
    icon: CheckCircle,
  },
  failed: {
    label: "Failed",
    variant: "destructive",
    className: "bg-red-100 text-red-800 border-red-300",
    icon: XCircle,
  },
  error: {
    label: "Error",
    variant: "destructive",
    className: "bg-red-100 text-red-800 border-red-300",
    icon: AlertCircle,
  },
  terminated: {
    label: "Terminated",
    variant: "secondary",
    className: "bg-gray-100 text-gray-800 border-gray-300",
    icon: MinusCircle,
  },
  online: {
    label: "Online",
    variant: "default",
    className: "bg-green-100 text-green-800 border-green-300",
    icon: Activity,
  },
  offline: {
    label: "Offline",
    variant: "secondary",
    className: "bg-gray-100 text-gray-800 border-gray-300",
    icon: MinusCircle,
  },
  degraded: {
    label: "Degraded",
    variant: "default",
    className: "bg-orange-100 text-orange-800 border-orange-300",
    icon: AlertCircle,
  },
}

const SIZE_CONFIG = {
  sm: {
    badge: "text-xs px-2 py-0.5",
    icon: "h-3 w-3",
  },
  md: {
    badge: "text-sm px-2.5 py-1",
    icon: "h-4 w-4",
  },
  lg: {
    badge: "text-base px-3 py-1.5",
    icon: "h-5 w-5",
  },
}

export function StatusBadge({
  status,
  showIcon = true,
  animated = true,
  size = "md",
  className,
  ...props
}: StatusBadgeProps) {
  const normalizedStatus = status.toLowerCase()
  const config = STATUS_CONFIG[normalizedStatus] || {
    label: status,
    variant: "outline" as const,
    className: "bg-gray-100 text-gray-800 border-gray-300",
    icon: Activity,
  }

  const Icon = config.icon
  const sizeConfig = SIZE_CONFIG[size]

  const isAnimated =
    animated &&
    (normalizedStatus === "building" ||
      normalizedStatus === "deploying" ||
      normalizedStatus === "pending")

  return (
    <Badge
      variant={config.variant}
      className={cn(
        config.className,
        sizeConfig.badge,
        "inline-flex items-center gap-1.5 font-medium border",
        className
      )}
      {...props}
    >
      {showIcon && (
        <Icon
          className={cn(
            sizeConfig.icon,
            isAnimated && "animate-spin"
          )}
        />
      )}
      <span>{config.label}</span>
    </Badge>
  )
}
