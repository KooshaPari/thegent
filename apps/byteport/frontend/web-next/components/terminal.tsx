"use client"

import * as React from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"

export interface TerminalProps extends React.HTMLAttributes<HTMLDivElement> {
  lines?: string[]
  prompt?: string
  autoScroll?: boolean
  maxLines?: number
}

// Simple ANSI color parser
function parseAnsiColors(text: string): React.ReactNode[] {
  const colorMap: Record<string, string> = {
    "30": "text-black",
    "31": "text-red-500",
    "32": "text-green-500",
    "33": "text-yellow-500",
    "34": "text-blue-500",
    "35": "text-magenta-500",
    "36": "text-cyan-500",
    "37": "text-white",
    "90": "text-gray-500",
    "91": "text-red-400",
    "92": "text-green-400",
    "93": "text-yellow-400",
    "94": "text-blue-400",
    "95": "text-magenta-400",
    "96": "text-cyan-400",
    "97": "text-gray-200",
  }

  // Strip ANSI codes and create simple colored output
  const ansiRegex = /\x1b\[([0-9;]+)m/g
  const parts: React.ReactNode[] = []
  let lastIndex = 0
  let currentColor = ""
  let match

  while ((match = ansiRegex.exec(text)) !== null) {
    // Add text before this code
    if (match.index > lastIndex) {
      const textContent = text.slice(lastIndex, match.index)
      parts.push(
        <span key={`${lastIndex}-text`} className={currentColor}>
          {textContent}
        </span>
      )
    }

    // Parse the color code
    const codes = match[1].split(";")
    if (codes.includes("0")) {
      currentColor = "" // Reset
    } else {
      const colorCode = codes.find((c) => colorMap[c])
      if (colorCode) {
        currentColor = colorMap[colorCode]
      }
    }

    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(
      <span key={`${lastIndex}-text`} className={currentColor}>
        {text.slice(lastIndex)}
      </span>
    )
  }

  return parts.length > 0 ? parts : [text]
}

export function Terminal({
  lines = [],
  prompt = "$",
  autoScroll = true,
  maxLines = 1000,
  className,
  ...props
}: TerminalProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)
  const displayLines = React.useMemo(
    () => (maxLines > 0 ? lines.slice(-maxLines) : lines),
    [lines, maxLines]
  )

  React.useEffect(() => {
    if (autoScroll && scrollRef.current) {
      const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }, [displayLines, autoScroll])

  return (
    <div
      className={cn(
        "rounded-lg border bg-black font-mono text-sm text-gray-100",
        className
      )}
      {...props}
    >
      <div className="flex items-center gap-2 border-b border-gray-800 bg-gray-900 px-4 py-2">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-red-500" />
          <div className="h-3 w-3 rounded-full bg-yellow-500" />
          <div className="h-3 w-3 rounded-full bg-green-500" />
        </div>
        <span className="text-xs text-gray-400">Terminal</span>
      </div>

      <ScrollArea ref={scrollRef} className="h-[400px]">
        <div className="p-4 space-y-1">
          {displayLines.length === 0 ? (
            <div className="flex items-center gap-2 text-gray-500">
              <span className="text-green-400">{prompt}</span>
              <span className="animate-pulse">_</span>
            </div>
          ) : (
            displayLines.map((line, index) => (
              <div key={index} className="flex items-start gap-2">
                {line.startsWith(prompt) ? (
                  <>
                    <span className="text-green-400 shrink-0">{prompt}</span>
                    <span className="flex-1 break-all">
                      {parseAnsiColors(line.slice(prompt.length).trim())}
                    </span>
                  </>
                ) : (
                  <span className="flex-1 break-all">{parseAnsiColors(line)}</span>
                )}
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
