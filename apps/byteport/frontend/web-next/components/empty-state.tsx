"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { LucideIcon, FileQuestion } from "lucide-react"
import { cn } from "@/lib/utils"

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: LucideIcon
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
    variant?: "default" | "outline" | "secondary" | "ghost" | "link"
  }
  secondaryAction?: {
    label: string
    onClick: () => void
    variant?: "default" | "outline" | "secondary" | "ghost" | "link"
  }
  variant?: "default" | "minimal" | "card"
}

export function EmptyState({
  icon: Icon = FileQuestion,
  title,
  description,
  action,
  secondaryAction,
  variant = "default",
  className,
  ...props
}: EmptyStateProps) {
  const content = (
    <>
      <div
        className={cn(
          "mx-auto flex items-center justify-center rounded-full",
          variant === "minimal" ? "h-12 w-12 bg-muted" : "h-16 w-16 bg-muted/50"
        )}
      >
        <Icon
          className={cn(
            "text-muted-foreground",
            variant === "minimal" ? "h-6 w-6" : "h-8 w-8"
          )}
        />
      </div>

      <div className="space-y-2 text-center">
        <h3 className={cn("font-semibold", variant === "minimal" ? "text-base" : "text-lg")}>
          {title}
        </h3>
        {description && (
          <p className={cn("text-muted-foreground", variant === "minimal" ? "text-xs" : "text-sm")}>
            {description}
          </p>
        )}
      </div>

      {(action || secondaryAction) && (
        <div className="flex items-center justify-center gap-2">
          {action && (
            <Button onClick={action.onClick} variant={action.variant || "default"} size={variant === "minimal" ? "sm" : "default"}>
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button onClick={secondaryAction.onClick} variant={secondaryAction.variant || "outline"} size={variant === "minimal" ? "sm" : "default"}>
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}
    </>
  )

  if (variant === "card") {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-4 rounded-lg border border-dashed bg-muted/20 p-8 text-center",
          className
        )}
        {...props}
      >
        {content}
      </div>
    )
  }

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-4 py-8 text-center",
        variant === "minimal" && "py-6",
        className
      )}
      {...props}
    >
      {content}
    </div>
  )
}

export interface EmptyStateListProps extends React.HTMLAttributes<HTMLDivElement> {
  items: {
    icon?: LucideIcon
    title: string
    description: string
  }[]
  title?: string
  description?: string
}

export function EmptyStateList({
  items,
  title = "Getting Started",
  description,
  className,
  ...props
}: EmptyStateListProps) {
  return (
    <div className={cn("space-y-6", className)} {...props}>
      {(title || description) && (
        <div className="space-y-2 text-center">
          {title && <h3 className="text-lg font-semibold">{title}</h3>}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((item, index) => {
          const ItemIcon = item.icon || FileQuestion
          return (
            <div
              key={index}
              className="flex flex-col items-center gap-3 rounded-lg border p-6 text-center transition-colors hover:bg-muted/50"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <ItemIcon className="h-6 w-6 text-primary" />
              </div>
              <div className="space-y-1">
                <h4 className="font-medium">{item.title}</h4>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
