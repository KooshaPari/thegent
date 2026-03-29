"use client"

import * as React from "react"
import { Check } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { ProviderName, AppType } from "@/lib/types"
import { ProviderBadge } from "@/components/provider-badge"

export interface ProviderSelectorProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "onChange"> {
  value?: ProviderName
  onChange?: (provider: ProviderName) => void
  appType?: AppType
  showCapabilities?: boolean
}

interface ProviderOption {
  name: ProviderName
  displayName: string
  description: string
  capabilities: string[]
  recommended?: boolean
  pricing: "free" | "paid" | "freemium"
  supportedTypes: AppType[]
}

const providers: ProviderOption[] = [
  {
    name: "vercel",
    displayName: "Vercel",
    description: "Optimal for Next.js, React, and frontend frameworks",
    capabilities: ["Edge Functions", "Serverless", "CDN", "Analytics"],
    recommended: true,
    pricing: "freemium",
    supportedTypes: ["frontend", "static", "backend"],
  },
  {
    name: "netlify",
    displayName: "Netlify",
    description: "Great for static sites and JAMstack applications",
    capabilities: ["CDN", "Forms", "Functions", "Split Testing"],
    pricing: "freemium",
    supportedTypes: ["frontend", "static"],
  },
  {
    name: "render",
    displayName: "Render",
    description: "Full-stack deployments with databases and services",
    capabilities: ["Databases", "Web Services", "Cron Jobs", "Background Workers"],
    pricing: "freemium",
    supportedTypes: ["frontend", "backend", "database", "container"],
  },
  {
    name: "railway",
    displayName: "Railway",
    description: "Simple infrastructure for modern applications",
    capabilities: ["Databases", "Services", "Cron Jobs", "Volumes"],
    pricing: "paid",
    supportedTypes: ["frontend", "backend", "database", "container"],
  },
  {
    name: "fly",
    displayName: "Fly.io",
    description: "Deploy apps close to your users worldwide",
    capabilities: ["Global Distribution", "Postgres", "Redis", "Volumes"],
    pricing: "freemium",
    supportedTypes: ["backend", "database", "container"],
  },
  {
    name: "aws",
    displayName: "AWS",
    description: "Enterprise-grade cloud infrastructure",
    capabilities: ["EC2", "S3", "RDS", "Lambda", "CloudFront"],
    pricing: "paid",
    supportedTypes: ["frontend", "backend", "database", "static", "container"],
  },
]

export function ProviderSelector({
  value,
  onChange,
  appType,
  showCapabilities = true,
  className,
  ...props
}: ProviderSelectorProps) {
  const filteredProviders = React.useMemo(() => {
    if (!appType) return providers
    return providers.filter((p) => p.supportedTypes.includes(appType))
  }, [appType])

  return (
    <div className={cn("space-y-4", className)} {...props}>
      <div className="grid gap-4 sm:grid-cols-2">
        {filteredProviders.map((provider) => {
          const isSelected = value === provider.name
          return (
            <Card
              key={provider.name}
              className={cn(
                "cursor-pointer transition-all hover:border-primary",
                isSelected && "border-primary bg-primary/5"
              )}
              onClick={() => onChange?.(provider.name)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <ProviderBadge provider={provider.name} />
                    {provider.recommended && (
                      <Badge variant="secondary" className="text-xs">
                        Recommended
                      </Badge>
                    )}
                  </div>
                  {isSelected && (
                    <div className="flex h-5 w-5 items-center justify-center rounded-full bg-primary">
                      <Check className="h-3 w-3 text-primary-foreground" />
                    </div>
                  )}
                </div>
                <CardDescription className="mt-2">{provider.description}</CardDescription>
              </CardHeader>

              {showCapabilities && (
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">Key Features</p>
                    <div className="flex flex-wrap gap-1">
                      {provider.capabilities.slice(0, 4).map((capability) => (
                        <Badge
                          key={capability}
                          variant="outline"
                          className="text-xs font-normal"
                        >
                          {capability}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>
          )
        })}
      </div>

      {filteredProviders.length === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center">
          <p className="text-sm text-muted-foreground">
            No providers available for the selected app type
          </p>
        </div>
      )}
    </div>
  )
}
