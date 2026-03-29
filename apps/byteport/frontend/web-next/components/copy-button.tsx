"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { Check, Copy } from "lucide-react"
import { cn } from "@/lib/utils"

export interface CopyButtonProps extends React.HTMLAttributes<HTMLButtonElement> {
  value: string
  variant?: "default" | "outline" | "ghost" | "link" | "secondary"
  size?: "default" | "sm" | "lg" | "icon"
  showIcon?: boolean
  showText?: boolean
  successDuration?: number
  onCopy?: () => void
}

export function CopyButton({
  value,
  variant = "ghost",
  size = "icon",
  showIcon = true,
  showText = false,
  successDuration = 2000,
  onCopy,
  className,
  ...props
}: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = React.useCallback(async () => {
    if (!value || copied) return

    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      onCopy?.()

      setTimeout(() => {
        setCopied(false)
      }, successDuration)
    } catch (error) {
      console.error("Failed to copy:", error)
    }
  }, [value, copied, successDuration, onCopy])

  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      onClick={handleCopy}
      className={cn("relative", className)}
      {...props}
    >
      {showIcon && (
        <>
          <Copy
            className={cn(
              "transition-all",
              size === "icon" ? "h-4 w-4" : "h-3.5 w-3.5",
              copied && "scale-0 opacity-0"
            )}
          />
          <Check
            className={cn(
              "absolute transition-all",
              size === "icon" ? "h-4 w-4" : "h-3.5 w-3.5",
              copied ? "scale-100 opacity-100" : "scale-0 opacity-0"
            )}
          />
        </>
      )}
      {showText && (
        <span className={cn(showIcon && "ml-2")}>
          {copied ? "Copied!" : "Copy"}
        </span>
      )}
      <span className="sr-only">{copied ? "Copied to clipboard" : "Copy to clipboard"}</span>
    </Button>
  )
}

export interface CopyCodeBlockProps extends React.HTMLAttributes<HTMLDivElement> {
  code: string
  language?: string
  showLineNumbers?: boolean
}

export function CopyCodeBlock({
  code,
  language,
  showLineNumbers = false,
  className,
  ...props
}: CopyCodeBlockProps) {
  const lines = code.split("\n")

  return (
    <div className={cn("group relative", className)} {...props}>
      <div className="absolute right-2 top-2 opacity-0 transition-opacity group-hover:opacity-100">
        <CopyButton value={code} />
      </div>

      <div className="overflow-x-auto rounded-lg bg-muted p-4">
        {language && (
          <div className="mb-2 text-xs font-medium text-muted-foreground">
            {language}
          </div>
        )}
        <pre className="text-sm">
          <code>
            {showLineNumbers
              ? lines.map((line, i) => (
                  <div key={i} className="flex">
                    <span className="mr-4 select-none text-muted-foreground">
                      {(i + 1).toString().padStart(2, "0")}
                    </span>
                    <span>{line}</span>
                  </div>
                ))
              : code}
          </code>
        </pre>
      </div>
    </div>
  )
}

export interface CopyTextProps extends React.HTMLAttributes<HTMLDivElement> {
  text: string
  truncate?: boolean
  maxLength?: number
  variant?: "default" | "inline"
}

export function CopyText({
  text,
  truncate = false,
  maxLength = 50,
  variant = "default",
  className,
  ...props
}: CopyTextProps) {
  const displayText = truncate && text.length > maxLength ? text.slice(0, maxLength) + "..." : text

  if (variant === "inline") {
    return (
      <div className={cn("group inline-flex items-center gap-1", className)} {...props}>
        <code className="rounded bg-muted px-1.5 py-0.5 text-sm font-mono">
          {displayText}
        </code>
        <CopyButton
          value={text}
          size="icon"
          className="h-6 w-6 opacity-0 transition-opacity group-hover:opacity-100"
        />
      </div>
    )
  }

  return (
    <div
      className={cn(
        "group relative flex items-center justify-between rounded-lg border bg-muted/50 px-3 py-2",
        className
      )}
      {...props}
    >
      <code className="flex-1 truncate text-sm font-mono">{displayText}</code>
      <CopyButton value={text} />
    </div>
  )
}
