"use client"

import * as React from "react"
import { Button, ButtonProps } from "@/components/ui/button"
import { Loader2, Rocket, Check, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

export interface DeployButtonProps extends Omit<ButtonProps, "onClick"> {
  onClick?: () => void | Promise<void>
  status?: "idle" | "loading" | "success" | "error"
  successMessage?: string
  errorMessage?: string
  loadingMessage?: string
}

export function DeployButton({
  children = "Deploy",
  onClick,
  status: controlledStatus,
  successMessage = "Deployed!",
  errorMessage = "Failed",
  loadingMessage = "Deploying...",
  className,
  disabled,
  ...props
}: DeployButtonProps) {
  const [internalStatus, setInternalStatus] = React.useState<
    "idle" | "loading" | "success" | "error"
  >("idle")

  const status = controlledStatus ?? internalStatus

  const handleClick = React.useCallback(async () => {
    if (onClick && !controlledStatus) {
      setInternalStatus("loading")
      try {
        await onClick()
        setInternalStatus("success")
        setTimeout(() => setInternalStatus("idle"), 2000)
      } catch (_error) {
        setInternalStatus("error")
        setTimeout(() => setInternalStatus("idle"), 3000)
      }
    } else if (onClick) {
      onClick()
    }
  }, [onClick, controlledStatus])

  const getIcon = () => {
    switch (status) {
      case "loading":
        return <Loader2 className="h-4 w-4 animate-spin" />
      case "success":
        return <Check className="h-4 w-4" />
      case "error":
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Rocket className="h-4 w-4" />
    }
  }

  const getMessage = () => {
    switch (status) {
      case "loading":
        return loadingMessage
      case "success":
        return successMessage
      case "error":
        return errorMessage
      default:
        return children
    }
  }

  const getVariant = (): ButtonProps["variant"] => {
    switch (status) {
      case "success":
        return "default"
      case "error":
        return "destructive"
      default:
        return props.variant ?? "default"
    }
  }

  return (
    <Button
      {...props}
      variant={getVariant()}
      onClick={handleClick}
      disabled={disabled || status === "loading"}
      className={cn("gap-2", className)}
    >
      {getIcon()}
      {getMessage()}
    </Button>
  )
}
