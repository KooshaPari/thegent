"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import {
  Rocket,
  Server,
  Settings,
  FileCode,
  Activity,
  DollarSign,
  Play,
  Pause,
  Trash2,
  RotateCw,
  Terminal,
  LayoutDashboard,
} from "lucide-react"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"

export interface CommandPaletteProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface CommandAction {
  id: string
  label: string
  icon?: React.ComponentType<{ className?: string }>
  keywords?: string[]
  onSelect: () => void
  shortcut?: string
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter()

  // Navigation commands
  const navigationCommands: CommandAction[] = [
    {
      id: "nav-dashboard",
      label: "Go to Dashboard",
      icon: LayoutDashboard,
      keywords: ["home"],
      onSelect: () => {
        router.push("/dashboard")
        onOpenChange(false)
      },
    },
    {
      id: "nav-deployments",
      label: "Go to Deployments",
      icon: Rocket,
      keywords: ["deploy"],
      onSelect: () => {
        router.push("/deployments")
        onOpenChange(false)
      },
    },
    {
      id: "nav-services",
      label: "Go to Services",
      icon: Server,
      keywords: ["service"],
      onSelect: () => {
        router.push("/services")
        onOpenChange(false)
      },
    },
    {
      id: "nav-monitoring",
      label: "Go to Monitoring",
      icon: Activity,
      keywords: ["metrics", "logs"],
      onSelect: () => {
        router.push("/monitoring")
        onOpenChange(false)
      },
    },
    {
      id: "nav-projects",
      label: "Go to Projects",
      icon: FileCode,
      keywords: ["project"],
      onSelect: () => {
        router.push("/projects")
        onOpenChange(false)
      },
    },
    {
      id: "nav-costs",
      label: "Go to Costs",
      icon: DollarSign,
      keywords: ["billing", "pricing"],
      onSelect: () => {
        router.push("/costs")
        onOpenChange(false)
      },
    },
    {
      id: "nav-settings",
      label: "Go to Settings",
      icon: Settings,
      keywords: ["preferences", "config"],
      onSelect: () => {
        router.push("/settings")
        onOpenChange(false)
      },
    },
  ]

  // Action commands
  const actionCommands: CommandAction[] = [
    {
      id: "new-deployment",
      label: "New Deployment",
      icon: Rocket,
      keywords: ["create", "deploy"],
      onSelect: () => {
        router.push("/deployments/new")
        onOpenChange(false)
      },
      shortcut: "⌘N",
    },
    {
      id: "view-logs",
      label: "View Logs",
      icon: Terminal,
      keywords: ["console", "output"],
      onSelect: () => {
        router.push("/monitoring/logs")
        onOpenChange(false)
      },
      shortcut: "⌘L",
    },
  ]

  // Deployment actions (would be populated dynamically based on active deployments)
  const deploymentCommands: CommandAction[] = [
    {
      id: "restart-deployment",
      label: "Restart Deployment",
      icon: RotateCw,
      keywords: ["reboot", "reload"],
      onSelect: () => {
        // Handle restart
        onOpenChange(false)
      },
    },
    {
      id: "stop-deployment",
      label: "Stop Deployment",
      icon: Pause,
      keywords: ["halt", "pause"],
      onSelect: () => {
        // Handle stop
        onOpenChange(false)
      },
    },
    {
      id: "start-deployment",
      label: "Start Deployment",
      icon: Play,
      keywords: ["run", "resume"],
      onSelect: () => {
        // Handle start
        onOpenChange(false)
      },
    },
    {
      id: "delete-deployment",
      label: "Delete Deployment",
      icon: Trash2,
      keywords: ["remove"],
      onSelect: () => {
        // Handle delete
        onOpenChange(false)
      },
    },
  ]

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        onOpenChange(!open)
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [open, onOpenChange])

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Navigation">
          {navigationCommands.map((command) => {
            const Icon = command.icon
            return (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(" ")}`}
                onSelect={command.onSelect}
              >
                {Icon && <Icon className="mr-2 h-4 w-4" />}
                <span>{command.label}</span>
              </CommandItem>
            )
          })}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Actions">
          {actionCommands.map((command) => {
            const Icon = command.icon
            return (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(" ")}`}
                onSelect={command.onSelect}
              >
                {Icon && <Icon className="mr-2 h-4 w-4" />}
                <span>{command.label}</span>
                {command.shortcut && (
                  <span className="ml-auto text-xs text-muted-foreground">
                    {command.shortcut}
                  </span>
                )}
              </CommandItem>
            )
          })}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Deployment Actions">
          {deploymentCommands.map((command) => {
            const Icon = command.icon
            return (
              <CommandItem
                key={command.id}
                value={`${command.label} ${command.keywords?.join(" ")}`}
                onSelect={command.onSelect}
              >
                {Icon && <Icon className="mr-2 h-4 w-4" />}
                <span>{command.label}</span>
              </CommandItem>
            )
          })}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}

export function useCommandPalette() {
  const [open, setOpen] = React.useState(false)

  return {
    open,
    setOpen,
    toggle: () => setOpen((prev) => !prev),
  }
}
