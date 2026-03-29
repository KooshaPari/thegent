"use client"

import * as React from "react"
import { Search, Download, X, Filter, Copy, CheckCheck, Play, Pause } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"
import { LogEntry, LogLevel } from "@/lib/types"
import { formatDateTime } from "@/lib/utils"
import toast from "react-hot-toast"

export interface LogViewerProps extends React.HTMLAttributes<HTMLDivElement> {
  logs: LogEntry[]
  onLoadMore?: () => void
  hasMore?: boolean
  isLoading?: boolean
  autoScroll?: boolean
  showLineNumbers?: boolean
  terminalMode?: boolean
  onAutoScrollChange?: (enabled: boolean) => void
}

const logLevelColors: Record<LogLevel, string> = {
  debug: "text-gray-400",
  info: "text-blue-400",
  warn: "text-yellow-400",
  error: "text-red-400",
  fatal: "text-red-600",
}

const logLevelBadgeColors: Record<LogLevel, string> = {
  debug: "bg-gray-500 text-white",
  info: "bg-blue-500 text-white",
  warn: "bg-yellow-500 text-black",
  error: "bg-red-500 text-white",
  fatal: "bg-red-900 text-white",
}

export function LogViewer({
  logs,
  onLoadMore,
  hasMore = false,
  isLoading = false,
  autoScroll: autoScrollProp = true,
  showLineNumbers = true,
  terminalMode = true,
  onAutoScrollChange,
  className,
  ...props
}: LogViewerProps) {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [levelFilter, setLevelFilter] = React.useState<LogLevel | "all">("all")
  const [sourceFilter, setSourceFilter] = React.useState<"all" | "build" | "runtime" | "system">(
    "all"
  )
  const [autoScroll, setAutoScroll] = React.useState(autoScrollProp)
  const [copied, setCopied] = React.useState(false)
  const scrollRef = React.useRef<HTMLDivElement>(null)

  const filteredLogs = React.useMemo(() => {
    return logs.filter((log) => {
      const matchesSearch =
        searchQuery === "" ||
        log.message.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesLevel = levelFilter === "all" || log.level === levelFilter
      const matchesSource =
        sourceFilter === "all" || log.source === sourceFilter
      return matchesSearch && matchesLevel && matchesSource
    })
  }, [logs, searchQuery, levelFilter, sourceFilter])

  React.useEffect(() => {
    if (autoScroll && scrollRef.current) {
      const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }, [filteredLogs, autoScroll])

  const handleDownload = () => {
    const logText = filteredLogs
      .map(
        (log) =>
          `[${formatDateTime(log.timestamp)}] [${log.level.toUpperCase()}] ${
            log.source ? `[${log.source}] ` : ""
          }${log.message}`
      )
      .join("\n")

    const blob = new Blob([logText], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `logs-${new Date().toISOString()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success("Logs downloaded")
  }

  const handleCopyLogs = async () => {
    const logText = filteredLogs
      .map(
        (log) =>
          `[${formatDateTime(log.timestamp)}] [${log.level.toUpperCase()}] ${
            log.source ? `[${log.source}] ` : ""
          }${log.message}`
      )
      .join("\n")

    try {
      await navigator.clipboard.writeText(logText)
      setCopied(true)
      toast.success("Logs copied to clipboard")
      setTimeout(() => setCopied(false), 2000)
    } catch (_err) {
      toast.error("Failed to copy logs")
    }
  }

  const handleClearFilters = () => {
    setSearchQuery("")
    setLevelFilter("all")
    setSourceFilter("all")
  }

  const toggleAutoScroll = () => {
    const newValue = !autoScroll
    setAutoScroll(newValue)
    onAutoScrollChange?.(newValue)
  }

  const hasActiveFilters = searchQuery !== "" || levelFilter !== "all" || sourceFilter !== "all"

  const isJsonLog = (message: string) => {
    try {
      JSON.parse(message)
      return true
    } catch {
      return false
    }
  }

  const formatJsonLog = (message: string) => {
    try {
      const parsed = JSON.parse(message)
      return JSON.stringify(parsed, null, 2)
    } catch {
      return message
    }
  }

  return (
    <div className={cn("flex flex-col space-y-4", className)} {...props}>
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>

        <Select value={levelFilter} onValueChange={(value) => setLevelFilter(value as LogLevel | "all")}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Levels</SelectItem>
            <SelectItem value="debug">Debug</SelectItem>
            <SelectItem value="info">Info</SelectItem>
            <SelectItem value="warn">Warning</SelectItem>
            <SelectItem value="error">Error</SelectItem>
            <SelectItem value="fatal">Fatal</SelectItem>
          </SelectContent>
        </Select>

        <Select value={sourceFilter} onValueChange={(value) => setSourceFilter(value as typeof sourceFilter)}>
          <SelectTrigger className="w-[130px]">
            <SelectValue placeholder="Source" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sources</SelectItem>
            <SelectItem value="build">Build</SelectItem>
            <SelectItem value="runtime">Runtime</SelectItem>
            <SelectItem value="system">System</SelectItem>
          </SelectContent>
        </Select>

        <Button
          variant={autoScroll ? "default" : "outline"}
          size="icon"
          onClick={toggleAutoScroll}
          title={autoScroll ? "Disable auto-scroll" : "Enable auto-scroll"}
        >
          {autoScroll ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
        </Button>

        <Button variant="outline" size="icon" onClick={handleCopyLogs} title="Copy logs">
          {copied ? <CheckCheck className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
        </Button>

        <Button variant="outline" size="icon" onClick={handleDownload} title="Download logs">
          <Download className="h-4 w-4" />
        </Button>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearFilters}
            className="gap-1"
          >
            <X className="h-3 w-3" />
            Clear Filters
          </Button>
        )}
      </div>

      {/* Log entries */}
      <div
        className={cn(
          "rounded-lg border overflow-hidden",
          terminalMode && "bg-black border-gray-800"
        )}
      >
        <ScrollArea ref={scrollRef} className="h-[500px]">
          <div className={terminalMode ? "p-4" : "divide-y"}>
            {filteredLogs.length === 0 ? (
              <div className="flex items-center justify-center p-8 text-sm text-muted-foreground">
                {logs.length === 0 ? "No logs available" : "No logs match your filters"}
              </div>
            ) : (
              filteredLogs.map((log, index) => {
                const lineNumber = index + 1
                const isJson = isJsonLog(log.message)

                return (
                  <div
                    key={log.id || index}
                    className={cn(
                      "flex gap-3 font-mono text-xs",
                      terminalMode
                        ? "py-1 hover:bg-gray-900/50"
                        : "p-3 hover:bg-muted/50"
                    )}
                  >
                    {showLineNumbers && (
                      <span
                        className={cn(
                          "shrink-0 select-none w-12 text-right",
                          terminalMode ? "text-gray-600" : "text-muted-foreground"
                        )}
                      >
                        {lineNumber}
                      </span>
                    )}

                    <span
                      className={cn(
                        "shrink-0",
                        terminalMode ? "text-gray-500" : "text-muted-foreground"
                      )}
                    >
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>

                    {terminalMode ? (
                      <span
                        className={cn(
                          "shrink-0 font-bold",
                          logLevelColors[log.level]
                        )}
                      >
                        [{log.level.toUpperCase()}]
                      </span>
                    ) : (
                      <Badge
                        variant="secondary"
                        className={cn(
                          "shrink-0 text-xs font-medium",
                          logLevelBadgeColors[log.level]
                        )}
                      >
                        {log.level.toUpperCase()}
                      </Badge>
                    )}

                    {log.source && (
                      terminalMode ? (
                        <span className="text-purple-400 shrink-0">
                          [{log.source}]
                        </span>
                      ) : (
                        <Badge variant="outline" className="shrink-0 text-xs">
                          {log.source}
                        </Badge>
                      )
                    )}

                    <span
                      className={cn(
                        "flex-1 break-all",
                        terminalMode && "text-gray-300"
                      )}
                    >
                      {isJson ? (
                        <pre className="whitespace-pre-wrap">
                          {formatJsonLog(log.message)}
                        </pre>
                      ) : (
                        log.message
                      )}
                    </span>
                  </div>
                )
              })
            )}

            {hasMore && (
              <div className={cn("p-3 text-center", terminalMode && "bg-black")}>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onLoadMore}
                  disabled={isLoading}
                >
                  {isLoading ? "Loading..." : "Load More"}
                </Button>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Summary */}
      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        <span>
          Showing {filteredLogs.length} of {logs.length} logs
        </span>
        {hasActiveFilters && (
          <span className="flex items-center gap-1">
            <Filter className="h-3 w-3" />
            Filters active
          </span>
        )}
      </div>
    </div>
  )
}
