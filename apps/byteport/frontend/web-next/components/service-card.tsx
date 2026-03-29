"use client"

import * as React from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { StatusIndicator } from "@/components/status-indicator"
import {
  Activity,
  Cpu,
  HardDrive,
  MoreVertical,
  Play,
  Pause,
  RotateCw,
  Settings,
  Trash2,
} from "lucide-react"
import { cn, formatPercentage } from "@/lib/utils"

export interface ServiceCardProps extends React.HTMLAttributes<HTMLDivElement> {
  service: {
    id: string
    name: string
    status: "online" | "offline" | "degraded"
    type: string
    cpu_usage?: number
    memory_usage?: number
    disk_usage?: number
    uptime?: string
    requests_per_minute?: number
  }
  onStart?: (id: string) => void
  onStop?: (id: string) => void
  onRestart?: (id: string) => void
  onSettings?: (id: string) => void
  onDelete?: (id: string) => void
  onView?: (id: string) => void
}

export function ServiceCard({
  service,
  onStart,
  onStop,
  onRestart,
  onSettings,
  onDelete,
  onView,
  className,
  ...props
}: ServiceCardProps) {
  const canStart = service.status === "offline"
  const canStop = service.status === "online" || service.status === "degraded"

  return (
    <Card className={cn("group hover:shadow-md transition-all", className)} {...props}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              {service.name}
              <StatusIndicator status={service.status} size="sm" pulsing />
            </CardTitle>
            <CardDescription className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {service.type}
              </Badge>
              {service.uptime && (
                <span className="text-xs text-muted-foreground">
                  Uptime: {service.uptime}
                </span>
              )}
            </CardDescription>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {canStop && (
                <>
                  <DropdownMenuItem onClick={() => onRestart?.(service.id)}>
                    <RotateCw className="mr-2 h-4 w-4" />
                    Restart
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onStop?.(service.id)}>
                    <Pause className="mr-2 h-4 w-4" />
                    Stop
                  </DropdownMenuItem>
                </>
              )}
              {canStart && (
                <DropdownMenuItem onClick={() => onStart?.(service.id)}>
                  <Play className="mr-2 h-4 w-4" />
                  Start
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onClick={() => onSettings?.(service.id)}>
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => onDelete?.(service.id)}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Resource Usage */}
        {(service.cpu_usage !== undefined ||
          service.memory_usage !== undefined ||
          service.disk_usage !== undefined) && (
          <div className="space-y-3">
            {service.cpu_usage !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">CPU</span>
                  </div>
                  <span className="font-medium">{formatPercentage(service.cpu_usage, 1)}</span>
                </div>
                <Progress value={service.cpu_usage} className="h-2" />
              </div>
            )}

            {service.memory_usage !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Memory</span>
                  </div>
                  <span className="font-medium">{formatPercentage(service.memory_usage, 1)}</span>
                </div>
                <Progress value={service.memory_usage} className="h-2" />
              </div>
            )}

            {service.disk_usage !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <HardDrive className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Disk</span>
                  </div>
                  <span className="font-medium">{formatPercentage(service.disk_usage, 1)}</span>
                </div>
                <Progress value={service.disk_usage} className="h-2" />
              </div>
            )}
          </div>
        )}

        {/* Metrics */}
        {service.requests_per_minute !== undefined && (
          <div className="flex items-center justify-between rounded-lg bg-muted px-3 py-2 text-sm">
            <span className="text-muted-foreground">Requests/min</span>
            <span className="font-medium">{service.requests_per_minute.toLocaleString()}</span>
          </div>
        )}
      </CardContent>

      <CardFooter className="border-t pt-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView?.(service.id)}
          className="w-full"
        >
          View Details
        </Button>
      </CardFooter>
    </Card>
  )
}
