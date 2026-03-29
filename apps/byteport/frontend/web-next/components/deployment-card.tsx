"use client"

import * as React from "react"
import { formatDistanceToNow } from "date-fns"
import { ProviderName } from "@/lib/types"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { StatusIndicator } from "@/components/status-indicator"
import { ProviderBadge } from "@/components/provider-badge"
import {
  ExternalLink,
  MoreVertical,
  Play,
  Pause,
  RotateCw,
  Trash2,
  Terminal,
  Settings,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Deployment } from "@/lib/types"

export interface DeploymentCardProps extends React.HTMLAttributes<HTMLDivElement> {
  deployment: Deployment
  onView?: (id: string) => void
  onRestart?: (id: string) => void
  onStop?: (id: string) => void
  onDelete?: (id: string) => void
  onViewLogs?: (id: string) => void
  onSettings?: (id: string) => void
}

export function DeploymentCard({
  deployment,
  onView,
  onRestart,
  onStop,
  onDelete,
  onViewLogs,
  onSettings,
  className,
  ...props
}: DeploymentCardProps) {
  const canStart = ["terminated", "failed"].includes(deployment.status)
  const canStop = ["running", "building", "deploying"].includes(deployment.status)
  const canRestart = deployment.status === "running"

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all hover:shadow-md",
        className
      )}
      {...props}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-1">
            <CardTitle className="flex items-center gap-2">
              {deployment.name}
              <StatusIndicator status={deployment.status} size="sm" />
            </CardTitle>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <ProviderBadge provider={deployment.provider as ProviderName} size="sm" />
              <span className="text-xs">
                {deployment.type.charAt(0).toUpperCase() + deployment.type.slice(1)}
              </span>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canRestart && (
                <DropdownMenuItem onClick={() => onRestart?.(deployment.id)}>
                  <RotateCw className="mr-2 h-4 w-4" />
                  Restart
                </DropdownMenuItem>
              )}
              {canStop && (
                <DropdownMenuItem onClick={() => onStop?.(deployment.id)}>
                  <Pause className="mr-2 h-4 w-4" />
                  Stop
                </DropdownMenuItem>
              )}
              {canStart && (
                <DropdownMenuItem onClick={() => onRestart?.(deployment.id)}>
                  <Play className="mr-2 h-4 w-4" />
                  Start
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={() => onViewLogs?.(deployment.id)}>
                <Terminal className="mr-2 h-4 w-4" />
                View Logs
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onSettings?.(deployment.id)}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => onDelete?.(deployment.id)}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {deployment.url && (
          <div className="flex items-center gap-2">
            <a
              href={deployment.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-sm text-primary hover:underline"
            >
              <ExternalLink className="h-3 w-3" />
              {deployment.url.replace(/^https?:\/\//, "")}
            </a>
          </div>
        )}

        {deployment.framework && (
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {deployment.framework}
            </Badge>
            {deployment.runtime && (
              <Badge variant="outline" className="text-xs">
                {deployment.runtime}
              </Badge>
            )}
          </div>
        )}

        {deployment.error_message && (
          <div className="rounded-md bg-destructive/10 p-2 text-xs text-destructive">
            {deployment.error_message}
          </div>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between border-t pt-4 text-xs text-muted-foreground">
        <span>
          Created {formatDistanceToNow(new Date(deployment.created_at), { addSuffix: true })}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView?.(deployment.id)}
          className="h-8 px-2"
        >
          View Details
        </Button>
      </CardFooter>
    </Card>
  )
}
