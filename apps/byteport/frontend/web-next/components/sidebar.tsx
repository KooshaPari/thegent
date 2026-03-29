"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Rocket,
  Server,
  Settings,
  DollarSign,
  Activity,
  FileCode,
  LogOut,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  collapsed?: boolean
  onCollapse?: (collapsed: boolean) => void
}

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string | number
}

const mainNav: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Deployments",
    href: "/deployments",
    icon: Rocket,
  },
  {
    title: "Services",
    href: "/services",
    icon: Server,
  },
  {
    title: "Monitoring",
    href: "/monitoring",
    icon: Activity,
  },
  {
    title: "Projects",
    href: "/projects",
    icon: FileCode,
  },
  {
    title: "Costs",
    href: "/costs",
    icon: DollarSign,
  },
]

const secondaryNav: NavItem[] = [
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar({
  className,
  collapsed = false,
  ...props
}: SidebarProps) {
  const pathname = usePathname()

  return (
    <div
      className={cn(
        "flex h-full flex-col border-r bg-background transition-all duration-300",
        collapsed ? "w-16" : "w-64",
        className
      )}
      {...props}
    >
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-4">
        {collapsed ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <span className="text-lg font-bold">B</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <span className="text-lg font-bold">B</span>
            </div>
            <span className="text-xl font-bold">BytePort</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <TooltipProvider delayDuration={0}>
          <nav className="space-y-1">
            {mainNav.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/")

              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link href={item.href}>
                      <Button
                        variant={isActive ? "secondary" : "ghost"}
                        className={cn(
                          "w-full justify-start gap-3",
                          collapsed && "justify-center px-2",
                          isActive && "bg-secondary font-medium"
                        )}
                        aria-label={item.title}
                        aria-current={isActive ? "page" : undefined}
                      >
                        <Icon className={cn("h-5 w-5", collapsed ? "mr-0" : "mr-0")} />
                        {!collapsed && (
                          <>
                            <span className="flex-1 text-left">{item.title}</span>
                            {item.badge && (
                              <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary px-1.5 text-xs text-primary-foreground">
                                {item.badge}
                              </span>
                            )}
                          </>
                        )}
                      </Button>
                    </Link>
                  </TooltipTrigger>
                  {collapsed && <TooltipContent side="right">{item.title}</TooltipContent>}
                </Tooltip>
              )
            })}
          </nav>

          <Separator className="my-4" />

          <nav className="space-y-1">
            {secondaryNav.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/")

              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link href={item.href}>
                      <Button
                        variant={isActive ? "secondary" : "ghost"}
                        className={cn(
                          "w-full justify-start gap-3",
                          collapsed && "justify-center px-2",
                          isActive && "bg-secondary font-medium"
                        )}
                        aria-label={item.title}
                        aria-current={isActive ? "page" : undefined}
                      >
                        <Icon className="h-5 w-5" />
                        {!collapsed && <span className="flex-1 text-left">{item.title}</span>}
                      </Button>
                    </Link>
                  </TooltipTrigger>
                  {collapsed && <TooltipContent side="right">{item.title}</TooltipContent>}
                </Tooltip>
              )
            })}
          </nav>
        </TooltipProvider>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-3">
        <TooltipProvider delayDuration={0}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start gap-3 text-muted-foreground hover:text-foreground",
                  collapsed && "justify-center px-2"
                )}
                aria-label="Logout"
              >
                <LogOut className="h-5 w-5" />
                {!collapsed && <span className="flex-1 text-left">Logout</span>}
              </Button>
            </TooltipTrigger>
            {collapsed && <TooltipContent side="right">Logout</TooltipContent>}
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  )
}
