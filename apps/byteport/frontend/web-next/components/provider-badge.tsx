"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { StatusIndicator } from "@/components/status-indicator"
import { cn } from "@/lib/utils"
import { ProviderName, ProviderStatus } from "@/lib/types"

export interface ProviderBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  provider: ProviderName
  status?: ProviderStatus
  showStatus?: boolean
  size?: "sm" | "md" | "lg"
}

const providerInfo: Record<
  ProviderName,
  { name: string; color: string; icon?: string }
> = {
  vercel: { name: "Vercel", color: "bg-black dark:bg-white text-white dark:text-black" },
  netlify: { name: "Netlify", color: "bg-[#00C7B7] text-white" },
  render: { name: "Render", color: "bg-[#46E3B7] text-black" },
  railway: { name: "Railway", color: "bg-black text-white" },
  fly: { name: "Fly.io", color: "bg-[#7B3FF2] text-white" },
  aws: { name: "AWS", color: "bg-[#FF9900] text-black" },
  gcp: { name: "GCP", color: "bg-[#4285F4] text-white" },
  azure: { name: "Azure", color: "bg-[#0078D4] text-white" },
  supabase: { name: "Supabase", color: "bg-[#3ECF8E] text-black" },
}

const sizeClasses = {
  sm: "text-xs px-2 py-0.5",
  md: "text-sm px-2.5 py-1",
  lg: "text-base px-3 py-1.5",
}

export function ProviderBadge({
  provider,
  status = "connected",
  showStatus = false,
  size = "md",
  className,
  ...props
}: ProviderBadgeProps) {
  const info = providerInfo[provider]

  return (
    <div className={cn("inline-flex items-center gap-2", className)} {...props}>
      <Badge
        variant="secondary"
        className={cn(
          "font-medium",
          sizeClasses[size],
          info.color,
          "border-0"
        )}
      >
        {info.name}
      </Badge>
      {showStatus && (
        <StatusIndicator
          status={status === "connected" ? "online" : status === "disconnected" ? "offline" : "degraded"}
          size={size === "sm" ? "sm" : "md"}
        />
      )}
    </div>
  )
}
